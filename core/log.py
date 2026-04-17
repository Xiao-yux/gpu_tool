import logging
import os
import re
import time
from functools import wraps
import utils.tool as util

# 全局日志实例
_global_logger = None


def init_logger(logconfig):
    """初始化全局日志实例
    
    Args:
        logconfig: 日志配置字典
    
    Returns:
        Log: 全局日志实例
    """
    global _global_logger
    _global_logger = Log(logconfig)
    return _global_logger


def get_logger():
    """获取全局日志实例
    
    Returns:
        Log: 全局日志实例
    
    Raises:
        RuntimeError: 如果日志未初始化
    """
    if _global_logger is None:
        raise RuntimeError("日志系统未初始化，请先调用 init_logger()")
    return _global_logger


def msg(message, level="INFO", logger_name="gpu_tool_debug", outconsole=False):
    """记录日志的便捷函数
    
    Args:
        message: 日志消息
        level: 日志级别
        logger_name: 日志器名称
        outconsole: 是否输出到控制台
    """
    get_logger().msg(message, level, logger_name, outconsole)


def create_log_file(log_file, path='') -> str:
    """创建新的日志文件的便捷函数
    
    Args:
        log_file: 日志文件名
        path: 日志文件路径
    
    Returns:
        str: 日志器名称
    """
    return get_logger().create_log_file(log_file, path)


def get_log_file(pathtime=True):
    """获取日志文件路径的便捷函数
    
    Args:
        pathtime: 是否返回带日期的路径
    
    Returns:
        str: 日志文件路径
    """
    return get_logger().get_log_file(pathtime)




def log_execution(func):
    """记录函数执行的装饰器
    
    Args:
        func: 被装饰的函数
    
    Returns:
        包装后的函数
    """
    return get_logger().log_execution(func)


# 日志类 ， 传入config
class Log:
    def __init__(self,logconfig=None):
        self.config = logconfig
        self.out = False
        if self.config is None:
            print("Error: No log config found")
            exit(1)
        self.ut= util.Tools()
        self.config["log_path"] = self.config["log_path"] + f"/{self.ut.get_serial_number().strip() or 'tmp'}"
        # print(self.config["log_path"])
        #创建目录
        if not os.path.exists(self.config["log_path"]):
            os.makedirs(self.config["log_path"])
        # 创建带时间戳的日志目录
        self.log_dir = os.path.join(self.config["log_path"], time.strftime("%Y-%m-%d-%H", time.localtime()))
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if self.config["log_level"] == "DEBUG":
            self.out = True
        # 创建主logger
        self.main_logger = self._create_logger("main", self.config["log_file"])

        # 存储其他logger
        self.loggers = {"main": self.main_logger}
        self.main_logger.info("日志系统初始化完成")

    def _create_logger(self, name, filename):
        logger = logging.getLogger(name)
        if self.config["log_level"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif self.config["log_level"] == "INFO":
            logger.setLevel(logging.INFO)

        # 创建文件处理器
        log_file = os.path.join(self.log_dir, filename)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加处理器到logger
        logger.addHandler(file_handler)

        # 添加控制台处理器
        if self.config["console_output"]:  # 默认为True，保持原有行为
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)

        return logger

    def set_log_path(self,path):
        """设置日志路径"""
        if path is not None:
            self.log_dir = path


    def _create_logger_with_path(self, name, filename, log_dir):
        """在指定目录下创建logger"""
        logger = logging.getLogger(name)
        if self.config["log_level"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif self.config["log_level"] == "INFO":
            logger.setLevel(logging.INFO)

        # 创建文件处理器，使用指定的目录
        log_file = os.path.join(log_dir, filename)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加处理器到logger
        logger.addHandler(file_handler)

        # 添加控制台处理器
        if self.config["console_output"]:  # 默认为True，保持原有行为
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def get_log_file(self,pathtime=True):
        """获取日志文件路径
        time : 是否返回带日期的路径
        """
        if pathtime:
            return self.log_dir

        return self.config["log_path"]

    def log_execution(self,func):
        """
        一个用于记录函数执行前/后信息的装饰器。
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # --- 在函数执行前记录日志 ---
            func_name = func.__name__
            # 记录传入的参数
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            self.msg(f"正在调用函数: {func_name}，参数: ({signature})")

            try:
                # --- 执行原始函数 ---
                result = func(*args, **kwargs)

                # --- 在函数执行后（成功返回时）记录日志 ---
                self.msg(f"函数 {func_name} 执行完毕，成功返回。结果: {result!r}")
                return result

            except Exception as e:
                # --- 如果函数抛出异常，记录错误日志 ---
                self.msg(f"函数 {func_name} 执行期间发生异常: {e}",level='ERROR')
                # 重新抛出异常，不改变原始函数的行为
                raise e

        return wrapper
    


    def msg(self, message, level="INFO", logger_name="gpu_tool_debug",outconsole=False):
        """# 记录日志"""
        if message is None:
            message = ""
        if self.out:
            outconsole = self.out
        if logger_name == "memtester_test":
            a = ['\\','/','-','|','setting','testing']
            p = re.compile(r'^(?:' + '|'.join(map(re.escape, a)) + ')')
            if p.search(message):
                return
        if outconsole:
            print(message, flush=True)
            
        if logger_name not in self.loggers:
            self.main_logger.warning(f"Logger {logger_name} not found, using main logger")
            self.create_log_file(logger_name)
            logger_name = "gpu_tool_debug"

        

        logger = self.loggers[logger_name]
        if level == "INFO":
            logger.info(message)
        elif level == "DEBUG":
            logger.debug(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "CRITICAL":
            logger.critical(message)
        else:
            logger.info(message)

    @staticmethod
    def clean(line:str)->str:
        """清理特殊字符"""
        _CLEAN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        line = _CLEAN.sub('', line)          # 去颜色
        line = re.sub(r'\x08+', '', line)    # 去退格
        return line.rstrip('\r\n')


    def create_log_file(self, log_file, path='') -> str:
        """# 创建新的logger 返回log名称"""
        if log_file.split('.')[-1] != 'log':
            #使创建的文件名以.log结尾
            log_file = log_file + '.log'
        logger_name = os.path.splitext(log_file)[0]  # 去掉文件扩展名作为logger名称
        if logger_name not in self.loggers:
            # 如果提供了path参数，则在指定路径下创建日志文件
            if path and isinstance(path, str):
                # 创建指定路径的目录
                target_dir = os.path.join(self.log_dir, path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                # 修改_create_logger方法以支持自定义路径
                self.loggers[logger_name] = self._create_logger_with_path(logger_name, log_file, target_dir)
            else:
                self.loggers[logger_name] = self._create_logger(logger_name, log_file)
            self.main_logger.info(f"创建日志文件: {logger_name}")
        return logger_name


