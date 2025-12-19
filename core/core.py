from __future__ import annotations
from core.config import Config
from core.log import Log
from menu.menu import Menu
from utils.command import GpuToolApi
from utils.check_and_save_system import CheckSystem
from noneprompt import CancelledError
import sys
import concurrent.futures as futures
from asyncio import CancelledError

class Core:
    def __init__(self):
        self.config = Config().config
        self.log = Log(self.config['LOG'])
        self.log.msg('Core initialized.')

        GpuToolApi(self.config['version'])
        self.menu = None
        # 异步执行，优化加载速度

        self._pool = futures.ThreadPoolExecutor(max_workers=2)
        self._menu_future = self._pool.submit(Menu,
                                              self.config['PATH'],
                                              self.log)
        self._check_future = self._pool.submit(CheckSystem,
                                               self.config['PATH'],
                                               self.log)


        # 3. 保证 run() 之前 CheckSystem 必须完成
        #    这里阻塞一下，异常会原样抛出来
        self._check_future.result()


    def run(self):
        try:
            self.menu = self._menu_future.result()
            self.menu.main_menu()
        except CancelledError:
            self.log.msg('用户取消了操作，程序退出。', outconsole=True)
            sys.exit(0)
        except KeyboardInterrupt:
            self.log.msg('程序被用户中断，退出。', outconsole=True)
            sys.exit(0)
        finally:
            sys.exit(0)

if __name__ == '__main__':
    c = Core()