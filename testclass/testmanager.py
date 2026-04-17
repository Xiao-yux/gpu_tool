import inspect
from typing import List
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from menu.menuarg_en import MenuChessEn
from utils.tool import Tools,JsonDB
from core.log import get_logger
from testclass.testfun import TestFun
from core.i18n import get_i18n

class Manager:
    def __init__(self,path,i18n=None):
        # 获取i18n实例
        if i18n is None:
            self.i18n = get_i18n()
        else:
            self.i18n = i18n
        
        # 根据语言设置选择合适的菜单
        if self.i18n.language == 'en':
            self.menu = MenuChessEn()
        else:
            self.menu = MenuChess()
        
        self.tool = Tools()
        self.path = path
        self.log = get_logger()
        self.testfunc = TestFun(path)
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
        else:
            print(self.i18n.get('ADD_FAILED', "添加失败"))

    def delete(self, func):
        """从管理列表中删除指定的函数"""
        if func in self.functions:
            self.functions.remove(func)
            print(self.i18n.get('FUNCTION_DELETED', "函数 {} 已删除").format(func.__name__))
        else:
            print(self.i18n.get('DELETE_FAILED', "删除失败：函数 {} 不在列表中").format(func.__name__))

    def run(self):
        """按顺序运行所有添加的函数，并使用printf同时输出"""
        if self.functions is None or len(self.functions) == 0:
            # print(self.i18n.get('FUNCTION_LIST_EMPTY', "函数列表为空，无事可做。"))
            return
        print(self.i18n.get('START_RUNNING_FUNCTIONS', "开始运行所有函数..."))
        for func in self.functions:
            self.aotojson.add("done",func.__name__)
            print(self.i18n.get('RUNNING_FUNCTION', "运行函数: {}").format(func.__name__))
            func()

        print(self.i18n.get('ALL_FUNCTIONS_COMPLETED', "所有函数运行完毕。"))
        self._clean_checkpoint()


    def runmenu(self):
        chin = self.menu.aotu_test_menu
        p = ListPrompt(self.i18n.get('SELECT', "请选择:"),chin).prompt()
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
        exclude = {'run_command', '__init__','test1','test2','nvbandwidth_test'}
        choices : List[Choice] = []
        a: int=0
        for name, method in inspect.getmembers(self.testfunc,
                                               predicate=inspect.ismethod):
            # 2. 通过 __func__ 取到原始函数对象
            func = method.__func__
            if (func.__qualname__.startswith(type(self.testfunc).__name__ + '.')
                    and name not in exclude):
                doc = inspect.getdoc(func) or name
                choices.append(Choice(doc, [method,a]))  # 返回值用绑定方法，直接可调用
                a+=1
        if not choices:
            print(self.i18n.get('NO_METHODS_AVAILABLE', '没有可调用的方法！'))
            return
        a: int =0
        choices.append(Choice(self.i18n.get('EXIT', "退出"),"exit"))
        choices.append(Choice(self.i18n.get('RUN', "运行"),"run"))
        ma = []
        while True:
            p = ListPrompt(self.i18n.get('SELECT_TEST_WITH_SELECTED', "请选择:           已选择:{}").format(ma), choices,default_select=a).prompt()
            print(end="\b")
            if p.data == "exit":
                self.functions=[]
                return
            if p.data == "run":
                self.log.msg(self.i18n.get('ABOUT_TO_EXECUTE', "即将执行:{}").format(self.testfunc.__name__),outconsole=True)
                break
            self.add(p.data[0])
            ma.append(p.name)
            a = int(p.data[1])


        targets = {self.testfunc.fieldiag_level1, self.testfunc.fieldiag_level2}

        idx = next((i for i, f in enumerate(self.functions) if f in targets), None)

        if idx is not None:  # 确实存在才移动
            func = self.functions.pop(idx)  # 删掉
            self.functions.append(func)  # 放到末尾

# --------------- 内部工具 ---------------
    def _get_fun_name(self,name):
        """传入函数名称返回对应函数"""
        if not hasattr(self.testfunc, name):
            raise AttributeError(self.i18n.get('METHOD_NOT_FOUND', '{} 没有方法 {}').format(self.testfunc.__class__.__name__, name))
        return getattr(self.testfunc, name)

    def _prepare_resume_file(self)->str:
        log_path = self.log.get_log_file(pathtime=False)          # 用户给的日志文件路径
        self._resume_file = log_path + '/resume.json'   # 断点文件
        return log_path + '/resume.json'

    def _clean_checkpoint(self):
        """全部跑完后删掉断点文件"""
        try:
            if os.path.exists(self._resume_file):
                os.remove(self._resume_file)
        except Exception as e:
            self.log.msg(self.i18n.get('CLEAN_CHECKPOINT_FAILED', "清理断点文件失败: {}").format(e))

    def _if_done(self):
        a= list(self.aotojson.get("todo")-self.aotojson.get("done"))
        if len(a) == 0:
            self._clean_checkpoint()
    def _rrun(self):
        self.log.set_log_path(self.aotojson.get("log_path"))
        self.log.msg(self.i18n.get('TEST_LOG', "测试log"))
        self.log.msg(self.log.get_log_file())
        self._fun_func()

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