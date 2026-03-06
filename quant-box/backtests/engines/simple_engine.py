from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    fee_bps: float = 5.0
    slippage_bps: float = 3.0
    initial_capital: float = 100000.0


class SimpleBacktestEngine:
    """Vectorized MVP backtester for rule-based signal series."""

    def run(self, df: pd.DataFrame, signal: pd.Series, config: BacktestConfig) -> dict:
        ret = df["close"].pct_change().fillna(0.0)
        gross = signal.shift(1).fillna(0.0) * ret
        turnover = signal.diff().abs().fillna(0.0)
        costs = turnover * ((config.fee_bps + config.slippage_bps) / 10000)
        net = gross - costs
        equity = (1 + net).cumprod() * config.initial_capital
        dd = equity / equity.cummax() - 1
        trades = int((turnover > 0).sum())
        wins = int((net > 0).sum())
        losses = int((net < 0).sum())
        gross_pos = net[net > 0].sum()
        gross_neg = abs(net[net < 0].sum()) + 1e-9
        sharpe = np.sqrt(252) * net.mean() / (net.std() + 1e-9)
        downside = net[net < 0]
        downside_std = downside.std()
        if np.isnan(downside_std):
            downside_std = 0.0
        sortino = np.sqrt(252) * net.mean() / (downside_std + 1e-9)
        cagr = (equity.iloc[-1] / config.initial_capital) ** (252 / max(len(equity), 1)) - 1
        max_dd = abs(dd.min())
        metrics = {
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "sortino": float(sortino),
            "max_drawdown": float(max_dd),
            "calmar": float(cagr / (max_dd + 1e-9)),
            "profit_factor": float(gross_pos / gross_neg),
            "win_rate": float(wins / max(wins + losses, 1)),
            "turnover": float(turnover.mean()),
            "exposure": float(signal.abs().mean()),
            "expectancy": float(net.mean()),
            "trades": float(trades),
        }
        return {
            "metrics": metrics,
            "equity_curve": {"x": df["timestamp"].astype(str).tolist(), "y": equity.tolist()},
            "drawdown_curve": {"x": df["timestamp"].astype(str).tolist(), "y": dd.tolist()},
            "returns": net,
        }
