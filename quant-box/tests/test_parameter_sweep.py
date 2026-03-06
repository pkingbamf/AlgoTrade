from research.experiments.sweep import ParameterSweepEngine


def test_parameter_sweep_count():
    spec = {
        "strategy_id": "s1",
        "family": "trend_following",
        "asset_universe": ["BTCUSDT"],
        "timeframe": "1h",
        "indicators": {"ma_fast": 10, "ma_slow": 20},
        "entry_rules": ["ma_fast > ma_slow"],
        "exit_rules": ["ma_fast < ma_slow"],
        "risk_rules": {"stop_loss_pct": 0.02},
        "parameter_ranges": {"ma_fast": [10, 20], "ma_slow": [50, 100, 150]},
        "notes": "test",
    }
    variants = ParameterSweepEngine().sweep(spec)
    assert len(variants) == 6
