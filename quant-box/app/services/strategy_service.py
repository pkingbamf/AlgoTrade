from itertools import product
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import StrategySpec


class StrategyService:
    def load_spec(self, path: str) -> dict:
        return yaml.safe_load(Path(path).read_text())

    def persist_spec(self, db: Session, spec: dict) -> StrategySpec:
        payload = StrategySpec(
            strategy_id=spec["strategy_id"],
            family=spec["family"],
            timeframe=spec["timeframe"],
            universe={"assets": spec["asset_universe"]},
            spec=spec,
        )
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload

    def generate_variants(self, spec: dict) -> list[dict]:
        ranges = spec["parameter_ranges"]
        keys = list(ranges.keys())
        combos = list(product(*(ranges[k] for k in keys)))
        return [{"strategy_id": spec["strategy_id"], "params": dict(zip(keys, values))} for values in combos]
