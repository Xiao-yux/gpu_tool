import sys
import time
import threading
from typing import Optional


class Colors:
    """终端颜色常量类"""
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

class SingleLineDisplay:
    """
    终端单行显示文字模块

    功能：
    - 初始化时传入一个字符串
    - 更新显示的文字
    - 追加显示的文字
    - 关闭显示
    - 打开显示
    - 设置文字颜色（默认为蓝色）
    """

    def __init__(self, initial_text: str = "", show: bool = True, color: str = Colors.BLUE):
        """
        初始化单行显示

        Args:
            initial_text: 初始显示的文字
            show: 是否立即显示
            color: 文字颜色，默认为蓝色
        """
        self.text = initial_text
        self.visible = show
        self.color = color
        self.lock = threading.Lock()
        self._last_length = 0

        if show:
            self._show()

    def update(self, new_text: str, show: Optional[bool] = None):
        """
        更新显示的文字

        Args:
            new_text: 新的文字内容
            show: 是否显示，None表示保持当前显示状态
        """
        with self.lock:
            self.text = new_text
            if show is not None:
                self.visible = show

            if self.visible:
                self._show()
            else:
                self._clear()

    def append(self, text_to_append: str, separator: str = " ", show: Optional[bool] = None):
        """
        追加文字到当前显示内容

        Args:
            text_to_append: 要追加的文字
            separator: 追加时使用的分隔符
            show: 是否显示，None表示保持当前显示状态
        """
        with self.lock:
            if self.text:
                self.text += separator + text_to_append
            else:
                self.text = text_to_append

            if show is not None:
                self.visible = show

            if self.visible:
                self._show()
            else:
                self._clear()

    def show(self):
        """打开显示"""
        with self.lock:
            self.visible = True
            self._show()

    def hide(self):
        """关闭显示"""
        with self.lock:
            self.visible = False
            self._clear()
    
    def set_color(self, color: str):
        """
        设置文字颜色
        
        Args:
            color: 颜色字符串，使用Colors类中的常量
        """
        with self.lock:
            self.color = color
            if self.visible:
                self._show()

    def _show(self):
        """内部方法：显示当前文字"""
        # 清除当前行
        sys.stdout.write("\r\033[K")

        # 替换文本中的换行符为空格，避免实际换行
        display_text = self.text
        
        # 应用颜色并显示新内容
        sys.stdout.write(f"{self.color}{display_text}{Colors.RESET}")

        # 填充剩余空间以确保清除整行
        remaining = max(0, self._last_length - len(self.text))
        sys.stdout.write(" " * remaining)

        # 保存当前长度以便下次清除
        self._last_length = len(display_text)

        # 确保立即刷新输出
        sys.stdout.flush()

    def _clear(self):
        """内部方法：清除当前行"""
        sys.stdout.write("\r\033[K")
        self._last_length = 0
        sys.stdout.flush()

    def __del__(self):
        """析构函数：确保在对象销毁时清除显示"""
        self._clear()

if __name__ == "__main__":
    # 示例用法
    print("测试")
    time.sleep(1)
    print("\b\b\a测试\b\b")
