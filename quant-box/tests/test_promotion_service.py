from app.services.promotion_service import PromotionService


def test_promotion_service_rejects_insufficient_trades():
    accepted, reason = PromotionService().evaluate(
        metrics={"trades": 5, "sharpe": 1.2, "max_drawdown": 0.1, "profit_factor": 1.4, "turnover": 0.5},
        promotion_score=1.0,
        stability_score=0.8,
        walk_forward_sharpes=[0.5, 0.3],
    )
    assert not accepted
    assert reason == "insufficient_trades"


def test_promotion_service_accepts_strong_profile():
    accepted, reason = PromotionService().evaluate(
        metrics={"trades": 60, "sharpe": 1.3, "max_drawdown": 0.08, "profit_factor": 1.5, "turnover": 0.4},
        promotion_score=0.95,
        stability_score=0.75,
        walk_forward_sharpes=[0.6, 0.7, 0.8],
    )
    assert accepted
    assert reason == "accepted"
