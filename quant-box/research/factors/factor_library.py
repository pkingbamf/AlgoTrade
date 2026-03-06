import pandas as pd


def zscore(series: pd.Series, lookback: int = 20) -> pd.Series:
    mean = series.rolling(lookback).mean()
    std = series.rolling(lookback).std().replace(0, 1)
    return ((series - mean) / std).fillna(0.0)


def momentum(series: pd.Series, lookback: int = 20) -> pd.Series:
    return series.pct_change(lookback).fillna(0.0)
