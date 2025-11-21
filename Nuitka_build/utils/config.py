import sys, pathlib
import toml
import os
import utils.tools as tools
import utils.log as log
from utils.putlin import SingleLineDisplay,Colors
import argparse

config_file= "/etc/gpu_tool/config.toml" #配置文件
main_file = "/usr/local/bin/gpu_tool"  #主程序
class Config:
    """ 创建配置文件"""
    def __init__(self):
        self.tool = tools.Tools()
        self.__config = {}
        self.tmpconfig = self.tool.get_tmp_path() + 'config.toml'
        self.config = config_file
        self.display = SingleLineDisplay("\n", show=True, color=Colors.YELLOW)
        self.load_config() 
        self.check_version()
        self.log = log.Log(self.__config.get('LOG'))
        self.log.msg('配置文件加载完成')
    def load_config(self):
        """ 加载配置文件"""
        self.is_config()
        try:
            with open(self.config, 'r', encoding='utf-8') as f:
                self.__config = toml.load(f)
                self.debug()
        except Exception as e:
            print(e)
    def load_tmp_config(self):
        """ 加载临时配置文件"""
        try:
            with open(self.tmpconfig, 'r', encoding='utf-8') as f:
                self.__oldconfig = toml.load(f)
        except Exception as e:
            print(e)
            
    def parse_arguments(ver=None):
        """
        解析命令行参数。
        """
        s = f'''菜单v{ver}
    项目地址：https://github.com/Xiao-yux/gpu_tool'''
        
        parser = argparse.ArgumentParser(
            description=s,
            formatter_class=argparse.RawDescriptionHelpFormatter  # 保持描述中的换行
        )
        
        # 添加参数
        parser.add_argument('--get_gpu_info', action='store_true', help='获取GPU信息')
        parser.add_argument('--get_sys_info', action='store_true', help='获取CPU和内存信息')
        parser.add_argument('--get_eth_info', action='store_true', help='获取网卡和硬盘信息')
        parser.add_argument('--version', action='version', version=f'{ver}', help='显示版本信息')
        parser.add_argument('--dispname', action='store', help='自定义颜文字')
        
        return parser.parse_args()
    def check_version(self)-> str:
        """ 检测系统下版本号是否最新"""
        self.load_tmp_config()
        executable_path = sys.argv[0]
        executable_name = os.path.basename(executable_path)
        a= self.__config.get('CONFIG')['version']
        
        b = self.__oldconfig.get('CONFIG')['version']
        
        if a != b:
            self.tool.copy_file(self.tmpconfig, config_file)
            
            self.tool.copy_file(self.tool.get_dist_path() + f'{executable_name}', main_file)
            self.load_config() #重新加载配置文件
            return '系统下不是最新版本'

    def is_config(self)-> bool:
        """ 判断配置文件是否存在"""
        # print(self.tool.is_config_path())
        executable_path = sys.argv[0]
        executable_name = os.path.basename(executable_path)
        if self.tool.is_config_path():
            
            return True
        else:
            os.system("mkdir -p /etc/gpu_tool")
            self.tool.copy_file(self.tool.get_dist_path() + f'{executable_name}', main_file)
            self.tool.copy_file(self.tmpconfig, config_file)
            return False
    def get_config_value(self, key: str) -> dict:
        """ 获取配置文件中的值"""
        return self.__config.get(key)
    def debug(self):
        if self.__config.get('CONFIG')['DEBUG']:
            os.system(f"rm {self.config}")
            return True
        else:
            return False
    def return_config(self):
        return self.__config
if __name__ == '__main__':
    a = Config()

    
    
