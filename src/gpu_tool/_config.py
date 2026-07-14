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