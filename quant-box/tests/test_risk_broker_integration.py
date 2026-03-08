from execution.paper.broker import PaperBroker
from risk.policies import RiskEngine, RiskLimits


def test_risk_then_broker_order_flow():
    risk = RiskEngine(RiskLimits(max_position_pct=0.2, vol_reduction_threshold=0.2))
    broker = PaperBroker()

    ok, reason, mult = risk.check_order(
        order_notional=10000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.4,
        context={"daily_loss_pct": 0.0, "drawdown_pct": 0.0, "strategy_family_allocation_pct": 0.1, "asset_exposure_pct": 0.1},
    )

    assert ok and reason == "ok"
    assert 0.25 <= mult <= 1.0

    order = broker.place_order("BTCUSDT", "buy", quantity=1.0 * mult, price=10000.0)
    assert order["status"] == "filled"
    assert "BTCUSDT" in broker.positions
