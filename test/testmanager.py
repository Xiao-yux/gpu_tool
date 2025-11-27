import subprocess
from typing import Dict, List
import json
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from utils.tool import Tools
from core.log import Log

class Manager:
    def __init__(self,log:Log):
        self.menu = MenuChess()
        self.tool = Tools()
        self.log = log