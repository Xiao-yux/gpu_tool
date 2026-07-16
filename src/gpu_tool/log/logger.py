"""negpu.log.logger - async-aware logging façade.

Wraps stdlib :mod:`logging` 

The format:

    ``%(asctime)s [%(levelname)s] %(name)s: %(message)s``
"""

from __future__ import annotations


import inspect
import logging
from pathlib import Path
from typing import Literal


from config.model import LogConfig
from config.paths import LogPaths
from log.filter import clean

# Per REFACTORING_TASK [9]A
_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]



class gpuLogger:
    """
    Async-aware logging façade wrapping stdlib :mod:`logging`.

    Provides ``info`` / ``debug`` / ``warning`` / ``error`` / ``critical``
    methods (mirroring the stdlib API) that each accept two extra
    parameters in addition to the message:

    * ``file_name`` — target log file.  When ``None`` (the default) the
      class falls back to :attr:`LogConfig.log_file`.  Sub-directories
      are supported: passing ``"123/123"`` writes to
      ``<self.paths.root>/123/123.log`` and creates any missing parent
      directories on demand.  The ``.log`` suffix is appended
      automatically when missing.
    * ``console`` — when ``True`` the message is also echoed to stdout
      (in addition to being written to the log file).

    The output format is the module-level :data:`_FORMAT`
    (``"%(asctime)s [%(levelname)s] %(name)s: %(message)s"``).
    """

    def __init__(self, log_config: LogConfig) -> None:
        self.config = log_config
        self.paths = LogPaths.for_session(self.config.log_path)
        # Cache stdlib loggers/handlers per resolved log file path so that
        # repeated calls reuse the same handler (and append to the same
        # file) instead of opening a new FD each time.
        self._loggers: dict[str, tuple[logging.Logger, logging.FileHandler]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_log_file(self, file_name: str | None) -> Path:
        """Resolve the absolute log file path.

        * Falls back to :attr:`LogConfig.log_file` when ``file_name`` is
          ``None`` or an empty string.
        * Accepts relative sub-paths such as ``"123/123"`` — the parent
          directories are created under :attr:`paths.root`.
        * Ensures the resulting file name ends with ``.log``.
        """
        name = (file_name or self.config.log_file).strip().strip("/\\")
        if not name:
            name = self.config.log_file
        if not name.lower().endswith(".log"):
            name = f"{name}.log"
        log_path = self.paths.root / name
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def _get_logger(
        self, caller_name: str, file_name: str | None
    ) -> tuple[logging.Logger, logging.FileHandler]:
        """Return a cached ``(logger, file_handler)`` pair for ``file_name``."""

        log_path = self._resolve_log_file(file_name)
        key = str(log_path)

        cached = self._loggers.get(key)
        if cached is not None:
            return cached

        logger = logging.getLogger(caller_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        # Drop any pre-existing handlers to keep the logger self-contained.
        for h in list(logger.handlers):
            logger.removeHandler(h)

        formatter = logging.Formatter(_FORMAT)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self._loggers[key] = (logger, file_handler)
        return self._loggers[key]

    def _log(
        self,
        level: Level,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Shared implementation behind every public log method."""
        text = clean(message) if message is not None else ""
        frame = inspect.stack()[2]
        caller_module = frame.frame.f_globals.get("__name__", "unknown")
        logger, _ = self._get_logger(caller_module, file_name)

        if console:
            print(f"[{level}] {text}", flush=True)

        log_fn = getattr(logger, level.lower())
        log_fn(text)

    # ------------------------------------------------------------------
    # Inherited-style log helpers (stdlib-shaped, with two extra kwargs)
    # ------------------------------------------------------------------

    def info(
        self,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Log an ``INFO`` level message."""
        self._log("INFO", message, file_name, console)

    def debug(
        self,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Log a ``DEBUG`` level message."""
        self._log("DEBUG", message, file_name, console)

    def warning(
        self,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Log a ``WARNING`` level message."""
        self._log("WARNING", message, file_name, console)

    def error(
        self,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Log an ``ERROR`` level message."""
        self._log("ERROR", message, file_name, console)

    def critical(
        self,
        message: str,
        file_name: str | None = None,
        console: bool = False,
    ) -> None:
        """Log a ``CRITICAL`` level message."""
        self._log("CRITICAL", message, file_name, console)


# ---------------------------------------------------------------------------
# Module-level 
# ---------------------------------------------------------------------------

_default: gpuLogger | None = None


def init_logger(log_config: LogConfig) -> gpuLogger:
    """Initialise the module-level default logger."""
    global _default
    _default = gpuLogger(log_config)
    return _default


def get_logger() -> gpuLogger:
    """Return the previously-initialised default logger."""
    if _default is None:
        raise RuntimeError("gpu logger not initialised; call init_logger() first")
    return _default