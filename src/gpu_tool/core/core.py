from config.loader import load
from menu.menu import Menu
from utils.command import GpuToolApi
from utils.check_and_save_system import CheckSystem
from noneprompt import CancelledError
from log.logger import get_logger,init_logger
import sys
import os
import threading
from asyncio import CancelledError
from utils.wscline import Cline
from i18n.i18n import init_i18n


def is_root():
    if os.popen("whoami").read().strip() == "root":
        return True
    else:
        print("需要root执行")
        sys.exit(0)


class Core:
    def __init__(self):
        is_root()
        self.config = load()
        # 初始化国际化
        language = self.config.language.language
        self.i18n = init_i18n()
        # 初始化全局日志实例
        self.log = init_logger(self.config.log)
        self.log.info('Core initialized.§§')
        self.wscline = Cline(self.config.update.wsurl)
        if self.config.update.wsenable:
            self.wscline.start()
        GpuToolApi(self.config.version)
        # CheckSystem(self.config.path, self.i18n)
        self.log.info('系统检查完成。')
        # self.menu = Menu(self.config['PATH'], self.i18n)

        CheckSystem(self.config.paths)
        self.menu = Menu(self.config.paths)
            

        


    def run(self):
        try:
            if self.menu is None:
                self.log.info('菜单初始化失败，无法加载主菜单。', console=True)
                sys.exit(1)
            self.menu.main_menu()
        except CancelledError:
            self.log.info('用户取消了操作，程序退出。', console=True)
            sys.exit(0)
        except KeyboardInterrupt:
            self.log.info('程序被用户中断，退出。', console=True)
            sys.exit(0)
        finally:
            sys.exit(0)

