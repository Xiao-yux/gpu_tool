#默认配置文件
from typing import Final

DEFAULT_CONFIG: Final[str] ="""\
# gpu_tool configuration
# {user} 为当前用户的用户名 自动获取

version = "{version}"  # _version.py

[language]
language = "zh_cn"            # auto | en | zh_cn

[paths]
config_file  = "/etc/gpu_tool/config.toml"
fd_path      = "/{user}/gpu-tests-tool/fieldiags"
gpu_burn_path = "/{user}/gpu-tests-tool/gpu-burn"
nccl_path    = "/{user}/gpu-tests-tool/nccl-tests/build"
download     = "/{user}/gpu-tests-tool"

gpu_burn_exe = "gpu_burn"
nccl_exe     = "all_reduce_perf"


[system]
bypass_root_check = false

[update]
wsenable = false
wsurl = "ws://127.0.0.1:8765"

[log]
log_path = "/{user}/log"
log_file = "gpu_tool_debug.log"
console_output = false

[report]
tester = "operator"
generate_html = true
generate_pdf = true
no_report = false
"""