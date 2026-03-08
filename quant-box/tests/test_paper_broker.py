from execution.paper.broker import PaperBroker


def test_order_execution_and_position_tracking():
    broker = PaperBroker()
    broker.place_order(symbol="BTCUSDT", side="buy", quantity=1.0, price=100.0)
    broker.place_order(symbol="BTCUSDT", side="buy", quantity=1.0, price=120.0)
    position = broker.positions["BTCUSDT"]
    assert position.quantity == 2.0
    assert round(position.avg_price, 2) == 110.0


def test_pnl_calculation_snapshot():
    broker = PaperBroker()
    broker.place_order(symbol="BTCUSDT", side="buy", quantity=2.0, price=100.0)
    pnl = broker.pnl_snapshot({"BTCUSDT": 110.0})
    assert pnl["unrealized_pnl"] == 20.0
    assert pnl["exposure"] == 220.0
