# Project Status

## Current Phase
Phase 7 — API (Complete)

---

# Completed

## Phase 1 — Foundation
Completed:
- repo scaffold, Docker, env config, DB base models, logging

## Phase 2 — Research Engine
Completed:
- ingestion, validation, spec schema, sweep engine, experiment persistence

## Phase 3 — Backtesting & Validation
Completed:
- backtesting metrics, walk-forward, Monte Carlo, sensitivity, reports

## Phase 4 — Paper Trading System
Completed:
- paper execution, deployment registry, audit logging, reconciliation

## Phase 5 — Risk Management
Completed:
- hard pre-trade limits, kill-switch and strategy disable controls, vol sizing reduction

## Phase 6 — Monitoring & Observability
Completed:
- health metadata, system metrics, stale-data detection, job tracking, alert hooks

## Phase 7 — API
Completed:
- FastAPI backend initialized and routed
- strategy endpoints (`/strategy-specs`, `/strategies`, `/strategies/{id}`)
- backtest endpoints (`/backtests/run`, `/backtests/{id}`, `/backtests/{id}/report`)
- rankings/promotions endpoints (`/rankings`, `/promotions`)
- paper trading endpoints (`/paper/deployments`, `/paper/orders`, `/paper/positions`, `/paper/pnl`, `/paper/portfolio-monitor`, `/paper/reconcile/{strategy_id}`)
- risk endpoints (`/risk/state`, `/risk/limits`, `/risk/kill-switch/{active}`, `/risk/disable/{strategy_id}`, `/risk/enable/{strategy_id}`)
- metrics endpoint (`/metrics`) and health endpoint (`/health`)

---

# Current Work

Phase 7 validation complete; preparing for Phase 8 dashboard expansion.

---

# Decisions

- API remains sync + DB-backed for MVP simplicity
- risk and monitoring are integrated into API flow at order and health/metrics boundaries

---

# Known Issues

- Full pytest still depends on runtime libraries unavailable in minimal runner environments.

---

# Next Phase

Phase 8 — Dashboard
