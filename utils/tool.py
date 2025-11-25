import os
import pathlib
import sys
import subprocess
import threading
import time
from noneprompt import Choice
from core.log import Log

class Tools:
    def __init__(self):
        ...

    @staticmethod
    def get_tmp_path() -> str:
        """获取临时目录
        return /usr/***/
        """
        temp_dir = os.path.join(os.path.dirname(__file__))
        a = temp_dir.replace('utils','')
        return a
    @staticmethod
    def get_dist_path() -> str:
        """获取程序所在目录

        """
        return str(pathlib.Path(sys.argv[0]).parent.resolve()) + '/'

    @staticmethod
    def is_config_path() -> bool:
        '''判断配置文件是否存在'''
        config_file= "/etc/gpu_tool/config.toml" #配置文件
        return os.path.exists(config_file)
    @staticmethod
    def get_gpu_count():
        '''返回GPU数量'''

        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("检测不到 nvidia-smi，无法获取 GPU 数量")
            return 0

        if not os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return 0
    @staticmethod
    def async_run(func, *args,daemon: bool = False, **kwargs) -> threading.Thread:
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

    @staticmethod
    def copy_file( src, dst)-> None:
        '''复制文件'''
        os.system(f'cp {src} {dst}')

    def get_gpu_info(self)-> str:
        '''返回GPU信息'''
        return os.popen(f"bash {self.get_tmp_path()}bash/nvidia_info.sh").read()
    def get_sys_info(self) -> str:
        '''# 返回系统信息'''
        return os.popen(f'bash {self.get_tmp_path()}bash/sys_info.sh').read()
    def get_eth_info(self) -> str:
        """# 网卡硬盘信息"""
        return os.popen(f'bash {self.get_tmp_path()}bash/CX_DISK_INFO.sh').read()
    @staticmethod
    def input_chick():
        """输入回车继续"""
        input("按下回车键继续...")
        return
    @staticmethod
    def run_command(command: str) -> str:
        '''执行命令并返回输出'''
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr.strip()}"

    def set_bmc_dhcp(self)-> bool:
        '''设置BMC为DHCP获取IP'''
        self.run_command('ipmitool lan set 1 ipsrc dhcp')

        return True
    @staticmethod
    def get_pwd()-> str:
        '''返回用户当前目录'''
        return os.popen('pwd').read().split('\n')[0]
    @staticmethod
    def get_serial_number():
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()

    @staticmethod
    def rest_gpu_server():
        # 重启GPU服务
        subprocess.run('systemctl restart nvidia-powerd', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-dcgm', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-fabricmanager', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-persistenced', shell=True, check=True)
        return True
    @staticmethod
    def check_fd_path(path):
        """检查目录非空"""
        if os.path.exists(path) and os.listdir(path):
            os.system(f"mv {path} {path}_{time.strftime('%Y-%m-%d-%H-%S', time.localtime())}_bak")
            return True
        return False
    @staticmethod
    def get_gpu_memory():
        """返回GPU显存信息"""
        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("检测不到 nvidia-smi，无法获取 GPU 显存")
            return 0

        if not os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return "NaN"

    @staticmethod
    def fd_arg_chines(chines):
        """fd 选择参数解析"""
        cmd = f"--test="
        for i in chines:
            cmd += i.data + ","
        cmd = cmd[:-1]  # 去除最后一个逗号
        return cmd
    @staticmethod
    def get_bash_path():
        """获取bash路径"""
        return f"{str(pathlib.Path(sys.argv[0]).parent.resolve())}"+ "/bash/"

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
    def syslogtotty():
        '''重定向系统日志到tty9'''
        subprocess.run('', shell=True, check=True)
    def user():
        '''用户信息'''
        return os.popen('ipmitool user list 1').read()


if __name__ == '__main__':
    tools = Tools()
    print(tools.get_tmp_path())
    print(tools.get_dist_path())
    print(tools.is_config_path())