"""Tests for negpu.log.system_collector."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

from negpu.log.system_collector import SystemCollector


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_default_commands_contains_expected_names() -> None:
    expected = {"dmesg", "nvidia-smi", "lspci", "lsblk",
                "ipmitool-lan", "ipmitool-sdr", "ipmitool-fru"}
    assert set(SystemCollector.DEFAULT_COMMANDS) == expected


def test_custom_commands_override_defaults(tmp_path: Path) -> None:
    custom = {"only_one": ("echo", "hi")}
    c = SystemCollector(tmp_path, commands=custom)
    assert c.commands == custom
    assert "dmesg" not in c.commands


# ---------------------------------------------------------------------------
# collect() / collect_all()
# ---------------------------------------------------------------------------


async def test_collect_all_writes_files_for_available_commands(
    tmp_path: Path,
) -> None:
    """Use a real command that always exists (``python -c``)."""
    commands = {
        "py-hello": (sys.executable, "-c", "print('hello')"),
        "py-bye": (sys.executable, "-c", "print('bye')"),
    }
    c = SystemCollector(tmp_path, commands=commands)
    results = await c.collect_all()
    assert results == {"py-hello": True, "py-bye": True}
    assert (tmp_path / "py-hello.log").is_file()
    assert (tmp_path / "py-bye.log").is_file()
    assert "hello" in (tmp_path / "py-hello.log").read_text(encoding="utf-8")


async def test_collect_writes_placeholder_for_missing_command(
    tmp_path: Path,
) -> None:
    commands = {"missing-cmd": ("__definitely_not_a_command_123__",)}
    c = SystemCollector(tmp_path, commands=commands)
    ok = await c.collect("missing-cmd")
    assert ok is False
    text = (tmp_path / "missing-cmd.log").read_text(encoding="utf-8")
    assert "# command not available" in text


async def test_collect_isolates_failures(tmp_path: Path) -> None:
    """One failing command does not affect the others."""
    commands = {
        "ok": (sys.executable, "-c", "print('hi')"),
        "missing": ("__definitely_not_a_command__",),
    }
    c = SystemCollector(tmp_path, commands=commands)
    results = await c.collect_all()
    assert results["ok"] is True
    assert results["missing"] is False
    assert (tmp_path / "ok.log").is_file()
    assert (tmp_path / "missing.log").is_file()


async def test_collect_unknown_name_raises(tmp_path: Path) -> None:
    c = SystemCollector(tmp_path, commands={"a": ("echo", "x")})
    with pytest.raises(KeyError):
        await c.collect("not_registered")


async def test_collect_all_creates_target_dir(tmp_path: Path) -> None:
    target = tmp_path / "new_subdir" / "system"
    assert not target.exists()
    c = SystemCollector(target, commands={"a": (sys.executable, "-c", "print()")})
    await c.collect_all()
    assert target.is_dir()
    assert (target / "a.log").is_file()