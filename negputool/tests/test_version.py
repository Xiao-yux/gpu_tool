"""Smoke tests for negpu._version and the package's public surface."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import negpu
from negpu._version import __version__

_PEP440 = re.compile(
    r"^\d+(\.\d+){0,2}"
    r"(?:(a|b|rc)\d+)?"
    r"(\.post\d+)?"
    r"(\.dev\d+)?$",
    re.IGNORECASE,
)


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_version_is_dev() -> None:
    # Phase 1 ships only a 0.1.0.dev0 tag; adjust when we cut 0.1.0.
    assert __version__.startswith("0.1.0")


def test_version_is_pep440_compliant() -> None:
    # PEP 440 format (avoid extra dep on the `packaging` library).
    assert _PEP440.match(__version__), f"version {__version__!r} is not PEP 440"


def test_package_exports_version() -> None:
    assert negpu.__version__ == __version__
    assert "__version__" in negpu.__all__


def test_package_has_py_typed_marker() -> None:
    # PEP 561: ships type info to type checkers.
    marker = Path(negpu.__file__).parent / "py.typed"
    assert marker.is_file(), f"py.typed missing at {marker!r}"


def test_i18n_locales_exist() -> None:
    locales_dir = Path(negpu.__file__).parent / "i18n" / "locales"
    assert (locales_dir / "en.json").is_file()
    assert (locales_dir / "zh_CN.json").is_file()


def test_locale_files_are_valid_json() -> None:
    locales_dir = Path(negpu.__file__).parent / "i18n" / "locales"
    for f in locales_dir.glob("*.json"):
        payload = json.loads(f.read_text(encoding="utf-8"))
        assert "_meta" in payload
        assert "language" in payload["_meta"]


def test_package_name_is_negpu() -> None:
    # Used by docs / packaging.
    assert re.fullmatch(r"[a-z0-9_\-]+", negpu.__name__.split(".")[0])


def test_all_subpackages_importable() -> None:
    # Sub-packages exist as directories with __init__.py, even if empty.
    for sub in (
        "config",
        "log",
        "i18n",
        "runner",
        "cases",
        "plugins",
        "report",
        "menu",
        "tools",
        "install",
        "wsclient",
        "autotest",
    ):
        assert (Path(negpu.__file__).parent / sub / "__init__.py").is_file(), (
            f"missing sub-package: negpu.{sub}"
        )
        assert sub in os.listdir(Path(negpu.__file__).parent)