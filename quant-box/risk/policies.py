from dataclasses import dataclass


@dataclass
class RiskLimits:
    max_position_pct: float = 0.10
    max_strategy_family_pct: float = 0.25
    max_daily_loss_pct: float = 0.02
    max_portfolio_drawdown_pct: float = 0.10
    max_asset_exposure_pct: float = 0.30
    correlated_exposure_cap_pct: float = 0.50  # placeholder for future correlation model
    vol_reduction_threshold: float = 0.35


class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.kill_switch = False
        self.strategy_disabled: set[str] = set()

    def disable_strategy(self, strategy_id: str) -> None:
        self.strategy_disabled.add(strategy_id)

    def enable_strategy(self, strategy_id: str) -> None:
        self.strategy_disabled.discard(strategy_id)

    def set_kill_switch(self, active: bool) -> None:
        self.kill_switch = active

    def size_multiplier(self, rolling_vol: float) -> float:
        if rolling_vol <= self.limits.vol_reduction_threshold:
            return 1.0
        # reduce exposure proportionally once above threshold; floor 25%
        return max(0.25, self.limits.vol_reduction_threshold / max(rolling_vol, 1e-9))

    def check_order(
        self,
        order_notional: float,
        equity: float,
        strategy_id: str,
        rolling_vol: float,
        context: dict[str, float] | None = None,
    ) -> tuple[bool, str, float]:
        context = context or {}

        if self.kill_switch:
            return False, "global_kill_switch", 0.0
        if strategy_id in self.strategy_disabled:
            return False, "strategy_disabled", 0.0
        if self.daily_loss_breached(context.get("daily_loss_pct", 0.0)):
            self.set_kill_switch(True)
            return False, "max_daily_loss_breached", 0.0
        if self.drawdown_breached(context.get("drawdown_pct", 0.0)):
            self.set_kill_switch(True)
            return False, "max_drawdown_breached", 0.0
        if order_notional / max(equity, 1e-9) > self.limits.max_position_pct:
            return False, "max_position_limit", 0.0
        if context.get("strategy_family_allocation_pct", 0.0) > self.limits.max_strategy_family_pct:
            return False, "max_strategy_family_allocation", 0.0
        if context.get("asset_exposure_pct", 0.0) > self.limits.max_asset_exposure_pct:
            return False, "max_asset_exposure", 0.0

        multiplier = self.size_multiplier(rolling_vol)
        return True, "ok", multiplier

    def daily_loss_breached(self, daily_loss_pct: float) -> bool:
        return daily_loss_pct > self.limits.max_daily_loss_pct

    def drawdown_breached(self, drawdown: float) -> bool:
        return drawdown > self.limits.max_portfolio_drawdown_pct
