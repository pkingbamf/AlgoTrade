import pandas as pd


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret_1"] = out["close"].pct_change().fillna(0.0)
    out["ma_fast"] = out["close"].rolling(10).mean().bfill()
    out["ma_slow"] = out["close"].rolling(30).mean().bfill()
    out["vol_20"] = out["ret_1"].rolling(20).std().bfill()
    return out
