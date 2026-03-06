import pandas as pd

from backtests.engines.simple_engine import BacktestConfig, SimpleBacktestEngine
from backtests.validation.validator import monte_carlo_trade_sequence, split_periods, walk_forward_windows
from research.features.feature_engineering import add_basic_features
from research.ranking.promotion import promotion_score


class ResearchService:
    def __init__(self):
        self.engine = SimpleBacktestEngine()

    def signal_from_spec(self, df: pd.DataFrame, family: str, params: dict[str, float | int] | None = None) -> pd.Series:
        params = params or {}
        feat = add_basic_features(df)

        if family == "trend_following":
            fast = int(params.get("ma_fast", 10))
            slow = int(params.get("ma_slow", 30))
            ma_fast = feat["close"].rolling(fast).mean().bfill()
            ma_slow = feat["close"].rolling(slow).mean().bfill()
            return (ma_fast > ma_slow).astype(float)

        if family == "mean_reversion":
            z_threshold = float(params.get("z_entry", -1.8))
            z = (feat["close"] - feat["ma_slow"]) / (feat["vol_20"] + 1e-9)
            return (z < z_threshold).astype(float)

        if family == "breakout":
            lookback = int(params.get("donchian", params.get("range", 20)))
            rolling_high = feat["high"].rolling(lookback).max().bfill()
            return (feat["close"] > rolling_high.shift(1).bfill()).astype(float)

        if family == "pairs":
            z_threshold = float(params.get("z_entry", -1.0))
            z = (feat["close"] - feat["ma_slow"]) / (feat["vol_20"] + 1e-9)
            return (z < z_threshold).astype(float)

        return pd.Series(0.0, index=df.index)

    def run_backtest(self, df: pd.DataFrame, family: str, config: BacktestConfig, params: dict[str, float | int] | None = None) -> dict:
        signal = self.signal_from_spec(df, family=family, params=params)
        return self.engine.run(df, signal, config)

    def run_validation_pipeline(
        self,
        df: pd.DataFrame,
        family: str,
        config: BacktestConfig,
        params: dict[str, float | int] | None = None,
    ) -> dict:
        splits = split_periods(df)
        train_run = self.run_backtest(splits["train"], family, config, params)
        oos_run = self.run_backtest(splits["test"], family, config, params)

        wf = []
        for _, te in walk_forward_windows(df):
            wf.append(self.run_backtest(te, family, config, params)["metrics"]["sharpe"])

        wf_series = pd.Series(wf, dtype=float) if wf else pd.Series([0.0], dtype=float)
        stability = max(0.0, 1.0 - float(wf_series.std()))
        regime_diversity = float(min(1.0, wf_series.nunique() / max(len(wf_series), 1)))

        train_sharpe = train_run["metrics"].get("sharpe", 0.0)
        oos_sharpe = oos_run["metrics"].get("sharpe", 0.0)
        oos_degradation = float(oos_sharpe - train_sharpe)

        mc = monte_carlo_trade_sequence(oos_run["returns"])
        score, detail = promotion_score(oos_run["metrics"], stability_score=stability, regime_diversity=regime_diversity)

        detail.update(
            {
                "train_sharpe": float(train_sharpe),
                "oos_sharpe": float(oos_sharpe),
                "oos_degradation": oos_degradation,
                "regime_diversity": regime_diversity,
            }
        )

        return {
            "train": train_run,
            "oos": oos_run,
            "walk_forward_sharpes": wf,
            "stability_score": stability,
            "regime_diversity": regime_diversity,
            "oos_degradation": oos_degradation,
            "monte_carlo": mc,
            "promotion_score": score,
            "promotion_detail": detail,
        }
