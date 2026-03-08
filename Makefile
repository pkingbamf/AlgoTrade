.PHONY: install test test-targeted compile smoke

install:
	cd quant-box && pip install -e .[dev]

test:
	cd quant-box && pytest -q

test-targeted:
	cd quant-box && pytest -q tests/test_monitoring_service.py tests/test_risk_engine.py tests/test_risk_controls_phase5.py tests/test_api_route_contracts.py tests/test_risk_broker_integration.py tests/test_backtest_invariants.py tests/test_dashboard_templates.py

compile:
	cd quant-box && python -m compileall app monitoring risk backtests tests

smoke:
	cd quant-box && python scripts/smoke_validate.py
