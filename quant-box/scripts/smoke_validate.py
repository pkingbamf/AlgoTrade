from pathlib import Path

REQUIRED_FILES = [
    "app/main.py",
    "app/api/routes.py",
    "risk/policies.py",
    "monitoring/observability.py",
    "frontend/templates/index.html",
]

REQUIRED_ROUTE_STRINGS = [
    '"/health"',
    '"/metrics"',
    '"/backtests/run"',
    '"/paper/orders"',
    '"/risk/state"',
    '"/system/logs"',
    '"/dashboard/overview"',
]


def main() -> None:
    missing = [p for p in REQUIRED_FILES if not Path(p).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    routes_content = Path("app/api/routes.py").read_text()
    missing_routes = [r for r in REQUIRED_ROUTE_STRINGS if r not in routes_content]
    if missing_routes:
        raise SystemExit(f"Missing required route signatures: {missing_routes}")

    print("smoke validation passed")


if __name__ == "__main__":
    main()
