import os


class Update:
    def __init__(self,config):
        self.config = config
    def update(self):
        oldven = self.config.get_config_value('CONFIG')['version']