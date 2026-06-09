"""negpu.config.model - pydantic v2 configuration models.

The on-disk TOML has lowercase sections and snake_case fields:

.. code-block:: toml

    version = "0.1.0"

    [language]
    language = "auto"

    [paths]
    fd_path = "/home/{user}/fd-40946"
    ...

Dynamic placeholders such as ``{user}`` are **not** resolved by pydantic;
see :mod:`negpu.config.loader` for the one-shot rendering that happens
when the default config is first copied to ``/etc/negpu/config.toml``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Section models
# ---------------------------------------------------------------------------


class PathConfig(BaseModel):
    """Filesystem locations of external test tools.

    Defaults assume the user has the binaries somewhere under
    ``/home/$USER/`` and that the package's ``bash/`` data dir was
    installed to ``/usr/local/share/negpu/bash``.
    """

    model_config = ConfigDict(extra="ignore")

    config_file: str = "/etc/negpu/config.toml"
    fd_path: str = "/home/{user}/fd-40946"
    gpu_burn_path: str = "/home/{user}/gpu-burn"
    nccl_path: str = "/home/{user}/nccl-tests/build"
    download: str = "/home/{user}"
    fd_exe: str = "fieldiag.sh"
    gpu_burn_exe: str = "gpu_burn"
    nccl_exe: str = "all_reduce_perf"
    bash_dir: str = "/usr/local/share/negpu/bash"


class LanguageConfig(BaseModel):
    """i18n settings."""

    model_config = ConfigDict(extra="ignore")

    language: str = "auto"  # auto | en | zh_CN


class SystemConfig(BaseModel):
    """System-level toggles (root check, parallel init, etc.)."""

    model_config = ConfigDict(extra="ignore")

    lto: bool = True  # parallel init in Core.__init__
    root_required: bool = True
    bypass_root_check: bool = False


class UpdateConfig(BaseModel):
    """WebSocket / auto-update settings.

    Note: ``wsenable`` defaults to ``False`` per REFACTORING_TASK [F]1;
    the WS client will not start unless this is flipped to ``True`` in
    the user's config (typically after the webserver is rewritten).
    """

    model_config = ConfigDict(extra="ignore")

    wsenable: bool = False
    wsurl: str = "ws://127.0.0.1:8765"


class LogConfig(BaseModel):
    """Logging directory + format settings."""

    model_config = ConfigDict(extra="ignore")

    log_path: str = "/home/{user}/log"
    log_file: str = "negpu_debug.log"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    console_output: bool = False


# ---------------------------------------------------------------------------
# Top-level model
# ---------------------------------------------------------------------------


class NegpuConfig(BaseModel):
    """The whole negpu configuration."""

    model_config = ConfigDict(extra="ignore")

    version: str = "0.1.0"
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    update: UpdateConfig = Field(default_factory=UpdateConfig)
    log: LogConfig = Field(default_factory=LogConfig)

    # ---- helpers ----

    def with_overrides(self, **overrides: object) -> "NegpuConfig":
        """Return a shallow copy with the given fields replaced.

        >>> c = NegpuConfig().with_overrides(log=LogConfig(log_level="DEBUG"))
        >>> c.log.log_level
        'DEBUG'
        """
        data = self.model_dump()
        for k, v in overrides.items():
            if "." in k:
                # dotted path: "log.log_level" -> {"log": {"log_level": v}}
                head, tail = k.split(".", 1)
                data.setdefault(head, {})[tail] = v
            else:
                data[k] = v
        return NegpuConfig.model_validate(data)