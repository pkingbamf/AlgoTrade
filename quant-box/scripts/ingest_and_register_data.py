from app.db.session import SessionLocal
from app.services.data_service import DataService


if __name__ == "__main__":
    service = DataService()
    db = SessionLocal()
    try:
        service.ingest_csv("data/raw/sample_ohlcv.csv", "data/processed/sample_ohlcv.parquet")
        asset = service.persist_metadata(
            db,
            source="sample",
            symbol="BTCUSDT",
            timeframe="1h",
            parquet_path="data/processed/sample_ohlcv.parquet",
        )
        print({"data_asset_id": asset.id, "rows": asset.row_count})
    finally:
        db.close()
