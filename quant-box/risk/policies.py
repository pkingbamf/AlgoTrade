from dataclasses import dataclass


@dataclass
class RiskLimits:
    max_position_pct: float = 0.10
    max_strategy_family_pct: float = 0.25
    max_daily_loss_pct: float = 0.02
    max_portfolio_drawdown_pct: float = 0.10
    vol_reduction_threshold: float = 0.35


class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.kill_switch = False
        self.strategy_disabled: set[str] = set()

    def check_order(self, order_notional: float, equity: float, strategy_id: str, rolling_vol: float) -> tuple[bool, str]:
        if self.kill_switch:
            return False, "global_kill_switch"
        if strategy_id in self.strategy_disabled:
            return False, "strategy_disabled"
        if order_notional / max(equity, 1e-9) > self.limits.max_position_pct:
            return False, "max_position_limit"
        if rolling_vol > self.limits.vol_reduction_threshold:
            return False, "volatility_reduction_trigger"
        return True, "ok"

    def daily_loss_breached(self, pnl_today: float, start_equity: float) -> bool:
        return abs(min(pnl_today, 0.0)) / max(start_equity, 1e-9) > self.limits.max_daily_loss_pct

    def drawdown_breached(self, drawdown: float) -> bool:
        return drawdown > self.limits.max_portfolio_drawdown_pct
