from typing import Any, Literal

from pydantic import BaseModel, Field


class StrategySpecSchema(BaseModel):
    strategy_id: str = Field(min_length=3)
    family: Literal["trend_following", "mean_reversion", "breakout", "pairs"]
    asset_universe: list[str] = Field(min_length=1)
    timeframe: str
    indicators: dict[str, Any]
    entry_rules: list[str] = Field(min_length=1)
    exit_rules: list[str] = Field(min_length=1)
    risk_rules: dict[str, Any]
    parameter_ranges: dict[str, list[float | int]]
    notes: str | None = None


class ExperimentRequest(BaseModel):
    strategy_id: str
    data_path: str = "data/processed/sample_ohlcv.parquet"
    top_k: int = 5


class ExperimentSummaryResponse(BaseModel):
    run_id: int
    strategy_id: str
    grid_size: int
    top_results: list[dict[str, Any]]
