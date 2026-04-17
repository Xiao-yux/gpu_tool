from core.config import Config
from menu.menu import Menu
from utils.command import GpuToolApi
from utils.check_and_save_system import CheckSystem
from noneprompt import CancelledError
import sys
import os
import threading
from asyncio import CancelledError
from utils.wscline import Cline
from core.i18n import init_i18n


def is_root():
    if os.popen("whoami").read().strip() == "root":
        return True
    else:
        print("需要root执行")
        sys.exit(0)


class Core:
    def __init__(self):
        is_root()
        self.config = Config().config
        # 初始化国际化
        language = self.config.get('LANGUAGE', {}).get('language', 'auto')
        self.i18n = init_i18n(language)
        # 初始化全局日志实例
        from core.log import init_logger
        self.log = init_logger(self.config['LOG'])
        self.log.msg('Core initialized.§§')
        self.wscline = Cline(self.config['UPDATE']['wsurl'])
        if self.config['UPDATE']['wsenable']:
            self.wscline.start()
        GpuToolApi(self.config['version'])
        self.log.msg(f'{self.i18n.get("LOG_PATH", "Log path:")}: {self.log.get_log_file()}',outconsole=True)
        self.menu = None
        # 将i18n实例传递给Manager
        self._i18n_for_manager = self.i18n
        # 优化加载速度

        # 用于存储线程结果
        self._menu_result = None
        self._check_result = None
        self._check_exception = None
        
        def run_menu():
            try:
                self._menu_result = Menu(self.config['PATH'], self.i18n)
            except Exception as e:
                self._check_exception = e
                raise

        def run_check():
            try:
                self._check_result = CheckSystem(self.config['PATH'], self.i18n)
            except Exception as e:
                self._check_exception = e
                raise
        
        # 创建并启动线程
        
        self._menu_thread = threading.Thread(target=run_menu)
        self._check_thread = threading.Thread(target=run_check)

        self._menu_thread.start()
        self._check_thread.start()
        

        # 3. 保证 run() 之前 CheckSystem 和 TerminalManager 必须完成
        #    这里阻塞一下，异常会原样抛出来
        self._check_thread.join()

        if self._check_exception:
            raise self._check_exception


    def run(self):
        try:
            # 等待Menu线程完成
            self.menu = self._menu_result
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

