import json
import os
import time

from config.loader import load
from runner.screen import TerminalManager
from runner.local import run_command
from i18n.i18n import get_i18n
from log.logger import get_logger
from utils.tool import Tools


class TestFun:

    def __init__(self):
        self.log = get_logger()
        self.i18n = get_i18n()
        self.tool = Tools()
        self.config = load()
        self.date = self.load_auto_tests()
        
        
    def _load_json(self, path: str) -> dict:
        """加载 JSON 文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_auto_tests(self):
        tmp_path = os.path.join(os.path.dirname(__file__),"tests")
        tmp_path = os.path.join(tmp_path, f"{self.config.paths.tests_file}")
        tests_config = os.path.join(self.config.paths.config_path, f"{self.config.paths.tests_file}")
        if not os.path.exists(tests_config):
            self.log.info(f"自动测试配置文件不存在，尝试从 {tmp_path} 复制到 {tests_config}")
            run_command(f"cp {tmp_path} {tests_config}")
            self.log.info(f"自动测试配置文件已复制到 {tests_config}")
        if os.path.exists(tests_config):
            self.log.info(f"加载自动测试配置文件: {tests_config}")
            return self._load_json(tests_config)
        return {}
    def get_name_test(self, test_name):
        return self.date.get(test_name)