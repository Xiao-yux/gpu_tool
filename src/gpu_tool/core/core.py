import sys
import os
import threading



def is_root():
    if os.popen("whoami").read().strip() == "root":
        return True
    else:
        print("需要root执行")
        sys.exit(0)


class Core:
    def __init__(self) -> None:
        pass
    
    def init(self):
        # print("计时开始{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        is_root()

        from config.loader import load
        from i18n.i18n import init_i18n
        from log.logger import init_logger
        from utils.command import GpuToolApi

        self.config = load()
        # 初始化国际化
        # print("config tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        self.i18n = init_i18n()
        
        # 初始化全局日志实例
        # print("i18 tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        self.log = init_logger(self.config.log)
        # print("log tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))

        self.log.info('Core initialized.§§')
        self.log.info(f'版本号:{self.config.version}')
        self.wscline = None
        if self.config.update.wsenable:
            from utils.wscline import Cline
            self.wscline = Cline(self.config.update.wsurl)
            self.wscline.start()
        GpuToolApi()
        # print("api tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))

        self.ch = threading.Thread(target=self._start_system_check, daemon=True)
        self.ch.start()
        self.log.info('系统检查已后台启动。')
        # print("check tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        self.menu = None
        # print("menu tiem:{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))

    def _start_system_check(self):
        from utils.check_and_save_system import CheckSystem
        CheckSystem(self.config.paths)
        self.log.info('系统检查完成。')

        


    def run(self):
        try:
            self.init()
            if self.menu is None:
                from menu.menu import Menu
                self.menu = Menu(self.config.paths)
            if self.menu is None:
                self.log.info('菜单初始化失败，无法加载主菜单。', console=True)
                sys.exit(1)
            self.ch.join()
            self.menu.main_menu()
        except KeyboardInterrupt:
            self.log.info('程序被用户中断，退出。', console=True)
            sys.exit(0)
        finally:
            sys.exit(0)

