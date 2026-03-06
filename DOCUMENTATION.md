# Project Status

## Current Phase
Phase 2 — Research Engine (Complete)

---

# Completed

## Phase 1 — Foundation
Completed:
- repo scaffold
- Docker configuration
- PostgreSQL setup
- environment handling
- logging
- base architecture
- startup lifecycle hardening (`FastAPI` lifespan)
- sqlite thread-safety config for local dev/test

## Phase 2 — Research Engine
Completed:
- market data ingestion (`DataService.ingest_csv`)
- parquet storage + metadata persistence to DB (`DataAsset`)
- data validation utilities (required columns, null checks, negative volume checks)
- YAML strategy specification schema validation (`StrategySpecSchema`)
- strategy generator and variant materialization
- feature calculation utilities
- factor library utilities
- parameter sweep engine (`ParameterSweepEngine`)
- experiment runner (`ExperimentService`)
- experiment results persistence (`ExperimentRun`, `ExperimentResult`)

---

# Current Work

Phase 2 closeout hardening and tests.

---

# Decisions

- PostgreSQL for metadata and experiment persistence
- parquet as research data store for fast iteration
- pydantic schema validation at spec load/persist boundaries
- parameter sweep + experiment ranking by Sharpe for MVP

---

# Known Issues

- Environment dependency availability may impact local `pytest` execution if packages are not installed.

---

# Next Phase

Phase 3 — Backtesting & Validation
