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
