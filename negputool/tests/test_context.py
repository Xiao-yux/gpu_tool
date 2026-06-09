"""Tests for negpu.context (DI container)."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from negpu.config.model import LogConfig, NegpuConfig
from negpu.config.paths import LogPaths
from negpu.context import Context
from negpu.i18n.loader import I18n
from negpu.log.logger import NegpuLogger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    p = tmp_path / "config.toml"
    # Use forward slashes for the log path: backslashes in the TOML
    # string are interpreted as escape sequences (e.g. \U → "Invalid hex").
    log_dir = (tmp_path / "log").as_posix()
    p.write_text(
        dedent("""
            version = "1.2.3"
            [language]
            language = "en"
            [log]
            log_path = "{LOG_DIR}"
            log_file = "negpu_debug.log"
            log_level = "WARNING"
        """).strip()
        .replace("{LOG_DIR}", log_dir)
        + "\n",
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# create() factory
# ---------------------------------------------------------------------------


def test_context_create_uses_explicit_config(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    assert ctx.config.version == "1.2.3"
    assert ctx.config.log.log_level == "WARNING"
    assert isinstance(ctx.i18n, I18n)
    assert isinstance(ctx.logger, NegpuLogger)
    assert isinstance(ctx.paths, LogPaths)


def test_context_create_uses_in_memory_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("negpu.config.loader._SEARCH_PATHS", ())
    monkeypatch.delenv("NEGPU_CONFIG", raising=False)
    # Force a deterministic language regardless of the host's LANG.
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.setattr("negpu.config.paths.current_user", lambda: "tester")
    ctx = Context.create(install_if_missing=False, sn="TESTSN")
    assert isinstance(ctx.config, NegpuConfig)
    assert ctx.config.log.log_level == "INFO"
    assert ctx.i18n.language == "en"  # no LANG env → en
    # Paths include the sn and timestamp
    assert "TESTSN" in str(ctx.paths.root)


def test_context_paths_reflect_config(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    # ``paths.root`` is ``<log_path>/<sn>/<timestamp>``, so
    # ``paths.root.parent.parent`` should equal ``log_path``.
    assert ctx.paths.root.parent.parent == Path(str(ctx.config.log.log_path))
    # The sn is part of the path
    assert "TESTSN" in str(ctx.paths.root)
    # The timestamp dir is the immediate parent of ``system``/``run``/etc.
    assert ctx.paths.run.parent == ctx.paths.root


# ---------------------------------------------------------------------------
# Shorthand helpers
# ---------------------------------------------------------------------------


def test_context_t_shorthand(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    # "menu.exit" is a key we know exists in en.json
    assert ctx.t("menu.exit") == "Exit"


def test_context_t_returns_default_on_miss(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    assert ctx.t("nonexistent.key", "fallback") == "fallback"


def test_context_log_msg_shorthand(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    # The test config sets log_level = "WARNING" so we must log at
    # WARNING or above to be visible in the main log.
    ctx.log_msg("hello from context", level="WARNING")
    content = ctx.logger.get_main_log_file().read_text(encoding="utf-8")
    assert "hello from context" in content


# ---------------------------------------------------------------------------
# Async lifecycle (sampler)
# ---------------------------------------------------------------------------


async def test_context_aenter_starts_sampler(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    assert not ctx.logger.sampler_running
    async with ctx:
        assert ctx.logger.sampler_running
    assert not ctx.logger.sampler_running


async def test_context_aexit_stops_sampler(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    async with ctx:
        await ctx.logger.stop_sampler()  # stop inside to test idempotency
    # outside the block, it's already stopped — calling again is safe
    await ctx.logger.stop_sampler()
    assert not ctx.logger.sampler_running


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


def test_context_is_frozen(config_path: Path) -> None:
    ctx = Context.create(config_path, sn="TESTSN")
    with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
        ctx.config = ctx.config  # type: ignore[misc]