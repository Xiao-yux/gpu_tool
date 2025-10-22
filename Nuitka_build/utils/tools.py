
import os
import pathlib
import sys
import subprocess

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
    
    def get_pwd(self)-> str:
        '''返回用户当前目录'''
        return os.popen('pwd').read().split('\n')[0]
    def get_serial_number(self):
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()
    def rest_gpu_server(self):
        # 重启GPU服务
        os.popen('systemctl restart nvidia-powerd')
        os.popen('systemctl restart dcgm')
        os.popen('systemctl restart nvidia-fabricmanager')
        os.popen('systemctl restart nvidia-persistenced')
        return True

class checksystem():
    """系统检测"""
    def __init__(self, arg):
       pass

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