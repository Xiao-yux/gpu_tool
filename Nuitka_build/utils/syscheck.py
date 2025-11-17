import os
class CheckSystem:
    def __init__(self,config):
        self.check = True
        self.log = config.log
        self.path = config.get_config_value("CONFIG")
        self.tool = config.tool
        self.printlog("开始检查系统环境","system_check")
        self.check_system()

    def check_system(self):
        '''检查系统环境'''
        self.is_gpu_available()
        g=0
        if self.check_gpu():
            g=1
        self.tool.async_run(self.sys_save(GPU=g))
        return True
    def check_ipmi(self) -> bool:
        '''检查ipmi是否安装'''
        if os.path.exists('/usr/bin/ipmitool'):
            return True
        else:
            return False
    def check_gpu(self) -> bool:
        '''检查gpu是否安装'''
        if not os.popen("lspci | grep -i nvidia").read():
            return False
        else:
            return True
    def check_nvswitch(self) -> bool:
        '''检查nvswitch是否安装'''
        if os.path.exists('/usr/bin/nvidia-smi nvlink --status'):
            return True
        else:
            return False

    def is_gpu_available(self):
        """检查系统"""
        g=1
       
        if not os.popen("lspci | grep -i nvidia").read():
            self.printlog("未检测到 NVIDIA GPU，部分功能将不可用")
            self.printlog(f"总线下显卡信息:{os.popen('lspci | grep -i nvidia').read()}",isprint=False)
            g=0
            
        if not os.path.exists("/usr/bin/nvidia-smi"):
            self.printlog("未检测到 NVIDIA 驱动，部分功能将不可用")
            g=0
        elif g==1:
            self.printlog("检测到 NVIDIA 驱动，开启持久化模式")
            self.tool.run_command("nvidia-smi -pm 1")
            
        
        #检测gpuburn
        
        if not os.path.exists(f"{self.path['gpu_burn_path']}/{self.path['gpu_burn_exe']}"):
            self.printlog(f"未检测到 {self.path['gpu_burn_path']}/{self.path['gpu_burn_exe']}，请确保已正确安装 GPU Burn，GPU Burn 测试功能将不可用")
        #检测nccl
        if not os.path.exists(f"{self.path['nccl_path']}/{self.path['nccl_exe']}"):
            self.printlog(f"未检测到 {self.path['nccl_path']}/{self.path['nccl_exe']}，请确保已正确安装 NCCL，NCCL 测试功能将不可用")
        #检测fieldiag
        if not os.path.exists(f"{self.path['fd_path']}/{self.path['fd_exe']}"):
            self.printlog(f"未检测到 {self.path['fd_path']}/{self.path['fd_exe']}，请确保已正确安装 FieldDiag，FieldDiag 测试功能将不可用")
        #检测dcgmi
        if not os.path.exists("/usr/bin/dcgmi"):
            self.printlog("未检测到 dcgmi，请确保已正确安装 DCGM，DCGM 测试功能将不可用")
        #检测nccllib
        if not os.popen("dpkg -l | grep -i libnccl2").read():
            self.printlog("未检测到 libnccl2，请确保已正确安装 NCCLlib，NCCL 测试功能将不可用")
        if not os.popen("dpkg -l | grep -i libnccl-dev").read():
            self.printlog("未检测到 libnccl-dev，请确保已正确安装 NCCLlib，NCCL 测试功能将不可用")
        
    def sys_save(self,GPU=0):
        """收集系统信息"""
        a = self.log.create_log_file("system_info.log")
        self.log.msg(self.tool.get_sys_info(), logger_name=a)
        self.log.msg(self.tool.get_eth_info(), logger_name=a)
        if GPU==1:
            self.log.msg(self.tool.get_gpu_info(), logger_name=a)
            self.log.msg(self.tool.run_command("nvidia-smi -q"), logger_name=self.log.create_log_file("nvidia-smi","system"))
        
        self.log.msg(self.tool.run_command("lspci -vvv"), logger_name=self.log.create_log_file("lspci","system"))
        self.log.msg(self.tool.run_command("lscpu"), logger_name=self.log.create_log_file("lscpu","system"))
        self.log.msg(self.tool.run_command("lsusb"), logger_name=self.log.create_log_file("lsusb","system"))
        self.log.msg(self.tool.run_command("dmidecode"), logger_name=self.log.create_log_file("dmidecode","system"))
        self.log.msg(self.tool.run_command("lshw"), logger_name=self.log.create_log_file("lshw","system"))
    def printlog(self,message,logname="system_check",path="system_check",isprint=True):
        '''打印日志,同时输出到控制台'''
        self.log.msg(message,logger_name=self.log.create_log_file(logname,path))
        if isprint:
            print(message)