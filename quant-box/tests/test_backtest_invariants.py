from backtests.validation.sensitivity import parameter_stability


def test_backtest_sensitivity_invariant_with_constant_metric():
    rows = [{"metrics": {"sharpe": 1.0}} for _ in range(5)]
    out = parameter_stability(rows)
    assert out["metric_std"] == 0.0
    assert out["stability_score"] == 1.0
