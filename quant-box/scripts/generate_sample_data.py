from pathlib import Path

import numpy as np
import pandas as pd


if __name__ == "__main__":
    np.random.seed(7)
    periods = 800
    ts = pd.date_range("2022-01-01", periods=periods, freq="H", tz="UTC")
    base = 20000 + np.cumsum(np.random.normal(0, 80, size=periods))
    close = pd.Series(base).clip(lower=100)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = np.maximum(open_, close) + np.random.uniform(5, 40, size=periods)
    low = np.minimum(open_, close) - np.random.uniform(5, 40, size=periods)
    volume = np.random.uniform(100, 1000, size=periods)
    df = pd.DataFrame({"timestamp": ts, "open": open_, "high": high, "low": low, "close": close, "volume": volume})
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/raw/sample_ohlcv.csv", index=False)
    df.to_parquet("data/processed/sample_ohlcv.parquet", index=False)
    print("generated data at data/processed/sample_ohlcv.parquet")
