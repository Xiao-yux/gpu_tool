
import os
import pathlib
import sys


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
    # 返回GPU数量
        try:
            if not os.path.exists('/usr/bin/nvidia-smi'):
                return 0
                
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=count', '--format=csv,noheader,nounits','| head -n 1'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 尝试将结果转换为整数
            gpu_count = int(result.stdout.strip())
            return gpu_count
            
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            # 如果nvidia-smi失败或输出无法转换为整数，返回0
            return 0
    def copy_file(self, src, dst)-> None:
        '''复制文件'''
        os.system(f'cp {src} {dst}')
    
    def get_gpu_info(self):
        return os.popen(f"bash {self.get_tmp_path()}bash/nvidia_info.sh").read()
    def get_sys_info(self):
        # 返回系统信息
        return os.popen(f'bash {self.get_tmp_path()}bash/sys_info.sh').read()
    def get_eth_info(self):
        # 网卡硬盘信息
        return os.popen(f'bash {self.get_tmp_path()}bash/CX_DISK_INFO.sh').read()
    
    def get_pwd(self)-> str:
        '''返回用户当前目录'''
        return os.popen('pwd').read().split('\n')[0]
    def get_serial_number(self):
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()
    def rest_gpu_server(self):
        # 重启GPU服务
        os.system('systemctl restart nvidia-powerd')
        os.system('systemctl restart dcgm')
        os.system('systemctl restart nvidia-fabricmanager')
        os.system('systemctl restart nvidia-persistenced')
        return True
if __name__ == '__main__':
    tools = Tools()
    print(tools.get_tmp_path())
    print(tools.get_dist_path())
    print(tools.is_config_path())