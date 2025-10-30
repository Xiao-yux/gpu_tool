import os


class Update:
    def __init__(self,config):
        self.config = config
        # print(self.config.get_config_value('CONFIG')['version'])
    def update(self):
        oldven = self.config.get_config_value('CONFIG')['version']