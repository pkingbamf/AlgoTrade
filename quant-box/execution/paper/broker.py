from dataclasses import dataclass


@dataclass
class PaperPositionState:
    quantity: float
    avg_price: float


class PaperBroker:
    def __init__(self):
        self.positions: dict[str, PaperPositionState] = {}
        self.orders: list[dict] = []

    def place_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        signed_qty = quantity if side == "buy" else -quantity
        pos = self.positions.get(symbol, PaperPositionState(quantity=0.0, avg_price=0.0))
        new_qty = pos.quantity + signed_qty
        if new_qty != 0:
            avg = ((pos.quantity * pos.avg_price) + (signed_qty * price)) / new_qty
        else:
            avg = 0.0
        self.positions[symbol] = PaperPositionState(quantity=new_qty, avg_price=avg)
        order = {"symbol": symbol, "side": side, "quantity": quantity, "price": price, "status": "filled"}
        self.orders.append(order)
        return order

    def pnl_snapshot(self, marks: dict[str, float]) -> dict:
        unrealized = 0.0
        exposure = 0.0
        for sym, pos in self.positions.items():
            mark = marks.get(sym, pos.avg_price)
            unrealized += (mark - pos.avg_price) * pos.quantity
            exposure += abs(mark * pos.quantity)
        return {"unrealized_pnl": unrealized, "exposure": exposure}

    def portfolio_monitor(self, marks: dict[str, float] | None = None) -> dict:
        marks = marks or {}
        pnl = self.pnl_snapshot(marks)
        positions = {symbol: {"quantity": p.quantity, "avg_price": p.avg_price} for symbol, p in self.positions.items()}
        return {"positions": positions, "orders": len(self.orders), "unrealized_pnl": pnl["unrealized_pnl"], "exposure": pnl["exposure"]}
