"""Smoke tests for the Typer CLI app."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from negpu.cli import app
from negpu._version import __version__


runner = CliRunner()


def test_version_flag_prints_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
    assert "negpu" in result.stdout


def test_help_flag_works() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "negpu" in result.stdout


def test_doctor_command_runs_placeholder() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Phase 2" in result.stdout


def test_config_show_command_runs_placeholder() -> None:
    result = runner.invoke(app, ["config-show"])
    assert result.exit_code == 0
    assert "Phase 2" in result.stdout


def test_menu_command_runs_placeholder() -> None:
    result = runner.invoke(app, ["menu"])
    assert result.exit_code == 0
    assert "Phase 5" in result.stdout


def test_no_args_mentions_negpu_somewhere() -> None:
    """With no args, typer should print help/usage that mentions 'negpu'.

    Some typer/click combinations exit 0 (no_args_is_help), others exit 2;
    we only care that the program name is visible in the output.
    """
    result = runner.invoke(app, [])
    output = (result.stdout or "") + (result.stderr or "")
    assert "negpu" in output
    # Acceptable: exit 0 (help shown) or 2 (usage error); not 1 (real failure).
    assert result.exit_code in (0, 2), f"unexpected exit code: {result.exit_code}"


def test_python_dash_m_negpu_invokes_app() -> None:
    """``python -m negpu`` should behave like ``negpu`` on the CLI.

    We explicitly forward ``PYTHONPATH=src`` because the package may not
    be editable-installed in every dev environment.
    """
    src = str(Path(__file__).resolve().parent.parent / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "negpu", "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr!r}"
    assert __version__ in proc.stdout
    assert re.search(r"negpu\s+\d+\.\d+\.\d+", proc.stdout)