def build_backtest_report(
    strategy_id: str,
    parameters: dict,
    in_sample: dict,
    out_of_sample: dict,
    walk_forward_sharpes: list[float],
    monte_carlo: dict[str, float],
    sensitivity: dict[str, float],
    promotion_score: float,
    promotion_detail: dict[str, float],
) -> dict:
    """Build a complete backtest report payload for storage/API usage."""

    return {
        "strategy_id": strategy_id,
        "parameters": parameters,
        "in_sample_metrics": in_sample.get("metrics", {}),
        "out_of_sample_metrics": out_of_sample.get("metrics", {}),
        "equity_curve": out_of_sample.get("equity_curve", {}),
        "drawdown_curve": out_of_sample.get("drawdown_curve", {}),
        "walk_forward_sharpes": walk_forward_sharpes,
        "monte_carlo": monte_carlo,
        "sensitivity": sensitivity,
        "promotion_score": promotion_score,
        "promotion_detail": promotion_detail,
    }
