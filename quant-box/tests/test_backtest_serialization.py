import math

import pandas as pd

from backtests.engines.simple_engine import BacktestConfig, SimpleBacktestEngine


def test_backtest_result_serialization_shape():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=50, freq="D", tz="UTC"),
            "close": [100 + i for i in range(50)],
        }
    )
    signal = pd.Series([1.0] * 50)
    out = SimpleBacktestEngine().run(df, signal, BacktestConfig())
    assert "metrics" in out
    assert len(out["equity_curve"]["x"]) == 50



def test_sortino_is_finite_without_losing_returns():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=30, freq="D", tz="UTC"),
            "close": [100 + i for i in range(30)],
        }
    )
    signal = pd.Series([1.0] * 30)
    out = SimpleBacktestEngine().run(df, signal, BacktestConfig(fee_bps=0.0, slippage_bps=0.0))
    assert math.isfinite(out["metrics"]["sortino"])
