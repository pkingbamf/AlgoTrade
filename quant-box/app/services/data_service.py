from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models import DataAsset


class DataService:
    """Market data ingestion, validation, storage metadata, and resampling helpers."""

    REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close", "volume"}

    def ingest_csv(self, source_path: str, target_parquet_path: str) -> pd.DataFrame:
        df = pd.read_csv(source_path)
        self.validate_ohlcv(df)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])
        Path(target_parquet_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(target_parquet_path, index=False)
        return df

    def persist_metadata(self, db: Session, source: str, symbol: str, timeframe: str, parquet_path: str) -> DataAsset:
        df = pd.read_parquet(parquet_path)
        asset = DataAsset(
            source=source,
            symbol=symbol,
            timeframe=timeframe,
            parquet_path=parquet_path,
            start_ts=str(df["timestamp"].min()),
            end_ts=str(df["timestamp"].max()),
            row_count=len(df),
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    def validate_ohlcv(self, df: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS.difference(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        if df[list(self.REQUIRED_COLUMNS)].isnull().any().any():
            raise ValueError("Detected null values in required OHLCV columns")
        if (df["volume"] < 0).any():
            raise ValueError("Volume cannot be negative")

    def resample(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        indexed = df.copy()
        indexed["timestamp"] = pd.to_datetime(indexed["timestamp"], utc=True)
        indexed = indexed.set_index("timestamp")
        out = indexed.resample(timeframe).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        return out.dropna().reset_index()
