import subprocess


def test_smoke_validate_script_runs():
    proc = subprocess.run(["python", "scripts/smoke_validate.py"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "smoke validation passed" in proc.stdout
