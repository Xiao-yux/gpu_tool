from gpu_tool.core.config import get_config, Config
from gpu_tool.menu.menu import Menu
from gpu_tool.utils.command import GpuToolApi
from gpu_tool.utils.check_and_save_system import CheckSystem
from noneprompt import CancelledError
import sys
import os
import threading
from asyncio import CancelledError
from gpu_tool.utils.wscline import Cline
from gpu_tool.core.i18n import init_i18n


def is_root():
    if os.popen("whoami").read().strip() == "root":
        return True
    else:
        print("需要root执行")
        sys.exit(0)


class Core:
    def __init__(self):
        is_root()
        self.config = get_config()
        # 初始化国际化
        language = self.config.get('LANGUAGE', {}).get('language', 'auto')
        self.i18n = init_i18n(language)
        # 初始化全局日志实例
        from gpu_tool.core.log import init_logger
        self.log = init_logger(self.config['LOG'])
        self.log.msg('Core initialized.§§')
        self.wscline = Cline(self.config['UPDATE']['wsurl'])
        if self.config['UPDATE']['wsenable']:
            self.wscline.start()
        GpuToolApi(self.config['version'])
        # CheckSystem(self.config['PATH'], self.i18n)
        self.log.msg(f'{self.i18n.get("LOG_PATH", "Log path")}: {self.log.get_log_file()}',outconsole=True)
        # self.menu = Menu(self.config['PATH'], self.i18n)
        
        if self.config['SYSTEM']['lto']:
            def menu_wrapper(self_ref):
                menu = Menu(self_ref.config['PATH'], self_ref.i18n)
                self_ref.menu = menu
                return menu
            self.tmp_menu = threading.Thread(target=menu_wrapper, args=(self,))
            self.tmp_check = threading.Thread(target=CheckSystem, args=(self.config['PATH'], self.i18n))
            self.tmp_menu.start()
            self.tmp_check.start()
        else:
            CheckSystem(self.config['PATH'], self.i18n)
            self.menu = Menu(self.config['PATH'], self.i18n)
            

        


    def run(self):
        try:
            # 等待Menu线程完成,获取Menu实例
            if self.config['SYSTEM']['lto']:
                self.tmp_menu.join()
                self.tmp_check.join()
            if self.menu is None:
                self.log.msg('菜单初始化失败，无法加载主菜单。', outconsole=True)
                sys.exit(1)
            self.menu.main_menu()
        except CancelledError:
            self.log.msg('用户取消了操作，程序退出。', outconsole=True)
            sys.exit(0)
        except KeyboardInterrupt:
            self.log.msg('程序被用户中断，退出。', outconsole=True)
            sys.exit(0)
        finally:
            sys.exit(0)

