from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DataAsset(Base):
    __tablename__ = "data_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    parquet_path: Mapped[str] = mapped_column(String(256), unique=True)
    start_ts: Mapped[str] = mapped_column(String(64))
    end_ts: Mapped[str] = mapped_column(String(64))
    row_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    family: Mapped[str] = mapped_column(String(64), index=True)
    dataset_path: Mapped[str] = mapped_column(String(256))
    parameter_grid_size: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="completed")
    summary: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_run_id: Mapped[int] = mapped_column(Integer, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    parameters: Mapped[dict] = mapped_column(JSON)
    metrics: Mapped[dict] = mapped_column(JSON)
    rank: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StrategySpec(Base):
    __tablename__ = "strategy_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    family: Mapped[str] = mapped_column(String(64), index=True)
    timeframe: Mapped[str] = mapped_column(String(32))
    universe: Mapped[dict] = mapped_column(JSON)
    spec: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    parameters: Mapped[dict] = mapped_column(JSON)
    period: Mapped[str] = mapped_column(String(32), default="in_sample")
    metrics: Mapped[dict] = mapped_column(JSON)
    equity_curve: Mapped[dict] = mapped_column(JSON)
    drawdown_curve: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    summary: Mapped[dict] = mapped_column(JSON)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PromotionDecision(Base):
    __tablename__ = "promotion_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    score: Mapped[float] = mapped_column(Float)
    accepted: Mapped[bool] = mapped_column(Boolean)
    detail: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StrategyDeployment(Base):
    __tablename__ = "strategy_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    mode: Mapped[str] = mapped_column(String(24), default="paper")
    status: Mapped[str] = mapped_column(String(24), default="active")
    config: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="filled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String(128), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    quantity: Mapped[float] = mapped_column(Float)
    avg_price: Mapped[float] = mapped_column(Float)
    mark_price: Mapped[float] = mapped_column(Float)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    component: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
