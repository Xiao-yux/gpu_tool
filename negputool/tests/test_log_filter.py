"""Tests for negpu.log.filter (clean + noise detection)."""

from __future__ import annotations

from negpu.log.filter import (
    clean,
    is_blank,
    is_memtester_noise,
    is_progress_noise,
    should_drop,
)


# ---- clean() ----

def test_clean_strips_trailing_newline() -> None:
    assert clean("hello\n") == "hello"
    assert clean("hello\r\n") == "hello"


def test_clean_strips_backspace_cluster() -> None:
    # ``clean`` only *strips* the backspaces (per the original gpu_tool
    # implementation); it does not simulate cursor movement.  So the
    # original characters remain in the output.
    assert clean("abc\x08\x08\x08") == "abc"
    assert clean("1234\x08\x08\x08") == "1234"
    # Even a single backspace is removed (no chars are deleted, only
    # the backspace byte itself).
    assert clean("hello\x08") == "hello"


def test_clean_strips_ansi_escape() -> None:
    # CSI colour + cursor escape
    assert clean("\x1b[31mred\x1b[0m") == "red"
    assert clean("\x1b[2Jclear") == "clear"


def test_clean_handles_none() -> None:
    assert clean(None) == ""  # type: ignore[arg-type]


def test_clean_preserves_normal_text() -> None:
    assert clean("hello world") == "hello world"
    assert clean("") == ""


# ---- is_memtester_noise() ----

def test_is_memtester_noise_matches_spinner() -> None:
    for s in ("\\", "/", "-", "|"):
        assert is_memtester_noise(s), f"{s!r} should be noise"


def test_is_memtester_noise_matches_state() -> None:
    for s in ("setting", "testing", "Setting", "TESTING"):
        assert is_memtester_noise(s), f"{s!r} should be noise"


def test_is_memtester_noise_does_not_match_real_output() -> None:
    assert not is_memtester_noise("memtester: passes 0/1")
    assert not is_memtester_noise("ok 1 0 0 1 0 0 0 0 0")
    assert not is_memtester_noise("done")


def test_is_memtester_noise_handles_whitespace() -> None:
    assert is_memtester_noise("  \\  ")
    assert is_memtester_noise(" setting ")


# ---- is_progress_noise() ----

def test_is_progress_noise_matches_dots() -> None:
    assert is_progress_noise("...")
    assert is_progress_noise("............")


def test_is_progress_noise_matches_stars() -> None:
    assert is_progress_noise("***")
    assert is_progress_noise("***   ***")  # stars + whitespace
    assert is_progress_noise("   ***   ***   ")


def test_is_progress_noise_does_not_match_text() -> None:
    assert not is_progress_noise("loading")
    assert not is_progress_noise("100%")


def test_is_progress_noise_rejects_empty() -> None:
    assert not is_progress_noise("")


# ---- is_blank() ----

def test_is_blank_matches_empty_and_whitespace() -> None:
    assert is_blank("")
    assert is_blank("   ")
    assert is_blank("\n")
    assert is_blank("\t\t")


def test_is_blank_does_not_match_content() -> None:
    assert not is_blank(".")
    assert not is_blank("a")
    assert not is_blank("  a  ")


# ---- should_drop() ----

def test_should_drop_is_union_of_filters() -> None:
    assert should_drop("\\")
    assert should_drop("setting")
    assert should_drop("...")
    assert should_drop("")
    assert should_drop("   ")


def test_should_drop_keeps_real_lines() -> None:
    assert not should_drop("memtester: passes 1/1")
    assert not should_drop("ok 1 0 0 1 0 0 0 0 0")
    assert not should_drop("GPU 0: 75°C")