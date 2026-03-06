from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import BacktestRun, PromotionDecision, StrategySpec, ValidationResult
from app.schemas.common import HealthResponse
from app.schemas.strategy import BacktestRunRequest, PaperOrderRequest, PromotionResponse, StrategySpecCreate
from app.services.promotion_service import PromotionService
from app.services.research_service import ResearchService
from app.services.strategy_service import StrategyService
from backtests.engines.simple_engine import BacktestConfig
from execution.paper.broker import PaperBroker
from monitoring.health import heartbeat
from risk.policies import RiskEngine, RiskLimits

router = APIRouter()
strategy_service = StrategyService()
research_service = ResearchService()
promotion_service = PromotionService()
paper_broker = PaperBroker()
risk_engine = RiskEngine(RiskLimits())


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", db="ok", heartbeat=heartbeat())


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return {
        "strategies": db.query(StrategySpec).count(),
        "backtests": db.query(BacktestRun).count(),
        "promotions": db.query(PromotionDecision).count(),
        "paper": paper_broker.pnl_snapshot({}),
    }


@router.post("/strategy-specs")
def create_strategy_spec(spec: StrategySpecCreate, db: Session = Depends(get_db)):
    model = strategy_service.persist_spec(db, spec.model_dump())
    return {"id": model.id, "strategy_id": model.strategy_id}


@router.get("/strategy-specs")
def list_strategy_specs(db: Session = Depends(get_db)):
    rows = db.query(StrategySpec).all()
    return [{"strategy_id": s.strategy_id, "family": s.family, "timeframe": s.timeframe} for s in rows]


@router.post("/backtests/run")
def run_backtest(payload: BacktestRunRequest, db: Session = Depends(get_db)):
    spec = db.query(StrategySpec).filter(StrategySpec.strategy_id == payload.strategy_id).first()
    if not spec:
        raise HTTPException(404, "strategy not found")

    path = Path("data/processed/sample_ohlcv.parquet")
    if not path.exists():
        raise HTTPException(400, "sample data not found; run scripts/generate_sample_data.py")

    df = pd.read_parquet(path)
    result = research_service.run_validation_pipeline(
        df,
        family=spec.family,
        config=BacktestConfig(initial_capital=payload.initial_capital, fee_bps=payload.fee_bps, slippage_bps=payload.slippage_bps),
    )

    oos_metrics = result["oos"]["metrics"]
    accepted, reason = promotion_service.evaluate(
        metrics=oos_metrics,
        promotion_score=result["promotion_score"],
        stability_score=result["stability_score"],
        walk_forward_sharpes=result["walk_forward_sharpes"],
    )

    run = BacktestRun(
        strategy_id=payload.strategy_id,
        parameters={"default": True},
        period="oos",
        metrics=oos_metrics,
        equity_curve=result["oos"]["equity_curve"],
        drawdown_curve=result["oos"]["drawdown_curve"],
    )
    db.add(run)

    validation = ValidationResult(
        strategy_id=payload.strategy_id,
        summary={
            "stability_score": result["stability_score"],
            "oos_degradation": result["oos_degradation"],
            "walk_forward_sharpes": result["walk_forward_sharpes"],
            "monte_carlo": result["monte_carlo"],
        },
        rejected=not accepted,
        rejection_reason=None if accepted else reason,
    )
    db.add(validation)

    decision = PromotionDecision(
        strategy_id=payload.strategy_id,
        score=result["promotion_score"],
        accepted=accepted,
        detail={**result["promotion_detail"], "decision_reason": reason},
    )
    db.add(decision)

    db.commit()
    db.refresh(run)
    return {"run_id": run.id, "strategy_id": run.strategy_id, "metrics": run.metrics}


@router.get("/backtests/{run_id}")
def get_backtest(run_id: int, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    if not run:
        raise HTTPException(404, "run not found")
    return {"id": run.id, "strategy_id": run.strategy_id, "metrics": run.metrics}


@router.get("/backtests/{run_id}/report")
def get_backtest_report(run_id: int, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    if not run:
        raise HTTPException(404, "run not found")
    return {"equity_curve": run.equity_curve, "drawdown_curve": run.drawdown_curve, "metrics": run.metrics}


@router.get("/rankings")
def rankings(db: Session = Depends(get_db)):
    rows = db.query(PromotionDecision).order_by(PromotionDecision.score.desc()).all()
    return [{"strategy_id": r.strategy_id, "score": r.score, "accepted": r.accepted} for r in rows]


@router.get("/promotions", response_model=list[PromotionResponse])
def promotions(db: Session = Depends(get_db)):
    rows = db.query(PromotionDecision).all()
    return [PromotionResponse(strategy_id=r.strategy_id, accepted=r.accepted, score=r.score, detail=r.detail) for r in rows]


@router.post("/paper/orders")
def place_paper_order(req: PaperOrderRequest):
    ok, reason = risk_engine.check_order(req.quantity * req.price, equity=100000, strategy_id=req.strategy_id, rolling_vol=0.2)
    if not ok:
        raise HTTPException(400, f"risk rejected: {reason}")
    return paper_broker.place_order(req.symbol, req.side, req.quantity, req.price)


@router.get("/paper/orders")
def paper_orders():
    return paper_broker.orders


@router.get("/paper/positions")
def paper_positions():
    return {k: vars(v) for k, v in paper_broker.positions.items()}


@router.get("/paper/pnl")
def paper_pnl():
    return paper_broker.pnl_snapshot({})


@router.get("/risk/state")
def risk_state():
    return {"kill_switch": risk_engine.kill_switch, "disabled_strategies": list(risk_engine.strategy_disabled)}


@router.get("/risk/limits")
def risk_limits():
    return vars(risk_engine.limits)


@router.get("/system/logs")
def system_logs():
    return {"logs": []}


@router.get("/strategies")
def strategies(db: Session = Depends(get_db)):
    rows = db.query(StrategySpec).all()
    return [{"strategy_id": r.strategy_id, "family": r.family, "timeframe": r.timeframe} for r in rows]


@router.get("/strategies/{strategy_id}")
def strategy_detail(strategy_id: str, db: Session = Depends(get_db)):
    row = db.query(StrategySpec).filter(StrategySpec.strategy_id == strategy_id).first()
    if not row:
        raise HTTPException(404, "strategy not found")
    return row.spec


@router.get("/", response_class=HTMLResponse)
def dashboard_overview():
    return HTMLResponse(Path("frontend/templates/index.html").read_text())
