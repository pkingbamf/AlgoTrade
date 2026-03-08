from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, BacktestRun, DataAsset, PaperPosition, PromotionDecision, StrategyDeployment, StrategySpec, ValidationResult
from app.schemas.common import HealthResponse
from app.schemas.strategy import BacktestRunRequest, DeployStrategyRequest, PaperOrderRequest, PromotionResponse, StrategySpecCreate
from app.services.paper_trading_service import PaperTradingService
from app.services.promotion_service import PromotionService
from app.services.research_service import ResearchService
from app.services.strategy_service import StrategyService
from backtests.engines.simple_engine import BacktestConfig
from execution.paper.broker import PaperBroker
from monitoring.health import heartbeat
from monitoring.observability import MonitoringService
from risk.policies import RiskEngine, RiskLimits

router = APIRouter()
strategy_service = StrategyService()
research_service = ResearchService()
promotion_service = PromotionService()
paper_broker = PaperBroker()
paper_service = PaperTradingService(paper_broker)
risk_engine = RiskEngine(RiskLimits())
monitoring_service = MonitoringService()

START_EQUITY = 100000.0
peak_equity = START_EQUITY


def _strategy_family_allocation_pct(db: Session, strategy_id: str, equity: float) -> float:
    spec = db.query(StrategySpec).filter(StrategySpec.strategy_id == strategy_id).first()
    if not spec:
        return 0.0
    family_ids = [r.strategy_id for r in db.query(StrategySpec).filter(StrategySpec.family == spec.family).all()]
    if not family_ids:
        return 0.0
    rows = db.query(PaperPosition).filter(PaperPosition.strategy_id.in_(family_ids)).all()
    notional = sum(abs(r.quantity * r.mark_price) for r in rows)
    return float(notional / max(equity, 1e-9))


def _asset_exposure_pct(symbol: str, equity: float) -> float:
    pos = paper_broker.positions.get(symbol)
    if not pos:
        return 0.0
    notional = abs(pos.quantity * pos.avg_price)
    return float(notional / max(equity, 1e-9))


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    latest_data = db.query(DataAsset).order_by(DataAsset.created_at.desc()).first()
    freshness = monitoring_service.data_freshness(latest_data.end_ts if latest_data else None, stale_after_seconds=7200)
    monitoring_service.alert_if(freshness["is_stale"], "stale_data", freshness)
    return HealthResponse(
        status="ok",
        db="ok",
        heartbeat=heartbeat(),
        details={
            "data_freshness": freshness,
            "jobs_running": sum(1 for j in monitoring_service.jobs.values() if j.status == "running"),
            "alerts_count": len(monitoring_service.alerts),
        },
    )


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    counters = {
        "strategies": db.query(StrategySpec).count(),
        "backtests": db.query(BacktestRun).count(),
        "promotions": db.query(PromotionDecision).count(),
        "deployments": db.query(StrategyDeployment).count(),
        "audit_logs": db.query(AuditLog).count(),
    }
    health_map = {"api": "ok", "db": "ok", "paper_broker": "ok"}
    return {
        "paper": paper_service.portfolio_monitor(),
        "system": monitoring_service.system_metrics(counters, health_map),
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
    monitoring_service.record_job_start("backtest_run")
    spec = db.query(StrategySpec).filter(StrategySpec.strategy_id == payload.strategy_id).first()
    if not spec:
        monitoring_service.record_job_end("backtest_run", "failed", {"reason": "strategy not found"})
        raise HTTPException(404, "strategy not found")

    path = Path("data/processed/sample_ohlcv.parquet")
    if not path.exists():
        monitoring_service.record_job_end("backtest_run", "failed", {"reason": "sample data missing"})
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
    monitoring_service.record_job_end("backtest_run", "completed", {"strategy_id": payload.strategy_id})
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


@router.post("/paper/deployments")
def deploy_paper_strategy(req: DeployStrategyRequest, db: Session = Depends(get_db)):
    dep = paper_service.deploy_strategy(db, strategy_id=req.strategy_id, config=req.config)
    return {"id": dep.id, "strategy_id": dep.strategy_id, "status": dep.status, "mode": dep.mode}


@router.get("/paper/deployments")
def list_deployments(db: Session = Depends(get_db)):
    rows = db.query(StrategyDeployment).order_by(StrategyDeployment.id.desc()).all()
    return [{"id": r.id, "strategy_id": r.strategy_id, "status": r.status, "mode": r.mode, "config": r.config} for r in rows]


@router.post("/paper/orders")
def place_paper_order(req: PaperOrderRequest, db: Session = Depends(get_db)):
    global peak_equity

    monitor = paper_service.portfolio_monitor()
    current_equity = START_EQUITY + monitor["unrealized_pnl"]
    peak_equity = max(peak_equity, current_equity)

    daily_loss_pct = abs(min(monitor["unrealized_pnl"], 0.0)) / max(START_EQUITY, 1e-9)
    drawdown_pct = max(0.0, (peak_equity - current_equity) / max(peak_equity, 1e-9))

    context = {
        "daily_loss_pct": daily_loss_pct,
        "drawdown_pct": drawdown_pct,
        "strategy_family_allocation_pct": _strategy_family_allocation_pct(db, req.strategy_id, START_EQUITY),
        "asset_exposure_pct": _asset_exposure_pct(req.symbol, START_EQUITY),
    }

    order_notional = req.quantity * req.price
    ok, reason, multiplier = risk_engine.check_order(
        order_notional=order_notional,
        equity=START_EQUITY,
        strategy_id=req.strategy_id,
        rolling_vol=0.2,
        context=context,
    )
    if not ok:
        raise HTTPException(400, f"risk rejected: {reason}")

    adjusted_qty = req.quantity * multiplier
    return paper_service.execute_order(db, req.strategy_id, req.symbol, req.side, adjusted_qty, req.price)


@router.get("/paper/orders")
def paper_orders():
    return paper_broker.orders


@router.get("/paper/positions")
def paper_positions():
    return {k: vars(v) for k, v in paper_broker.positions.items()}


@router.get("/paper/pnl")
def paper_pnl():
    return paper_broker.pnl_snapshot({})


@router.get("/paper/portfolio-monitor")
def paper_portfolio_monitor():
    return paper_service.portfolio_monitor()


@router.get("/paper/reconcile/{strategy_id}")
def paper_reconcile(strategy_id: str, db: Session = Depends(get_db)):
    return paper_service.reconcile_positions(db, strategy_id)


@router.post("/risk/kill-switch/{active}")
def set_kill_switch(active: bool):
    risk_engine.set_kill_switch(active)
    return {"kill_switch": risk_engine.kill_switch}


@router.post("/risk/disable/{strategy_id}")
def disable_strategy(strategy_id: str):
    risk_engine.disable_strategy(strategy_id)
    return {"disabled_strategies": list(risk_engine.strategy_disabled)}


@router.post("/risk/enable/{strategy_id}")
def enable_strategy(strategy_id: str):
    risk_engine.enable_strategy(strategy_id)
    return {"disabled_strategies": list(risk_engine.strategy_disabled)}


@router.get("/risk/state")
def risk_state():
    return {
        "kill_switch": risk_engine.kill_switch,
        "disabled_strategies": list(risk_engine.strategy_disabled),
        "limits": vars(risk_engine.limits),
    }


@router.get("/risk/limits")
def risk_limits():
    return vars(risk_engine.limits)


@router.get("/system/jobs")
def system_jobs():
    return {"jobs": monitoring_service.job_status()}


@router.get("/system/data-freshness")
def system_data_freshness(db: Session = Depends(get_db)):
    latest_data = db.query(DataAsset).order_by(DataAsset.created_at.desc()).first()
    freshness = monitoring_service.data_freshness(latest_data.end_ts if latest_data else None, stale_after_seconds=7200)
    monitoring_service.alert_if(freshness["is_stale"], "stale_data", freshness)
    return freshness


@router.get("/system/logs")
def system_logs(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(100).all()
    db_logs = [{"component": r.component, "event_type": r.event_type, "payload": r.payload, "created_at": r.created_at.isoformat()} for r in rows]
    alerts = [{"component": "monitoring", "event_type": a["name"], "payload": a["payload"], "created_at": a["created_at"]} for a in monitoring_service.alerts]
    return {"logs": db_logs + alerts}


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


@router.get("/dashboard/overview", response_class=HTMLResponse)
def dashboard_overview_page():
    return HTMLResponse(Path("frontend/templates/index.html").read_text())


@router.get("/dashboard/strategy-library", response_class=HTMLResponse)
def dashboard_strategy_library():
    return HTMLResponse(Path("frontend/templates/strategy_library.html").read_text())


@router.get("/dashboard/backtest-runs", response_class=HTMLResponse)
def dashboard_backtest_runs():
    return HTMLResponse(Path("frontend/templates/backtest_runs.html").read_text())


@router.get("/dashboard/rankings", response_class=HTMLResponse)
def dashboard_rankings():
    return HTMLResponse(Path("frontend/templates/rankings.html").read_text())


@router.get("/dashboard/paper-trading", response_class=HTMLResponse)
def dashboard_paper_trading():
    return HTMLResponse(Path("frontend/templates/paper_trading.html").read_text())


@router.get("/dashboard/risk-monitor", response_class=HTMLResponse)
def dashboard_risk_monitor():
    return HTMLResponse(Path("frontend/templates/risk_monitor.html").read_text())


@router.get("/dashboard/system-health", response_class=HTMLResponse)
def dashboard_system_health():
    return HTMLResponse(Path("frontend/templates/system_health.html").read_text())
