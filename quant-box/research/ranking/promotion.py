def promotion_score(metrics: dict[str, float], stability_score: float, regime_diversity: float) -> tuple[float, dict[str, float]]:
    drawdown_penalty = metrics.get("max_drawdown", 0.0) * 1.5
    turnover_penalty = metrics.get("turnover", 0.0) * 0.25
    score = (
        0.35 * metrics.get("sharpe", 0.0)
        + 0.25 * metrics.get("profit_factor", 0.0)
        + 0.2 * stability_score
        + 0.1 * regime_diversity
        - 0.07 * drawdown_penalty
        - 0.03 * turnover_penalty
    )
    detail = {
        "oos_sharpe": metrics.get("sharpe", 0.0),
        "profit_factor": metrics.get("profit_factor", 0.0),
        "drawdown_penalty": drawdown_penalty,
        "stability_score": stability_score,
        "turnover_penalty": turnover_penalty,
        "regime_diversity": regime_diversity,
    }
    return float(score), detail
