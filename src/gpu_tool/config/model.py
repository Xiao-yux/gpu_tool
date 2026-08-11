"""gpu.config.model - pydantic v2 configuration models.

The on-disk TOML has lowercase sections and snake_case fields:

.. code-block:: toml

    version = "0.1.0"

    [language]
    language = "auto"

    [paths]
    fd_path = "/home/{user}/fd-40946"
    ...

    [report]
    tester = "operator"


Dynamic placeholders such as ``{user}`` are **not** resolved by pydantic;
see :mod:`gpu.config.loader` for the one-shot rendering that happens
when the default config is first copied to ``/etc/gpu/config.toml``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Section models
# ---------------------------------------------------------------------------


class PathConfig(BaseModel):
    """路径配置
    """

    model_config = ConfigDict(extra="ignore")

    config_file: str = "/etc/gpu_tool/config.toml"   # 配置存放文件路径
    fd_path: str = "/{user}/gpu-tests-tool/fieldiag"          # fieldiag 路径
    gpu_burn_path: str = "/{user}/gpu-tests-tool/gpu-burn"    # gpu_burn 路径
    nccl_path: str = "/{user}/gpu-tests-tool/nccl-tests/build"# nccl-tests 路径
    download: str = "/{user}"                  # 下载路径
    gpu_burn_exe: str = "gpu_burn"                  # gpu_burn 可执行文件名
    nccl_exe: str = "all_reduce_perf"               # nccl-tests 可执行文件名


class LanguageConfig(BaseModel):
    """i18n settings."""

    model_config = ConfigDict(extra="ignore")

    language: str = "auto"  # auto | en | zh_CN


class SystemConfig(BaseModel):
    """System-level toggles (root check, parallel init, etc.)."""

    model_config = ConfigDict(extra="ignore")
    bypass_root_check: bool = True  # 是否检查root


class UpdateConfig(BaseModel):
    """WebSocket / auto-update settings.

    Note: ``wsenable`` defaults to ``False`` per REFACTORING_TASK [F]1;
    the WS client will not start unless this is flipped to ``True`` in
    the user's config (typically after the webserver is rewritten).
    """

    model_config = ConfigDict(extra="ignore")

    wsenable: bool = False
    wsurl: str = "ws://127.0.0.1:8765"  # ws 服务器地址


class LogConfig(BaseModel):
    """Logging directory + format settings."""

    model_config = ConfigDict(extra="ignore")

    log_path: str = "/{user}/log"   # 日志文件夹路径
    log_file: str = "gpu_tool_debug.log"  # 主日志文件名
    console_output: bool = False   # 是否在控制台输出日志


class ReportConfig(BaseModel):
    """报告输出设置
    """

    model_config = ConfigDict(extra="ignore")

    tester: str = ""                         # 测试人 / operator name
    generate_html: bool = True               # 是否生成 HTML 报告
    generate_pdf: bool = True                # 是否生成 PDF 报告
    no_report: bool = False                  # 是否不生成报告（覆盖前两个选项）



class gpuConfig(BaseModel):
    """The whole negpu configuration."""

    model_config = ConfigDict(extra="ignore")

    version: str = "0.1.0"
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    update: UpdateConfig = Field(default_factory=UpdateConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)

    # ---- helpers ----

    def with_overrides(self, **overrides: object) -> gpuConfig:
        """Return a shallow copy with the given fields replaced.

        >>> c = gpuConfig().with_overrides(log=LogConfig(log_level="DEBUG"))
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
        return gpuConfig.model_validate(data)