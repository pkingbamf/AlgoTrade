from itertools import product
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import StrategySpec
from app.schemas.research import StrategySpecSchema


class StrategyService:
    def load_spec(self, path: str) -> dict:
        payload = yaml.safe_load(Path(path).read_text())
        return StrategySpecSchema(**payload).model_dump()

    def persist_spec(self, db: Session, spec: dict) -> StrategySpec:
        validated = StrategySpecSchema(**spec).model_dump()
        payload = StrategySpec(
            strategy_id=validated["strategy_id"],
            family=validated["family"],
            timeframe=validated["timeframe"],
            universe={"assets": validated["asset_universe"]},
            spec=validated,
        )
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload

    def generate_variants(self, spec: dict) -> list[dict]:
        validated = StrategySpecSchema(**spec).model_dump()
        ranges = validated["parameter_ranges"]
        keys = list(ranges.keys())
        combos = list(product(*(ranges[k] for k in keys)))
        return [{"strategy_id": validated["strategy_id"], "params": dict(zip(keys, values))} for values in combos]
