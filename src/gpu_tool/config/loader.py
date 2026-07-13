"""config.loader - TOML config loader + first-run install.

Implements REFACTORING_TASK [1]B / [2]C / [4]A / [14]C:

* [1]  Config file is named ``config.toml``.
* [2]  Search order: ``/etc/gpu_tool/config.toml`` → ``~/config.toml`` →
       ``./config.toml`` → ``$gpu_tool_CONFIG``.
* [4]  Version mismatch → deep-merge defaults INTO the user file
       (缺键补默认，旧值保留) so the user's edits are preserved.
* [14]  On the very first run (no ``/etc/gpu_tool/config.toml``) the
       package's built-in :data:`DEFAULT_CONFIG_TEMPLATE` is rendered
       with the current user name and copied to the system path.
       From that point on the system file is the authoritative source
       and dynamic ``{user}`` placeholders are **not** re-evaluated.
"""

from __future__ import annotations
__all__: list[str] = ["load"]
import os
import sys
from pathlib import Path
from typing import Any, Final, cast

# ``tomllib`` is stdlib in Python 3.11+.  For 3.10 we use the
# ``tomli`` backport (already in requirements.txt for py<3.11).
try:
    import tomllib  
except ImportError:  
    import tomli as tomllib  

from _version import __version__
from config.model import gpuConfig
from config.paths import current_user

# ---------------------------------------------------------------------------
# Search paths
# ---------------------------------------------------------------------------

# Per REFACTORING_TASK [2]C
_SEARCH_PATHS: Final[tuple[str, ...]] = (
    "/etc/gpu_tool/config.toml",
    "~/config.toml",
    "./config.toml",
)

# The canonical install location for the first-run copy.
_DEFAULT_INSTALL_PATH: Final[str] = "/etc/gpu_tool/config.toml"


# ---------------------------------------------------------------------------
# Built-in default config (rendered on first run)
# ---------------------------------------------------------------------------

# Note: the ``{user}`` placeholder here is *only* resolved on first-run
# install. Subsequent reads never touch it again.
DEFAULT_CONFIG_TEMPLATE: Final[str] = """\
# gpu_tool configuration
# Auto-generated on first run; edit freely.
# Re-running ``gpu_tool config-install`` will not overwrite your changes.

version = "{version}"

[language]
language = "auto"            # auto | en | zh_CN

[paths]
config_file  = "/etc/gpu_tool/config.toml"
fd_path      = "/home/{user}/fd-40946"
gpu_burn_path = "/home/{user}/gpu-burn"
nccl_path    = "/home/{user}/nccl-tests/build"
download     = "/home/{user}"
fd_exe       = "fieldiag.sh"
gpu_burn_exe = "gpu_burn"
nccl_exe     = "all_reduce_perf"


[system]
bypass_root_check = false

[update]
wsenable = false
wsurl = "ws://127.0.0.1:8765"

[log]
log_path = "/home/{user}/log"
log_file = "gpu_tool_debug.log"
console_output = false

[report]
# Phase 5: report layer settings.
tester = "operator"
generate_html = true
generate_pdf = true
no_report = false

"""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def find_config_file() -> Path | None:
    """Return the first existing config file in the search order.

    Search order (per REFACTORING_TASK [2]C):

    1. ``/etc/gpu_tool/config.toml``
    2. ``~/config.toml``
    3. ``./config.toml``
    4. ``$gpu_tool_CONFIG``  (if set)
    """
    for raw in _SEARCH_PATHS:
        p = Path(raw).expanduser()
        if p.is_file():
            return p
    env = os.environ.get("GPU_TOOL_CONFIG")
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p
    return None


# ---------------------------------------------------------------------------
# Version merge
# ---------------------------------------------------------------------------


def _deep_merge(defaults: dict[str, object], user: dict[str, object]) -> dict[str, object]:
    """
    配置文件合并：用户配置覆盖默认配置，但缺键补默认，且嵌套 dict 也递归合并。
    """
    result: dict[str, object] = dict(defaults)  # start from defaults
    for k, v in user.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(cast(dict[str, object], result[k]), v)
        else:
            result[k] = v
    return result


# ---------------------------------------------------------------------------
# First-run install
# ---------------------------------------------------------------------------


def install_default_config(
    target: str | Path = _DEFAULT_INSTALL_PATH,
    *,
    overwrite: bool = False,
) -> Path:
    """
    target: where to install the default config (default: ``/etc/gpu_tool/config.toml``).
    overwrite: if True, 是否覆盖已存在的文件 (default: False, recommended to avoid clobbering user edits).
    """
    dest = Path(target).expanduser()
    if dest.exists() and not overwrite:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    rendered = DEFAULT_CONFIG_TEMPLATE.format(version=__version__, user=current_user())
    dest.write_text(rendered, encoding="utf-8")
    return dest


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def _read_toml(path: Path) -> dict[str, object]:
    """Read and parse a TOML file, raising on syntax errors."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_config(
    explicit_path: str | Path | None = None,
    *,
    install_if_missing: bool = True,
) -> tuple[gpuConfig, Path]:
    """Load the gpu_tool configuration.

    Returns a ``(config, source_path)`` tuple.  ``source_path`` is the
    file that was actually read; it's ``Path("(defaults)")`` when no
    file was found and built-in defaults were used.

    On Linux, if no config file exists and ``install_if_missing`` is
    True (default), the default config is installed to
    ``/etc/gpu_tool/config.toml`` so the user can edit it next time.
    """
    if explicit_path is not None:
        path = Path(explicit_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"config file not found: {path}")
        raw = _read_toml(path)
        return gpuConfig.model_validate(raw), path

    found = find_config_file()
    if found is not None:
        raw = _read_toml(found)
        # Apply version-aware deep merge: defaults fill in missing keys,
        # the user's values win everywhere else.
        defaults = _default_dump()
        merged = _deep_merge(defaults, raw)  # type: ignore[arg-type]
        return gpuConfig.model_validate(merged), found

    # No config file anywhere.
    if install_if_missing and sys.platform.startswith("linux"):
        try:
            installed = install_default_config()
            raw = _read_toml(installed)
            return gpuConfig.model_validate(raw), installed
        except (PermissionError, OSError):
            # Not root or /etc not writable → silently fall back to in-memory defaults.
            pass

    return gpuConfig(), Path("(defaults)")


def _default_dump() -> dict[str, object]:
    """Dump the built-in :class:`gpuConfig` defaults to a plain dict."""
    return gpuConfig().model_dump()


# Re-export the main entry point under a shorter name for callers.
def load() -> gpuConfig:
    """Convenience wrapper: load the default config and return only the model."""
    cfg, _ = load_config()
    return cfg