import sys, pathlib
import toml
import os
import utils.tools as tools
import utils.log as log


config_file= "/etc/aisuan/config.toml" #配置文件
main_file = "/usr/local/bin/aisuan"  #主程序
class Config:
    """ 创建配置文件"""
    def __init__(self):
        self.tool = tools.Tools()
        self.__config = {}
        self.tmpconfig = self.tool.get_tmp_path() + '/config.toml'
        self.config = config_file
        self.load_config() 
        self.log = log.Log(self.__config.get('LOG'))
        self.log.msg('配置文件加载完成')
        self.sys_save()
    def load_config(self):
        """ 加载配置文件"""
        self.is_config()
        try:
            with open(self.config, 'r', encoding='utf-8') as f:
                self.__config = toml.load(f)
                self.debug()
        except Exception as e:
            print(e)
    def sys_save(self):
        """收集系统信息"""
        self.log.create_log_file("system_info.log")
        self.log.msg(self.tool.get_sys_info(), logger_name="system_info.log")
        self.log.msg(self.tool.get_eth_info(), logger_name="system_info.log")
        self.log.msg(self.tool.get_gpu_info(), logger_name="system_info.log")
    def is_config(self)-> bool:
        """ 判断配置文件是否存在"""
        # print(self.tool.is_config_path())
        if self.tool.is_config_path():
            
            return True
        else:
            os.system("mkdir -p /etc/aisuan")
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

    
    
