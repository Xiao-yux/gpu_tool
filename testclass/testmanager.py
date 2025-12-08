import inspect
from typing import List

from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from utils.tool import Tools
from core.log import Log
from testclass.testfun import TestFun
from testclass.testclass import Test

class Manager:
    def __init__(self,log:Log,path):

        self.menu = MenuChess()
        self.tool = Tools()
        self.path = path
        self.testfunc = TestFun(path,log)
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
        if self.functions is None or len(self.functions) == 0:
            return
        print("开始运行所有函数...")
        for func in self.functions:
            print(f"运行函数: {func.__name__}")
            func()
        print("所有函数运行完毕。")

    def runmenu(self):
        chin = self.menu.aotu_test_menu
        p = ListPrompt("请选择:",chin).prompt()
        if p.data == "exit" :
            return
        if p.data == "1":
            self.functions = self.testfunc.test1()
        if p.data == "2":
            self.functions = self.testfunc.test2()
        if p.data == "3" :
            self.testarg()
        self.run()
    def testarg(self):
        exclude = {'run_command', '__init__','test1','test2'}
        choices : List[Choice] = []
        for name, method in inspect.getmembers(self.testfunc,
                                               predicate=inspect.ismethod):
            # 2. 通过 __func__ 取到原始函数对象
            func = method.__func__
            if (func.__qualname__.startswith(type(self.testfunc).__name__ + '.')
                    and name not in exclude):
                doc = inspect.getdoc(func) or name
                choices.append(Choice(doc, method))  # 返回值用绑定方法，直接可调用

        if not choices:
            print('没有可调用的方法！')
            return
        p = CheckboxPrompt("请选择:", choices).prompt()
        for i in p:
            self.functions.append(i.data)



if __name__ == "__main__":
    Tools.show_methods(TestFun)