from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AuditLog, PaperOrder, PaperPosition, StrategyDeployment
from execution.paper.broker import PaperBroker


class PaperTradingService:
    """Handles paper deployments, executions, audit logs, and monitoring views."""

    def __init__(self, broker: PaperBroker):
        self.broker = broker

    def deploy_strategy(self, db: Session, strategy_id: str, config: dict | None = None) -> StrategyDeployment:
        deployment = StrategyDeployment(strategy_id=strategy_id, mode="paper", status="active", config=config or {})
        db.add(deployment)
        db.add(
            AuditLog(
                component="paper_trading",
                event_type="strategy_deployed",
                payload={"strategy_id": strategy_id, "timestamp": datetime.utcnow().isoformat()},
            )
        )
        db.commit()
        db.refresh(deployment)
        return deployment

    def execute_order(self, db: Session, strategy_id: str, symbol: str, side: str, quantity: float, price: float) -> dict:
        order = self.broker.place_order(symbol=symbol, side=side, quantity=quantity, price=price)

        db_order = PaperOrder(
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status=order["status"],
        )
        db.add(db_order)

        pos_state = self.broker.positions.get(symbol)
        if pos_state is not None:
            db_pos = db.query(PaperPosition).filter(PaperPosition.strategy_id == strategy_id, PaperPosition.symbol == symbol).first()
            if db_pos is None:
                db_pos = PaperPosition(
                    strategy_id=strategy_id,
                    symbol=symbol,
                    quantity=pos_state.quantity,
                    avg_price=pos_state.avg_price,
                    mark_price=price,
                    unrealized_pnl=0.0,
                )
                db.add(db_pos)
            else:
                db_pos.quantity = pos_state.quantity
                db_pos.avg_price = pos_state.avg_price
                db_pos.mark_price = price
                db_pos.unrealized_pnl = (price - db_pos.avg_price) * db_pos.quantity
                db_pos.updated_at = datetime.utcnow()

        db.add(
            AuditLog(
                component="paper_trading",
                event_type="order_executed",
                payload={
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                },
            )
        )

        db.commit()
        return order

    def portfolio_monitor(self, marks: dict[str, float] | None = None) -> dict:
        return self.broker.portfolio_monitor(marks or {})

    def reconcile_positions(self, db: Session, strategy_id: str) -> dict:
        persisted = db.query(PaperPosition).filter(PaperPosition.strategy_id == strategy_id).all()
        persisted_map = {p.symbol: p.quantity for p in persisted}
        broker_map = {k: v.quantity for k, v in self.broker.positions.items()}
        mismatches = [sym for sym in set(persisted_map) | set(broker_map) if persisted_map.get(sym, 0.0) != broker_map.get(sym, 0.0)]

        db.add(
            AuditLog(
                component="paper_trading",
                event_type="position_reconciliation",
                payload={"strategy_id": strategy_id, "mismatch_count": len(mismatches), "symbols": mismatches},
            )
        )
        db.commit()
        return {"mismatch_count": len(mismatches), "symbols": mismatches}
