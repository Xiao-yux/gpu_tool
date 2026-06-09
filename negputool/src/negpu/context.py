"""negpu.context - explicit dependency-injection container.

Per REFACTORING_TASK [13]A: every module receives a :class:`Context`
explicitly. There is **no** global singleton.

Typical usage::

    ctx = Context.create()
    async with ctx:
        await ctx.system_collector.collect_all()
        await ctx.logger.start_sampler()

The :class:`Context` is a frozen dataclass, so it can be safely shared
between coroutines and tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Self

from negpu.config.loader import load_config
from negpu.config.model import NegpuConfig
from negpu.config.paths import LogPaths
from negpu.i18n.loader import I18n
from negpu.log.logger import NegpuLogger


@dataclass(frozen=True)
class Context:
    """Immutable application context.

    Combine a :class:`NegpuConfig` with its resolved :class:`LogPaths`,
    an :class:`I18n` translator, and a :class:`NegpuLogger`.
    """

    config: NegpuConfig
    paths: LogPaths
    i18n: I18n
    logger: NegpuLogger

    # ---- factory ----

    @classmethod
    def create(
        cls,
        config_path: str | Path | None = None,
        *,
        install_if_missing: bool = True,
        sn: str | None = None,
    ) -> Self:
        """Build a Context with full config discovery and path resolution.

        * ``config_path`` — explicit override; skip search.
        * ``install_if_missing`` — controls the first-run copy to
          ``/etc/negpu/config.toml`` (Linux only).
        * ``sn`` — override the chassis serial number (used by tests
          and by the WSL fallback).
        """
        config, _source = load_config(
            config_path,
            install_if_missing=install_if_missing,
        )
        paths = LogPaths.for_session(config.log.log_path, sn=sn)
        i18n = I18n(config.language.language)
        logger = NegpuLogger(config.log, paths)
        return cls(config=config, paths=paths, i18n=i18n, logger=logger)

    # ---- convenience accessors ----

    def t(self, key: str, default: str = "") -> str:
        """Translate a key (shorthand for ``self.i18n.get(key, default)``)."""
        return self.i18n.get(key, default)

    def log_msg(
        self,
        message: str,
        level: str = "INFO",
        logger_name: str = "main",
        outconsole: bool = False,
    ) -> None:
        """Log via the context's logger (shorthand).

        ``level`` accepts any of ``"DEBUG" / "INFO" / "WARNING" /
        "ERROR" / "CRITICAL"``; the type is widened to ``str`` so
        callers can pass raw config values without casting.
        """
        self.logger.msg(message, level, logger_name, outconsole)  # type: ignore[arg-type]

    # ---- async lifecycle (REFACTORING_TASK [12]A sampler) ----

    async def __aenter__(self) -> Self:
        await self.logger.start_sampler()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.logger.stop_sampler()