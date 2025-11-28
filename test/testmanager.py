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
        self.functions = []

    def add(self, func):
        """添加一个函数到管理列表中"""
        if callable(func):
            self.functions.append(func)
            print(f"函数 {func.__name__} 已添加")
        else:
            print("添加失败：参数必须是可调用的函数")

    def delete(self, func):
        """从管理列表中删除指定的函数"""
        if func in self.functions:
            self.functions.remove(func)
            print(f"函数 {func.__name__} 已删除")
        else:
            print(f"删除失败：函数 {func.__name__} 不在列表中")

    def run(self):
        """按顺序运行所有添加的函数，并使用printf同时输出"""
        print("开始运行所有函数...")
        for func in self.functions:
            print(f"运行函数: {func.__name__}")
            func()
        print("所有函数运行完毕。")
