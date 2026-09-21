from utils.tool import Tools
from runner.local import run_command


def get_gpumemory_bandwidth():
    nvvs_path = "/var/log/nvidia-dcgm/nvvs.log"
    #删除nvvs.log文件
    run_command("rm -f " + nvvs_path)
    #开始测试
    run_command("dcgmi diag -r memory_bandwidth")
    str = run_command(f"cat {nvvs_path} | grep 'Test memory_bandwidth:'")
    return str