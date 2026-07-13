"""log.path - re-exports of path helpers for log-specific use.
"""

from __future__ import annotations

from config.paths import (  # noqa: F401
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