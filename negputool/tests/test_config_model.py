"""Tests for negpu.config.model (pydantic v2 models)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from negpu.config.model import (
    LanguageConfig,
    LogConfig,
    NegpuConfig,
    PathConfig,
    SystemConfig,
    UpdateConfig,
)


def test_default_negpu_config_has_all_sections() -> None:
    c = NegpuConfig()
    assert c.language.language == "auto"
    assert c.paths.fd_path == "/home/{user}/fd-40946"
    assert c.system.lto is True
    assert c.update.wsenable is False
    assert c.log.log_level == "INFO"


def test_path_config_does_not_have_main_file() -> None:
    """P0 user requirement: no main_file field (program install path)."""
    assert "main_file" not in PathConfig.model_fields
    assert "main_file" not in NegpuConfig().paths.model_dump()


def test_log_level_is_validated() -> None:
    with pytest.raises(ValidationError):
        LogConfig(log_level="VERBOSE")  # type: ignore[arg-type]


def test_log_level_accepts_valid_values() -> None:
    for lvl in ("DEBUG", "INFO", "WARNING", "ERROR"):
        c = LogConfig(log_level=lvl)  # type: ignore[arg-type]
        assert c.log_level == lvl


def test_with_overrides_replaces_top_level_field() -> None:
    c = NegpuConfig().with_overrides(version="9.9.9")
    assert c.version == "9.9.9"
    # other fields unchanged
    assert c.log.log_level == "INFO"


def test_with_overrides_replaces_dotted_path() -> None:
    c = NegpuConfig().with_overrides(**{"log.log_level": "DEBUG"})
    assert c.log.log_level == "DEBUG"


def test_with_overrides_replaces_full_section() -> None:
    new_log = LogConfig(log_level="ERROR", console_output=True)
    c = NegpuConfig().with_overrides(log=new_log)
    assert c.log.log_level == "ERROR"
    assert c.log.console_output is True


def test_extra_keys_are_ignored() -> None:
    """Per pydantic config, unknown fields are silently dropped."""
    raw = {
        "version": "1.0.0",
        "language": {"language": "en", "extra_unknown": 42},
    }
    c = NegpuConfig.model_validate(raw)
    assert c.language.language == "en"


def test_sub_models_instantiable_independently() -> None:
    assert LanguageConfig(language="zh_CN").language == "zh_CN"
    assert SystemConfig(lto=False).lto is False
    assert UpdateConfig(wsenable=True).wsenable is True


def test_negpu_config_dump_round_trip() -> None:
    original = NegpuConfig()
    dumped = original.model_dump()
    reloaded = NegpuConfig.model_validate(dumped)
    assert reloaded == original