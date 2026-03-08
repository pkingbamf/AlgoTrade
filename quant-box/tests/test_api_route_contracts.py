from pathlib import Path


def test_required_api_contract_routes_present():
    content = Path("app/api/routes.py").read_text()
    required = [
        '"/health"',
        '"/metrics"',
        '"/strategies"',
        '"/strategy-specs"',
        '"/backtests/run"',
        '"/rankings"',
        '"/promotions"',
        '"/paper/orders"',
        '"/paper/positions"',
        '"/paper/pnl"',
        '"/risk/state"',
        '"/risk/limits"',
        '"/system/logs"',
    ]
    for route in required:
        assert route in content, f"missing route {route}"
