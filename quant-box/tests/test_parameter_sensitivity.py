from backtests.validation.sensitivity import parameter_stability


def test_parameter_stability_score_range():
    results = [
        {"metrics": {"sharpe": 1.0}},
        {"metrics": {"sharpe": 1.1}},
        {"metrics": {"sharpe": 0.9}},
    ]
    out = parameter_stability(results)
    assert 0.0 <= out["stability_score"] <= 1.0
    assert "metric_std" in out
