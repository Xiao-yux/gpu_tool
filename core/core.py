from core.config import Config
from core.log import Log
from menu.menu import Menu
from noneprompt import CancelledError

class Core:
    def __init__(self):
        self.config = Config().config
        self.log = Log(self.config['LOG'])
        self.log.msg('Core initialized.')
        self.menu = Menu(self.config['PATH'], self.log)

    def run(self):
        try:
            self.menu.main_menu()
        except CancelledError:
            self.log.msg('用户取消了操作，程序退出。', outconsole=True)
            exit(0)
        except KeyboardInterrupt:
            self.log.msg('程序被用户中断，退出。', outconsole=True)
            exit(0)

if __name__ == '__main__':
    c = Core()
    print(c.config)