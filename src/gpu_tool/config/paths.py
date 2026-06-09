"""Path resolution for the negpu runtime.

Centralises every "where on disk do we put things" decision so the rest of
the codebase never assembles paths by hand.

Layout (negpu >=0.1):

    /home/<user>/log/<sn>/<时间>/
    ├── system/     # dmesg, nvidia-smi, lspci, ipmitool* (collected on startup)
    ├── run/        # per-test command outputs
    ├── script/     # bash/*.sh execution logs
    ├── report/     # generated PDF / HTML / MD reports
    └── time_5_save_info.log
"""

from __future__ import annotations

import asyncio
import getpass
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

# Match the original gpu_tool timestamp format so log-compare tools work.
_TIMESTAMP_FMT: Final[str] = "%Y-%m-%d-%H"

# Sub-directories inside a single time-stamped log root.
SYSTEM_SUBDIR: Final[str] = "system"
RUN_SUBDIR: Final[str] = "run"
SCRIPT_SUBDIR: Final[str] = "script"
REPORT_SUBDIR: Final[str] = "report"


def current_user() -> str:
    """Return the effective user name (used as a path component)."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):  # pragma: no cover - exotic envs
        return os.environ.get("USER", "unknown")


def user_log_root(log_path_template: str) -> Path:
    """Resolve ``/home/<user>/log`` (or the override template).

    The template may be a relative path, in which case it is resolved
    against the user's home directory.  The literal token ``{user}`` is
    replaced with the current user name so config files can write
    e.g. ``/var/log/{user}`` without hard-coding a user.
    """
    template = log_path_template.format(user=current_user())
    p = Path(template).expanduser()
    if not p.is_absolute():
        p = Path.home() / p
    return p


def serial_number() -> str:
    """Best-effort chassis serial number.

    Prefers ``dmidecode -s system-serial-number`` (Linux), falls back to
    the hostname when dmidecode is missing or returns empty.
    """
    if shutil.which("dmidecode") is None:
        return _hostname_fallback()
    try:
        out = subprocess_run_capture(["dmidecode", "-s", "system-serial-number"])
    except (FileNotFoundError, PermissionError, OSError):
        return _hostname_fallback()
    cleaned = out.strip()
    if not cleaned or cleaned.lower() in {"to be filled by o.e.m.", "default string", "none"}:
        return _hostname_fallback()
    # Serial numbers may contain spaces or slashes; sanitise for path use.
    return re.sub(r"[^A-Za-z0-9_.-]", "_", cleaned)


def _hostname_fallback() -> str:
    return os.uname().nodename if hasattr(os, "uname") else "unknown"


def subprocess_run_capture(argv: list[str], *, timeout: float = 5.0) -> str:
    """Run a command and return stdout (sync helper used by path code)."""
    import subprocess

    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return ""
    return result.stdout


def timestamp_dir() -> str:
    """Return the current time bucket string (``YYYY-MM-DD-HH``)."""
    return time.strftime(_TIMESTAMP_FMT, time.localtime())


@dataclass(frozen=True)
class LogPaths:
    """Resolved filesystem layout for one run of negpu on one machine.

    Instances are immutable; rebuild with ``LogPaths.for_session()`` if the
    time bucket needs to roll over (e.g. when the menu stays open across
    midnight).
    """

    user: str
    sn: str
    timestamp: str
    log_path_template: str
    _root: Path = field(init=False)

    def __post_init__(self) -> None:
        base = user_log_root(self.log_path_template)
        object.__setattr__(self, "_root", base / self.sn / self.timestamp)
        # Make sure all sub-dirs exist. ``mkdir -p`` semantics.
        for sub in (SYSTEM_SUBDIR, RUN_SUBDIR, SCRIPT_SUBDIR, REPORT_SUBDIR):
            (self._root / sub).mkdir(parents=True, exist_ok=True)

    # ---- convenience accessors ----

    @property
    def root(self) -> Path:
        return self._root

    @property
    def system(self) -> Path:
        return self._root / SYSTEM_SUBDIR

    @property
    def run(self) -> Path:
        return self._root / RUN_SUBDIR

    @property
    def script(self) -> Path:
        return self._root / SCRIPT_SUBDIR

    @property
    def report(self) -> Path:
        return self._root / REPORT_SUBDIR

    @property
    def time_5_log(self) -> Path:
        return self._root / "time_5_save_info.log"

    # ---- factory ----

    @classmethod
    def for_session(cls, log_path_template: str, *, sn: str | None = None) -> "LogPaths":
        return cls(
            user=current_user(),
            sn=sn or serial_number(),
            timestamp=timestamp_dir(),
            log_path_template=log_path_template,
        )

    # ---- dunder ----

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return str(self._root)


# Re-export the asyncio event loop policy for callers that want a single
# way to obtain the loop.
def running_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()