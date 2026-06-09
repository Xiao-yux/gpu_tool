"""negpu.log.logger - async-aware logging façade.

Wraps stdlib :mod:`logging` and provides:

* per-test log files (one ``logging.Logger`` per test case name)
* main debug log at the time-stamped root
* 5-minute ``nvidia-smi`` sampler task (REFACTORING_TASK [12]A;
  paused by FD tests in Phase 4)
* the small ``msg()`` API that the rest of the codebase already uses

The format follows REFACTORING_TASK [9]A:

    ``%(asctime)s [%(levelname)s] %(name)s: %(message)s``
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Literal, Protocol

import aiofiles

from negpu.config.model import LogConfig
from negpu.config.paths import LogPaths
from negpu.log.filter import clean

# Per REFACTORING_TASK [9]A
_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_INTERVAL_SEC: int = 300  # 5 minutes

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class _PathsLike(Protocol):
    """Anything with ``time_5_log`` and ``run`` attributes works."""

    time_5_log: Path
    run: Path
    root: Path


class NegpuLogger:
    """Async-aware logging façade.

    >>> import tempfile, pathlib
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     cfg = LogConfig(log_path=str(pathlib.Path(tmp) / "log"))
    ...     paths = LogPaths.for_session(cfg.log_path)
    ...     log = NegpuLogger(cfg, paths)
    ...     log.msg("hello world")
    ...     log_paths = sorted(p.name for p in pathlib.Path(tmp).rglob("*.log"))
    >>> any("negpu_debug" in p for p in log_paths)  # main log was created
    True
    """

    def __init__(self, log_config: LogConfig, paths: LogPaths) -> None:
        self.config = log_config
        self.paths = paths
        self._loggers: dict[str, logging.Logger] = {}
        self._sampler_task: asyncio.Task[None] | None = None
        self._sampler_interval: int = _DEFAULT_INTERVAL_SEC
        self._sampler_running: bool = False
        self._init_main()

    # ---- public API ----

    def msg(
        self,
        message: str,
        level: Level = "INFO",
        logger_name: str = "main",
        outconsole: bool = False,
    ) -> None:
        """Log a message; optionally echo to console.

        ``message`` is passed through :func:`negpu.log.filter.clean` so
        raw subprocess output is safe to log directly.
        """
        text = clean(message)
        if not text:
            return
        if logger_name not in self._loggers:
            # auto-create a logger in run/ for unknown names
            self.create_log_file(logger_name)
        logger = self._loggers.get(logger_name, self._loggers["main"])
        getattr(logger, level.lower())(text)
        if outconsole or self.config.console_output:
            print(text)

    def create_log_file(self, name: str, subdir: str = "") -> str:
        """Create a per-test logger writing to ``run/<subdir>/<name>.log``.

        Returns the canonical logger name (file name without ``.log``).
        Subsequent calls with the same name are idempotent.
        """
        if not name.endswith(".log"):
            name = f"{name}.log"
        logger_name = Path(name).stem
        if logger_name in self._loggers:
            return logger_name
        target_dir = (self.paths.run / subdir) if subdir else self.paths.run
        target_dir.mkdir(parents=True, exist_ok=True)
        log_file = target_dir / name
        self._loggers[logger_name] = self._make_logger(logger_name, log_file)
        return logger_name

    def get_log_file(self) -> Path:
        """Return the time-stamped log root (e.g. ``.../2026-06-08-16/``)."""
        return self.paths.root

    def get_main_log_file(self) -> Path:
        """Return the path of the main debug log file."""
        return self.paths.root / self.config.log_file

    # ---- 5-minute sampler (REFACTORING_TASK [12]A) ----

    async def start_sampler(self, interval_sec: int = _DEFAULT_INTERVAL_SEC) -> None:
        """Start the periodic ``nvidia-smi`` background task.

        Idempotent. Safe to call multiple times; only one task runs.
        """
        if self._sampler_task is not None and not self._sampler_task.done():
            return
        self._sampler_interval = interval_sec
        self._sampler_task = asyncio.create_task(
            self._sampler_loop(),
            name="negpu-time5-sampler",
        )

    async def stop_sampler(self) -> None:
        """Stop the background sampler. Safe to call when not running."""
        if self._sampler_task is None:
            return
        self._sampler_task.cancel()
        try:
            await self._sampler_task
        except asyncio.CancelledError:
            pass
        finally:
            self._sampler_task = None

    @property
    def sampler_running(self) -> bool:
        return self._sampler_task is not None and not self._sampler_task.done()

    async def _sampler_loop(self) -> None:
        """Periodically run ``nvidia-smi`` and append to ``time_5_log``."""
        # Wait one interval before the first sample (don't snapshot at t=0).
        while True:
            try:
                await asyncio.sleep(self._sampler_interval)
                await self._sample_once()
            except asyncio.CancelledError:
                return
            except Exception:  # noqa: BLE001 - never let the sampler crash the app
                # Swallow & continue; sampling is best-effort.
                await asyncio.sleep(5)

    async def _sample_once(self) -> None:
        target = self.paths.time_5_log
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            proc = await asyncio.create_subprocess_exec(
                "nvidia-smi",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await proc.communicate()
        except (FileNotFoundError, PermissionError, OSError):
            return
        async with aiofiles.open(target, "ab") as f:
            header = f"\n# {time.strftime('%Y-%m-%d %H:%M:%S')}\n".encode()
            await f.write(header)
            await f.write(stdout)

    # ---- internals ----

    def _init_main(self) -> None:
        main_log = self.paths.root / self.config.log_file
        self._loggers["main"] = self._make_logger("main", main_log)

    def _make_logger(self, name: str, file: Path) -> logging.Logger:
        logger = logging.getLogger(f"negpu.{name}")
        logger.setLevel(self.config.log_level)
        # Don't propagate to root (avoids duplicate console output).
        logger.propagate = False
        # Close + remove any existing handlers (idempotent re-create
        # AND prevents ``ResourceWarning: unclosed file`` warnings when
        # a test re-uses a logger name on a different path).
        for h in list(logger.handlers):
            try:
                h.close()
            except Exception:  # noqa: BLE001
                pass
            logger.removeHandler(h)
        file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(file, encoding="utf-8")
        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)
        if self.config.console_output:
            console = logging.StreamHandler()
            console.setFormatter(logging.Formatter(_FORMAT))
            logger.addHandler(console)
        return logger

    def close(self) -> None:
        """Close all log handlers, releasing the underlying file handles.

        Call this in fixture teardown (or at process exit) to avoid
        ``ResourceWarning`` on Windows / pytest.
        """
        for logger in self._loggers.values():
            for h in list(logger.handlers):
                try:
                    h.close()
                except Exception:  # noqa: BLE001
                    pass
                logger.removeHandler(h)
        self._loggers.clear()


# ---------------------------------------------------------------------------
# Module-level convenience (mirrors the old negpu.log.msg() API)
# ---------------------------------------------------------------------------

_default: NegpuLogger | None = None


def init_logger(log_config: LogConfig, paths: LogPaths) -> NegpuLogger:
    """Initialise the module-level default logger."""
    global _default
    _default = NegpuLogger(log_config, paths)
    return _default


def get_logger() -> NegpuLogger:
    """Return the previously-initialised default logger."""
    if _default is None:
        raise RuntimeError("negpu logger not initialised; call init_logger() first")
    return _default