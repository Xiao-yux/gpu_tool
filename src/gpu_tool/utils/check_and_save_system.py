import os
from typing import ClassVar

from utils.tool import Tools
from log.logger import get_logger
from i18n.i18n import get_i18n
from config.model import PathConfig
from runner.local import run_command

class CheckSystem:
    
    DEFAULT_COMMANDS: ClassVar[dict[str, tuple[str, ...]]] = {
        "dmesg": ("dmesg",),
        "nvidia-smi": ("nvidia-smi","-q"),
        "nvidia-smi-nvlink": ("nvidia-smi", "nvlink", "--status"),
        "nvidia-smi-topo": ("nvidia-smi", "topo", "-m"),
        "lspci": ("lspci", "-vvv"),
        "lsblk": ("lsblk", "-O"),
        "lsusb": ("lsusb",),
        "lshw": ("lshw",),
        "dmidecode": ("dmidecode",),
        "ipmitool-lan": ("ipmitool", "lan", "print"),
        "ipmitool-sdr": ("ipmitool", "sdr"),
        "ipmitool-fru": ("ipmitool", "fru"),
    }
    def __init__(self, config: PathConfig):
        self.log = get_logger()
        self.path = config
        self.tool = Tools()
        # 获取i18n实例
        self.i18n = get_i18n()

        self.log.info(self.i18n.get('start_checksys'))
        self.check_system()

    def check_system(self):
        """检查系统环境"""
        self.is_gpu_available()
        g = 0
        if self.check_gpu():
            g = 1
        self.sys_save(GPU=g)
        
        return True

    def check_ipmi(self) -> bool:
        """检查ipmi是否安装"""
        if os.path.exists('/usr/bin/ipmitool'):
            return True
        else:
            return False

    def check_gpu(self) -> bool:
        """检查gpu是否安装"""
        if not os.popen("lspci | grep -i nvidia").read():
            return False
        else:
            return True

    def check_nvswitch(self) -> bool:
        """检查nvswitch是否安装"""
        if os.path.exists('/usr/bin/nvidia-smi nvlink --status'):
            return True
        else:
            return False
    def check_dcgmi(self) -> bool:
        if os.path.exists('/usr/bin/dcgmi'):
            self.log.info(self.i18n.get('no_dcgmi'))
            return True
        else:
            return False
    def is_gpu_available(self):
        """检查系统"""
        g = 1

        if not run_command("lspci | grep -i nvidia"):
            self.log.info(self.i18n.get('no_gpu'),console=True)
            self.log.info(f"GPU Bus Info: {run_command('lspci | grep -i nvidia')}", console=False)
            g = 0

        if not os.path.exists("/usr/bin/nvidia-smi"):
            self.log.info(self.i18n.get('no_nvidia_smi'),console=True)
            g = 0
        elif g == 1:
            self.tool.run_nvidia_service()
            # run_command("nvidia-smi -pm 1")

        # 检测gpuburn

        if not os.path.exists(f"{self.path.gpu_burn_path}/{self.path.gpu_burn_exe}"):
            self.log.info(
                self.i18n.get('no_gpu_burn'),console=True)
        # 检测nccl
        if not os.path.exists(f"{self.path.nccl_path}/{self.path.nccl_exe}"):
            self.log.info(
                self.i18n.get('no_nccl'),console=True)
        # 检测fieldiag
        if not os.path.exists(f"{self.path.fd_path}/{self.path.fd_exe}"):
            self.log.info(
                self.i18n.get('no_fd'),console=True)
        # 检测dcgmi
        if not os.path.exists("/usr/bin/dcgmi"):
            self.log.info(self.i18n.get('no_dcgmi'),console=True)
        # 检测nccllib
        if not run_command("dpkg -l | grep -i libnccl2"):
            self.log.info(self.i18n.get('no_nccl2lib'),console=True)
        if not run_command("dpkg -l | grep -i libnccl-dev"):
            self.log.info(self.i18n.get('no_nccl_dev'),console=True)

    def sys_save(self, GPU=0):
        """收集系统信息"""
        a = "system_info"
        self.log.info(f"{self.i18n.get('gpu_cont')} {self.tool.get_gpu_count()}\n",console=True,file_name=a)
        self.log.info(self.tool.get_sys_info(), file_name=a)
        self.log.info(self.tool.get_eth_info(), file_name=a)
        if GPU == 1:
            self.log.info(self.tool.get_gpu_info(), file_name=a)
        self.save_def_info()
        self.tool.get_nvidia_bug_report(f"{self.log.paths.system}")
    def save_def_info(self):
        """收集系统原始数据 DEFAULT_COMMANDS 内的命令
        """
        for cmd_name, cmd in self.DEFAULT_COMMANDS.items():
            try:
                output = run_command(" ".join(cmd))
                self.log.info(output, file_name=f"system/{cmd_name}")
            except Exception as e:
                self.log.info(f"{self.i18n.get('command_execution_failed').format(' '.join(cmd), e)}", console=True)
        