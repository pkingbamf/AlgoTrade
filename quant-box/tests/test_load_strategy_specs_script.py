from pathlib import Path


def test_load_strategy_specs_initializes_schema_before_session():
    script = Path("scripts/load_strategy_specs.py").read_text()
    assert "init_db()" in script
    assert script.index("init_db()") < script.index("SessionLocal()")
