import inspect
import json
from typing import List
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from utils.tool import Tools,JsonDB
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
        self._resume_file : str ='' # 断点文件路径
        self._prepare_resume_file()
        self.aotojson = JsonDB(self._resume_file,auto_save=True)
        self._rrun()
    def add(self, func):
        """添加一个函数到管理列表中"""
        if callable(func):
            self.functions.append(func)
            self.aotojson.add("todo",func.__name__)
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
            print("自动执行函数列表为空，无事可做。")
            return
        print("开始运行所有函数...")
        for func in self.functions:
            self.aotojson.add("done",func.__name__)
            print(f"运行函数: {func.__name__}")
            func()

        print("所有函数运行完毕。")
        self._clean_checkpoint()


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
            self.add(i.data)

        targets = {self.testfunc.fieldiag_level1, self.testfunc.fieldiag_level2}

        idx = next((i for i, f in enumerate(self.functions) if f in targets), None)

        if idx is not None:  # 确实存在才移动
            func = self.functions.pop(idx)  # 删掉
            self.functions.append(func)  # 放到末尾

# --------------- 内部工具 ---------------
    def _prepare_resume_file(self)->str:
        log_path = self.log.get_log_file(pathtime=False)          # 用户给的日志文件路径
        self._resume_file = log_path + '/resume.json'   # 断点文件
        os.system(f"touch {self._resume_file}")
        return log_path + '/resume.json'

    def _clean_checkpoint(self):
        """全部跑完后删掉断点文件"""
        try:
            if os.path.exists(self._resume_file):
                os.remove(self._resume_file)
        except Exception as e:
            self.log.msg(f"清理断点文件失败: {e}")

    def _if_done(self):
        a= list(self.aotojson.get("todo")-self.aotojson.get("done"))
        if len(a) == 0:
            self._clean_checkpoint()
    def _rrun(self):
        a = self.aotojson.get("logpath")
        if a is None:
            self.aotojson.add("logpath",self.log.get_log_file())

    def _fun_func(self):
        # 计算剩余任务
        todo_set = self._to_set(self.aotojson.get("todo"))
        done_set = self._to_set(self.aotojson.get("done"))
        b = list(todo_set - done_set)
        for i in b:
            if hasattr(self.testfunc,i):
                self.functions.append(getattr(self.testfunc, i))

    @staticmethod
    def _to_set(value):
        if value is None:
            return set()
        if isinstance(value, str):
            return {value}
        if isinstance(value, list):
            return set(value)
        return set(value)

if __name__ == "__main__":
    Tools.show_methods(TestFun)