from app.core.config import get_settings


class PromotionService:
    """Apply hard promotion gates and score acceptance decision."""

    def __init__(self):
        self.settings = get_settings()

    def evaluate(
        self,
        metrics: dict[str, float],
        promotion_score: float,
        stability_score: float,
        walk_forward_sharpes: list[float],
    ) -> tuple[bool, str]:
        trades = metrics.get("trades", 0.0)
        sharpe = metrics.get("sharpe", 0.0)
        max_dd = metrics.get("max_drawdown", 1.0)
        profit_factor = metrics.get("profit_factor", 0.0)
        turnover = metrics.get("turnover", 0.0)

        if trades < self.settings.promotion_min_trades:
            return False, "insufficient_trades"
        if sharpe < self.settings.promotion_min_oos_sharpe:
            return False, "oos_sharpe_below_threshold"
        if max_dd > self.settings.promotion_max_drawdown:
            return False, "max_drawdown_above_threshold"
        if profit_factor < 1.1:
            return False, "profit_factor_below_threshold"
        if turnover > 1.5:
            return False, "turnover_too_high"
        if stability_score < 0.2:
            return False, "stability_too_low"
        if walk_forward_sharpes and min(walk_forward_sharpes) < -1.0:
            return False, "walk_forward_fragility"
        if promotion_score < 0.8:
            return False, "promotion_score_below_threshold"
        return True, "accepted"
