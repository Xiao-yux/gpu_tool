import os

import toml
import utils.tool as tool
import core.log as log

class Config:
    def __init__(self):
        self.config = None
        self.load()
        self.check_version()

    path = '/etc/gpu_tool/config.toml'

    def load(self):
        self.check_config()
        if not self.check_config():
            exit(1)
        self.config = toml.load(f'{self.path}')
        return self.config

    def check_config(self):
        if os.path.exists(self.path):
            return True
        else:
            co = tool.Tools.get_tmp_path() + 'config.toml'
            os.system(f'cp {co} {self.path}')
            return False
    def check_version(self):
        """检查配置文件版本"""
        co = tool.Tools.get_tmp_path() + 'config.toml'
        config_tmp = toml.load(f'{co}')
        if self.config['version'] != config_tmp['version']:
            os.system(f'cp {co} {self.path}')
            self.load()
            return True
        return '版本无更新'


if __name__ == '__main__':
    print(tool.Tools.get_tmp_path())
