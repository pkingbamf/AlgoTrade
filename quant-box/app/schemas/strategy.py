from typing import Any, Literal

from pydantic import BaseModel, Field


class StrategySpecBase(BaseModel):
    strategy_id: str
    family: Literal["trend_following", "mean_reversion", "breakout", "pairs"]
    asset_universe: list[str]
    timeframe: str
    indicators: dict[str, Any]
    entry_rules: list[str]
    exit_rules: list[str]
    risk_rules: dict[str, Any]
    parameter_ranges: dict[str, list[float | int]]
    notes: str | None = None


class StrategySpecCreate(StrategySpecBase):
    pass


class StrategySpecResponse(StrategySpecBase):
    id: int

    class Config:
        from_attributes = True


class BacktestRunRequest(BaseModel):
    strategy_id: str
    initial_capital: float = 100000.0
    fee_bps: float = 5.0
    slippage_bps: float = 3.0


class BacktestRunResponse(BaseModel):
    run_id: int
    strategy_id: str
    metrics: dict[str, float]


class PromotionResponse(BaseModel):
    strategy_id: str
    accepted: bool
    score: float
    detail: dict[str, float]


class PaperOrderRequest(BaseModel):
    strategy_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
