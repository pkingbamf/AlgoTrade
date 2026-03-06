from research.ranking.promotion import promotion_score


def test_promotion_score_positive_for_good_metrics():
    score, detail = promotion_score({"sharpe": 1.5, "profit_factor": 1.8, "max_drawdown": 0.1, "turnover": 0.2}, 0.8, 0.7)
    assert score > 0.5
    assert "drawdown_penalty" in detail
