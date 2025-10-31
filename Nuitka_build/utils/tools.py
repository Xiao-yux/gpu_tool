from typing import Callable, Any
import os
import pathlib
import sys
import subprocess
import threading
class Tools:
    def __init__(self):
        ...

    def get_tmp_path(self) -> str:
        '''获取临时目录'''
        temp_dir = os.path.join(os.path.dirname(__file__))
        a = temp_dir.replace('utils','')
        return a

    def get_dist_path(self) -> str:
        '''获取程序所在目录'''
        return str(pathlib.Path(sys.argv[0]).parent.resolve()) + '/aisuan'
    
    def is_config_path(self) -> bool:
        '''判断配置文件是否存在'''
        config_file= "/etc/aisuan/config.toml" #配置文件
        return os.path.exists(config_file)
    
    def get_gpu_count(self):
        '''返回GPU数量'''

        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("检测不到 nvidia-smi，无法获取 GPU 数量")
            return 0
                
        if not os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return 0

    def async_run(self, func, *args,daemon: bool = False, **kwargs) -> threading.Thread:
        """
    异步运行函数
    
    Args:
        func: 要异步执行的函数
        *args: 函数的位置参数
        daemon: 是否设置为守护线程
        **kwargs: 函数的关键字参数
        
    Returns:
        threading.Thread: 创建的线程对象
    """
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = daemon
        thread.start()
        return thread


    def copy_file(self, src, dst)-> None:
        '''复制文件'''
        os.system(f'cp {src} {dst}')
    
    def get_gpu_info(self)-> str:
        '''返回GPU信息'''
        return os.popen(f"bash {self.get_tmp_path()}bash/nvidia_info.sh").read()
    def get_sys_info(self) -> str:
        '''# 返回系统信息'''
        return os.popen(f'bash {self.get_tmp_path()}bash/sys_info.sh').read()
    def get_eth_info(self) -> str:
        '''# 网卡硬盘信息'''
        return os.popen(f'bash {self.get_tmp_path()}bash/CX_DISK_INFO.sh').read()
    def run_command(self, command: str) -> str:
        '''执行命令并返回输出'''
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr.strip()}"
    def set_bmc_dhcp(self)-> bool:
        '''设置BMC为DHCP获取IP'''
        os.popen('ipmitool lan set 1 ipsrc dhcp').read()
        os.popen('ipmitool lan set 0 ipsrc dhcp').read()
        return True
    def get_pwd(self)-> str:
        '''返回用户当前目录'''
        return os.popen('pwd').read().split('\n')[0]
    def get_serial_number(self):
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()
    def rest_gpu_server(self):
        # 重启GPU服务
        os.system('systemctl restart nvidia-powerd')
        os.system('systemctl restart nvidia-dcgm')
        os.system('systemctl restart nvidia-fabricmanager')
        os.system('systemctl restart nvidia-persistenced')
        return True

class checksystem():
    """系统检测"""
    def __init__(self, arg):
       pass

    def check_ipmi(self) -> bool:
        '''检查ipmi是否安装'''
        if os.path.exists('/usr/bin/ipmitool'):
            return True
        else:
            return False
    def check_gpu(self) -> bool:
        '''检查gpu驱动是否安装'''
        if os.path.exists('/usr/bin/nvidia-smi'):
            return True
        else:
            return False
    def check_nvswitch(self) -> bool:
        '''检查nvswitch是否安装'''
        if os.path.exists('/usr/bin/nvidia-smi nvlink --status'):
            return True
        else:
            return False
class ipmitools():
    """ ipmi相关工具"""
    
    def sdr():
        '''传感器数据'''
        return os.popen('ipmitool sdr').read()
    def fru():
        '''电源信息'''
        return os.popen('ipmitool fru').read()
    def lan():
        '''lan信息'''
        return os.popen('ipmitool lan print').read()
    def user():
        '''用户信息'''
        return os.popen('ipmitool user list 1').read()
if __name__ == '__main__':
    tools = Tools()
    print(tools.get_tmp_path())
    print(tools.get_dist_path())
    print(tools.is_config_path())