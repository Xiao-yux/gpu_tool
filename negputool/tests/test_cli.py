"""Smoke tests for the Typer CLI app."""

from __future__ import annotations

import re
import subprocess
import sys

from typer.testing import CliRunner

from negpu.cli import app
from negpu._version import __version__


runner = CliRunner(mix_stderr=False)


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


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "negpu" in result.stdout


def test_python_dash_m_negpu_invokes_app() -> None:
    """``python -m negpu`` should behave like ``negpu`` on the CLI."""
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "negpu", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert __version__ in proc.stdout
    assert re.search(r"negpu\s+\d+\.\d+\.\d+", proc.stdout)