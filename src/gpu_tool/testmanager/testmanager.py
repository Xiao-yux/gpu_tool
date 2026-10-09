import inspect
import os

from i18n.i18n import get_i18n
from log.logger import get_logger
from noneprompt import Choice, ListPrompt
from testmanager.test_config import TestFun
from utils.tool import Tools


class Manager:
    def __init__(self):
        self.test = TestFun()
    
    