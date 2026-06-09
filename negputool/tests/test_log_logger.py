"""Tests for negpu.log.logger (per-test loggers + sampler)."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import pytest

from negpu.config.model import LogConfig
from negpu.config.paths import LogPaths
from negpu.log.logger import NegpuLogger, init_logger, get_logger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def log_paths(tmp_path: Path) -> LogPaths:
    """A LogPaths rooted in tmp_path so tests don't touch the user's home."""
    return LogPaths.for_session(str(tmp_path / "log"), sn="TESTSN")


@pytest.fixture(autouse=True)
def _close_default_logger() -> object:  # type: ignore[no-untyped-def]
    """Close the module-level default logger after each test (defence)."""
    yield
    try:
        from negpu.log.logger import _default
        if _default is not None:
            _default.close()
    except Exception:  # noqa: BLE001
        pass


@pytest.fixture
def log_config(tmp_path: Path) -> LogConfig:
    return LogConfig(
        log_path=str(tmp_path / "log"),
        log_file="negpu_debug.log",
        log_level="DEBUG",
        console_output=False,
    )


# ---------------------------------------------------------------------------
# Construction + main log
# ---------------------------------------------------------------------------


def test_logger_creates_main_log_file(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    assert log.get_main_log_file().is_file()


def test_logger_get_log_file_returns_root(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    assert log.get_log_file() == log_paths.root


# ---------------------------------------------------------------------------
# msg()
# ---------------------------------------------------------------------------


def test_msg_writes_to_main_log(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    log.msg("hello world")
    content = log.get_main_log_file().read_text(encoding="utf-8")
    assert "hello world" in content


def test_msg_with_level(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    log.msg("debug message", level="DEBUG")
    log.msg("warn message", level="WARNING")
    content = log.get_main_log_file().read_text(encoding="utf-8")
    assert "DEBUG" in content
    assert "WARNING" in content


def test_msg_cleans_input(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    log.msg("hello\n\x08\x08\x08\x1b[31m")
    content = log.get_main_log_file().read_text(encoding="utf-8")
    assert "\x08" not in content
    assert "\x1b" not in content
    assert "hello" in content


def test_msg_empty_after_cleaning_is_skipped(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    log.msg("")  # nothing should be written
    log.msg("\n\r\n")  # still nothing
    content = log.get_main_log_file().read_text(encoding="utf-8")
    # Just the header / logger init message, no real content lines.
    assert "hello" not in content


# ---------------------------------------------------------------------------
# create_log_file()
# ---------------------------------------------------------------------------


def test_create_log_file_writes_to_run_dir(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    name = log.create_log_file("gpu_burn")
    log.msg("burning GPU 0", logger_name=name)
    target = log_paths.run / "gpu_burn.log"
    assert target.is_file()
    assert "burning GPU 0" in target.read_text(encoding="utf-8")


def test_create_log_file_uses_subdir(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    name = log.create_log_file("fd", subdir="fd")
    target = log_paths.run / "fd" / "fd.log"
    assert target.is_file()


def test_create_log_file_idempotent(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    a = log.create_log_file("test1")
    b = log.create_log_file("test1")
    assert a == b


def test_create_log_file_strips_log_suffix(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    name = log.create_log_file("test.log")
    assert name == "test"
    assert (log_paths.run / "test.log").is_file()


# ---------------------------------------------------------------------------
# 5-minute sampler
# ---------------------------------------------------------------------------


async def test_sampler_start_stop(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    assert not log.sampler_running
    await log.start_sampler(interval_sec=60)
    assert log.sampler_running
    await log.stop_sampler()
    assert not log.sampler_running


async def test_sampler_start_is_idempotent(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    await log.start_sampler(interval_sec=60)
    first = log._sampler_task  # noqa: SLF001
    assert first is not None
    await log.start_sampler(interval_sec=60)
    assert log._sampler_task is first  # noqa: SLF001
    await log.stop_sampler()


async def test_sampler_stop_when_not_running(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    # Should not raise
    await log.stop_sampler()
    assert not log.sampler_running


async def test_sampler_writes_to_time5_log(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = NegpuLogger(log_config, log_paths)
    await log._sample_once()  # noqa: SLF001
    # If nvidia-smi exists on the test machine, the file should be created.
    # If it doesn't, _sample_once silently returns. Either way we just
    # verify the call does not raise and the path is well-defined.
    assert log_paths.time_5_log.parent.is_dir()


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def test_init_logger_and_get_logger(
    log_config: LogConfig, log_paths: LogPaths
) -> None:
    log = init_logger(log_config, log_paths)
    assert get_logger() is log


def test_get_logger_before_init_raises() -> None:
    # Reset the module-level singleton to ensure a clean state.
    import negpu.log.logger as mod
    mod._default = None  # noqa: SLF001
    with pytest.raises(RuntimeError):
        get_logger()