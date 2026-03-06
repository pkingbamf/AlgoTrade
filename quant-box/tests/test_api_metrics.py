from fastapi.testclient import TestClient

from app.api.routes import risk_engine
from app.core.config import get_settings
from app.main import app


def test_metrics_endpoint_shape():
    client = TestClient(app)
    res = client.get("/metrics")
    assert res.status_code == 200
    payload = res.json()
    assert "strategies" in payload
    assert "paper" in payload



def test_risk_engine_uses_configured_limits():
    settings = get_settings()
    assert risk_engine.limits.max_position_pct == settings.risk_max_position_pct
    assert risk_engine.limits.max_strategy_family_pct == settings.risk_max_family_allocation_pct
    assert risk_engine.limits.max_daily_loss_pct == settings.risk_max_daily_loss_pct
    assert risk_engine.limits.max_portfolio_drawdown_pct == settings.risk_max_portfolio_dd_pct
    assert risk_engine.limits.vol_reduction_threshold == settings.vol_reduction_threshold
