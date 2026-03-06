import numpy as np
import pandas as pd


def split_periods(df: pd.DataFrame, train_frac: float = 0.6, val_frac: float = 0.2) -> dict[str, pd.DataFrame]:
    n = len(df)
    i = int(n * train_frac)
    j = int(n * (train_frac + val_frac))
    return {"train": df.iloc[:i], "validation": df.iloc[i:j], "test": df.iloc[j:]}


def walk_forward_windows(df: pd.DataFrame, train: int = 200, test: int = 50) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    windows = []
    for start in range(0, len(df) - train - test + 1, test):
        windows.append((df.iloc[start : start + train], df.iloc[start + train : start + train + test]))
    return windows


def monte_carlo_trade_sequence(returns: pd.Series, samples: int = 200) -> dict[str, float]:
    rng = np.random.default_rng(42)
    terminal_values = []
    arr = returns.values
    for _ in range(samples):
        shuffled = rng.choice(arr, size=len(arr), replace=True)
        terminal_values.append(float((1 + shuffled).prod()))
    return {
        "mc_terminal_p05": float(np.percentile(terminal_values, 5)),
        "mc_terminal_p50": float(np.percentile(terminal_values, 50)),
        "mc_terminal_p95": float(np.percentile(terminal_values, 95)),
    }
