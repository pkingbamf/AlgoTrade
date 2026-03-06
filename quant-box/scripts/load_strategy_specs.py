from pathlib import Path

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.services.strategy_service import StrategyService


if __name__ == "__main__":
    service = StrategyService()
    db = SessionLocal()
    try:
        for p in sorted(Path("research/strategy_specs").glob("*.yaml")):
            spec = service.load_spec(str(p))
            try:
                service.persist_spec(db, spec)
                print(f"loaded {spec['strategy_id']}")
            except IntegrityError:
                db.rollback()
                print(f"skipped existing {spec['strategy_id']}")
    finally:
        db.close()
