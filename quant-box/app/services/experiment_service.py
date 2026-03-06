from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models import DataAsset, ExperimentResult, ExperimentRun, StrategySpec
from app.services.research_service import ResearchService
from backtests.engines.simple_engine import BacktestConfig
from backtests.reports.report_builder import build_backtest_report
from backtests.validation.sensitivity import parameter_stability
from research.experiments.sweep import ParameterSweepEngine


class ExperimentService:
    """Runs parameter sweeps and persists experiment metadata/results."""

    def __init__(self):
        self.sweep_engine = ParameterSweepEngine()
        self.research_service = ResearchService()

    def register_dataset(self, db: Session, source: str, symbol: str, timeframe: str, parquet_path: str) -> DataAsset:
        path = Path(parquet_path)
        existing = db.query(DataAsset).filter(DataAsset.parquet_path == str(path)).first()
        if existing:
            return existing

        df = pd.read_parquet(path)
        asset = DataAsset(
            source=source,
            symbol=symbol,
            timeframe=timeframe,
            parquet_path=str(path),
            start_ts=str(df["timestamp"].min()),
            end_ts=str(df["timestamp"].max()),
            row_count=int(len(df)),
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    def run_experiment(self, db: Session, strategy_id: str, data_path: str, top_k: int = 5) -> dict:
        spec_row = db.query(StrategySpec).filter(StrategySpec.strategy_id == strategy_id).first()
        if not spec_row:
            raise ValueError(f"Unknown strategy_id={strategy_id}")

        spec = spec_row.spec
        variants = self.sweep_engine.sweep(spec)
        df = pd.read_parquet(data_path)
        cfg = BacktestConfig()

        scored: list[dict] = []
        for variant in variants:
            params = variant["params"]
            validation = self.research_service.run_validation_pipeline(df, family=spec["family"], config=cfg, params=params)
            oos_metrics = validation["oos"]["metrics"]
            score = float(validation["promotion_score"])
            report = build_backtest_report(
                strategy_id=strategy_id,
                parameters=params,
                in_sample=validation["train"],
                out_of_sample=validation["oos"],
                walk_forward_sharpes=validation["walk_forward_sharpes"],
                monte_carlo=validation["monte_carlo"],
                sensitivity={},
                promotion_score=score,
                promotion_detail=validation["promotion_detail"],
            )
            scored.append(
                {
                    "strategy_id": strategy_id,
                    "params": params,
                    "metrics": oos_metrics,
                    "validation": {
                        "stability_score": validation["stability_score"],
                        "walk_forward_sharpes": validation["walk_forward_sharpes"],
                        "oos_degradation": validation["oos_degradation"],
                    },
                    "report": report,
                    "score": score,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        sensitivity = parameter_stability(scored, metric="sharpe")

        run = ExperimentRun(
            strategy_id=strategy_id,
            family=spec["family"],
            dataset_path=data_path,
            parameter_grid_size=len(variants),
            status="completed",
            summary={
                "best_promotion_score": scored[0]["score"] if scored else 0.0,
                "best_params": scored[0]["params"] if scored else {},
                "sensitivity": sensitivity,
            },
        )
        db.add(run)
        db.flush()

        for idx, row in enumerate(scored, start=1):
            db.add(
                ExperimentResult(
                    experiment_run_id=run.id,
                    strategy_id=strategy_id,
                    parameters=row["params"],
                    metrics={
                        **row["metrics"],
                        "promotion_score": row["score"],
                        "stability_score": row["validation"]["stability_score"],
                        "oos_degradation": row["validation"]["oos_degradation"],
                        "sensitivity_score": sensitivity["stability_score"],
                    },
                    rank=idx,
                )
            )

        db.commit()
        db.refresh(run)
        return {
            "run_id": run.id,
            "strategy_id": strategy_id,
            "grid_size": len(variants),
            "sensitivity": sensitivity,
            "top_results": scored[:top_k],
        }
