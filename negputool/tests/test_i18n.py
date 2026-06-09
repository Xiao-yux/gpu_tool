"""Tests for negpu.i18n.loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from negpu.i18n.loader import I18n, detect_locale, get_i18n


def test_detect_locale_explicit_zh() -> None:
    assert detect_locale("zh_CN") == "zh_CN"


def test_detect_locale_explicit_en() -> None:
    assert detect_locale("en") == "en"


def test_detect_locale_auto_chinese(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANG", "zh_CN.UTF-8")
    assert detect_locale("auto") == "zh_CN"


def test_detect_locale_auto_english(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert detect_locale("auto") == "en"


def test_detect_locale_auto_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANG", raising=False)
    assert detect_locale("auto") == "en"


def test_i18n_english_loads() -> None:
    i = I18n("en")
    assert i.language == "en"
    assert i.get("menu.main_title")  # non-empty
    assert i.get("menu.exit") == "Exit"


def test_i18n_chinese_loads() -> None:
    i = I18n("zh_CN")
    assert i.language == "zh_CN"
    assert i.get("menu.exit") == "退出"


def test_i18n_unknown_lang_falls_back_to_english() -> None:
    i = I18n("de")  # no de.json
    assert i.language == "de"
    # Falls back to en.json content
    assert i.get("menu.exit") == "Exit"


def test_i18n_get_nested_key() -> None:
    i = I18n("en")
    assert i.get("common.press_enter") == "Press Enter to continue..."


def test_i18n_get_missing_key_returns_default() -> None:
    i = I18n("en")
    assert i.get("nonexistent.key", "fallback") == "fallback"
    assert i.get("nonexistent.key") == ""


def test_i18n_get_partial_path_returns_default() -> None:
    i = I18n("en")
    # "menu" exists but "menu.nonexistent" doesn't
    assert i.get("menu.nonexistent", "X") == "X"


def test_i18n_available_languages() -> None:
    i = I18n("en")
    langs = i.available_languages()
    assert "en" in langs
    assert "zh_CN" in langs


def test_i18n_reload() -> None:
    i = I18n("en")
    assert i.get("menu.exit") == "Exit"
    i.reload()
    assert i.get("menu.exit") == "Exit"


def test_get_i18n_returns_singleton() -> None:
    a = get_i18n()
    b = get_i18n()
    assert a is b