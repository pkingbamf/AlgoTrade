from pathlib import Path


TEMPLATES = [
    "frontend/templates/index.html",
    "frontend/templates/strategy_library.html",
    "frontend/templates/backtest_runs.html",
    "frontend/templates/rankings.html",
    "frontend/templates/paper_trading.html",
    "frontend/templates/risk_monitor.html",
    "frontend/templates/system_health.html",
]


def test_dashboard_templates_exist():
    for template in TEMPLATES:
        assert Path(template).exists(), f"missing template {template}"


def test_overview_template_has_navigation_links():
    html = Path("frontend/templates/index.html").read_text()
    assert "/dashboard/overview" in html
    assert "/dashboard/system-health" in html
