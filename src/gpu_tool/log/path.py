"""negpu.log.path - re-exports of path helpers for log-specific use.

Most code can simply :mod:`import negpu.config.paths` directly. This
module exists so that tests and downstream consumers can write
``negpu.log.path.LogPaths`` and have a stable, narrow import surface.
"""

from __future__ import annotations

from gpu_tool.config.paths import (  # noqa: F401
    REPORT_SUBDIR,
    RUN_SUBDIR,
    SCRIPT_SUBDIR,
    SYSTEM_SUBDIR,
    LogPaths,
    current_user,
    serial_number,
    timestamp_dir,
    user_log_root,
)

__all__: list[str] = [
    "REPORT_SUBDIR",
    "RUN_SUBDIR",
    "SCRIPT_SUBDIR",
    "SYSTEM_SUBDIR",
    "LogPaths",
    "current_user",
    "serial_number",
    "timestamp_dir",
    "user_log_root",
]