"""negpu.i18n - JSON-based locale loader.

A minimal, no-deps i18n helper. Translation files are flat JSON
dictionaries in :mod:`negpu.i18n.locales`. Keys are looked up with
**dot notation** (e.g. ``"menu.main_title"``) and a fallback value is
returned when a key is missing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Final

_LOCALES_DIR: Final[Path] = Path(__file__).parent / "locales"
_FALLBACK_LANG: Final[str] = "en"


def detect_locale(requested: str = "auto") -> str:
    """Resolve a locale string.

    Resolution order (per REFACTORING_TASK [8]A):

    1. If ``requested`` is not ``"auto"`` → return it directly.
    2. Otherwise look at the ``LANG`` environment variable.
    3. Fall back to English.
    """
    if requested and requested != "auto":
        return requested
    env = os.environ.get("LANG", "")
    env_low = env.lower()
    if env_low.startswith("zh"):
        return "zh_CN"
    if env_low.startswith("en"):
        return "en"
    return _FALLBACK_LANG


class I18n:
    """Lightweight in-memory translation helper.

    >>> i = I18n("en")
    >>> i.get("menu.main_title", "DEFAULT")
    'Please select an action:'
    >>> i.get("nonexistent.key", "fallback")
    'fallback'
    """

    __slots__ = ("language", "_strings", "_requested")

    def __init__(self, language: str = "auto") -> None:
        self._requested = language
        self.language = detect_locale(language)
        self._strings: dict[str, Any] = self._load(self.language)

    # ---- public API ----

    def get(self, key: str, default: str = "") -> str:
        """Look up a dot-separated key, returning ``default`` on miss."""
        cur: Any = self._strings
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return str(cur) if cur else default

    def available_languages(self) -> list[str]:
        """Return the list of language codes shipped with the package."""
        if not _LOCALES_DIR.is_dir():
            return []
        return sorted(p.stem for p in _LOCALES_DIR.glob("*.json"))

    def reload(self) -> None:
        """Re-read the locale file (useful after the user edits JSON)."""
        self.language = detect_locale(self._requested)
        self._strings = self._load(self.language)

    # ---- internals ----

    @staticmethod
    def _load(language: str) -> dict[str, Any]:
        """Try the requested language, then fall back to English."""
        for name in (f"{language}.json", f"{_FALLBACK_LANG}.json"):
            f = _LOCALES_DIR / name
            if f.is_file():
                try:
                    return json.loads(f.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
        return {}


# Module-level convenience ---------------------------------------------------

_default: I18n | None = None


def get_i18n() -> I18n:
    """Return a lazily-created default :class:`I18n` (``auto`` mode)."""
    global _default
    if _default is None:
        _default = I18n("auto")
    return _default