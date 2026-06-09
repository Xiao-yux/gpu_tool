"""negpu.log.filter - control-character & noise filters.

Two layers:

* :func:`clean` — strip backspaces and trailing newline noise; applied
  to **every** log line before write.
* :func:`is_memtester_noise` / :func:`is_progress_noise` / :func:`is_blank` —
  predicate filters applied to specific loggers that are known to emit
  useless updates (memtester progress, spinning cursors, blank rows).

Per REFACTORING_TASK [11]B, the noise set is the original 5 classes
(``\\\\ / - | setting testing``) **plus** progress bars and blank
lines.
"""

from __future__ import annotations

import re
from typing import Final

# Memtester's "spinner" + state-change noise (5 classes from the original
# gpu_tool plus a few more, see REFACTORING_TASK [11]B).
_MEMTESTER_NOISE: Final[re.Pattern[str]] = re.compile(
    r"^(?:[\\/\-|]|setting\b|testing\b)\s*$",
    re.IGNORECASE,
)

# Pure progress bars: dots, stars, dashes, with optional whitespace.
_PROGRESS_NOISE: Final[re.Pattern[str]] = re.compile(r"^[\s.*\-+]+$")

# Backspace + ANSI ESC cluster — used by :func:`clean`.
_BACKSPACE: Final[re.Pattern[str]] = re.compile(r"\x08+")
_ANSI_ESC: Final[re.Pattern[str]] = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def clean(line: str | None) -> str:
    """Sanitise a line for logging.

    * Strips ``\\x08+`` backspace clusters (memtester overwrites).
    * Removes ANSI ESC sequences.
    * Strips trailing ``\\r\\n`` / ``\\n``.
    * Returns ``""`` for ``None``.
    """
    if line is None:
        return ""
    line = _BACKSPACE.sub("", line)
    line = _ANSI_ESC.sub("", line)
    return line.rstrip("\r\n")


def is_memtester_noise(line: str) -> bool:
    """True if ``line`` is a memtester spinner / state line.

    >>> is_memtester_noise("\\")
    True
    >>> is_memtester_noise("|")
    True
    >>> is_memtester_noise("setting")
    True
    >>> is_memtester_noise("testing")
    True
    >>> is_memtester_noise("memtester: passes 0/1")
    False
    """
    return bool(_MEMTESTER_NOISE.match(line.strip()))


def is_progress_noise(line: str) -> bool:
    """True if ``line`` is a progress bar (dots / stars / dashes only)."""
    s = line.strip()
    return bool(s) and bool(_PROGRESS_NOISE.fullmatch(s))


def is_blank(line: str) -> bool:
    """True if ``line`` has no printable characters."""
    return not line.strip()


def should_drop(line: str) -> bool:
    """Convenience: True if the line is any kind of noise we want to skip."""
    return is_memtester_noise(line) or is_progress_noise(line) or is_blank(line)