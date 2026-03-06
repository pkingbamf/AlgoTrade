from app.db.session import SessionLocal
from app.services.experiment_service import ExperimentService


if __name__ == "__main__":
    db = SessionLocal()
    try:
        service = ExperimentService()
        result = service.run_experiment(db, strategy_id="trend_ma_cross_1", data_path="data/processed/sample_ohlcv.parquet", top_k=3)
        print(result)
    finally:
        db.close()
