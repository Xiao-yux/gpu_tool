"""Tests for negpu.config.paths (path resolver + LogPaths)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from negpu.config.paths import (
    LogPaths,
    REPORT_SUBDIR,
    RUN_SUBDIR,
    SCRIPT_SUBDIR,
    SYSTEM_SUBDIR,
    current_user,
    serial_number,
    timestamp_dir,
    user_log_root,
)


# ---------------------------------------------------------------------------
# current_user
# ---------------------------------------------------------------------------


def test_current_user_returns_non_empty_string() -> None:
    u = current_user()
    assert isinstance(u, str)
    assert u


def test_current_user_uses_passwd(monkeypatch: pytest.MonkeyPatch) -> None:
    import getpass
    monkeypatch.setattr(getpass, "getuser", lambda: "alice")
    assert current_user() == "alice"


# ---------------------------------------------------------------------------
# timestamp_dir
# ---------------------------------------------------------------------------


def test_timestamp_dir_format() -> None:
    ts = timestamp_dir()
    # YYYY-MM-DD-HH
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{2}", ts), ts


# ---------------------------------------------------------------------------
# user_log_root
# ---------------------------------------------------------------------------


def test_user_log_root_expands_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("negpu.config.paths.current_user", lambda: "alice")
    root = user_log_root("~/{user}/log")
    assert root == Path("/home/alice/log") or root == Path.home() / "alice" / "log"


def test_user_log_root_substitutes_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("negpu.config.paths.current_user", lambda: "bob")
    root = user_log_root("/var/log/negpu/{user}")
    # The exact representation differs across platforms (Windows adds
    # a drive letter), so we just check the substituted name is present
    # and the path's name component is ``bob``.
    assert "bob" in str(root)
    assert root.name == "bob"
    assert root.parts[-1] == "bob"


# ---------------------------------------------------------------------------
# serial_number
# ---------------------------------------------------------------------------


def test_serial_number_falls_back_to_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("negpu.config.paths.shutil.which", lambda _x: None)
    sn = serial_number()
    # The fallback is the hostname, which is non-empty on any POSIX system.
    assert sn
    assert isinstance(sn, str)


def test_serial_number_sanitises_unsafe_chars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Pretend dmidecode returned a serial with a slash and space
    monkeypatch.setattr("negpu.config.paths.shutil.which", lambda _x: "/bin/yes")
    monkeypatch.setattr(
        "negpu.config.paths.subprocess_run_capture", lambda _a: "  abc/def 123 "
    )
    sn = serial_number()
    assert "/" not in sn
    assert " " not in sn


def test_serial_number_rejects_known_garbage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("negpu.config.paths.shutil.which", lambda _x: "/bin/yes")
    monkeypatch.setattr(
        "negpu.config.paths.subprocess_run_capture", lambda _a: "To be filled by O.E.M."
    )
    sn = serial_number()
    # Should have fallen back to hostname.
    assert sn.lower() != "to be filled by o.e.m."


# ---------------------------------------------------------------------------
# LogPaths
# ---------------------------------------------------------------------------


def test_logpaths_creates_subdirectories(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="SN123")
    assert paths.system.is_dir()
    assert paths.run.is_dir()
    assert paths.script.is_dir()
    assert paths.report.is_dir()


def test_logpaths_root_layout(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="SN123")
    assert paths.root == tmp_path / "SN123" / paths.timestamp


def test_logpaths_subdir_names(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="X")
    assert paths.system.name == SYSTEM_SUBDIR
    assert paths.run.name == RUN_SUBDIR
    assert paths.script.name == SCRIPT_SUBDIR
    assert paths.report.name == REPORT_SUBDIR


def test_logpaths_time_5_log_in_root(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="X")
    assert paths.time_5_log.parent == paths.root


def test_logpaths_is_immutable(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="X")
    with pytest.raises((AttributeError, Exception)):
        paths.user = "other"  # type: ignore[misc]


def test_logpaths_str_returns_root(tmp_path: Path) -> None:
    paths = LogPaths.for_session(str(tmp_path), sn="X")
    assert str(paths) == str(paths.root)