from backtests.reports.report_builder import build_backtest_report


def test_report_builder_contains_core_sections():
    report = build_backtest_report(
        strategy_id="s1",
        parameters={"p": 1},
        in_sample={"metrics": {"sharpe": 1.0}},
        out_of_sample={"metrics": {"sharpe": 0.8}, "equity_curve": {"x": [], "y": []}, "drawdown_curve": {"x": [], "y": []}},
        walk_forward_sharpes=[0.7, 0.8],
        monte_carlo={"mc_terminal_p50": 1.1},
        sensitivity={"stability_score": 0.7},
        promotion_score=0.9,
        promotion_detail={"oos_sharpe": 0.8},
    )
    assert report["strategy_id"] == "s1"
    assert "out_of_sample_metrics" in report
    assert "monte_carlo" in report
