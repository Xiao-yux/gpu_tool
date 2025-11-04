import logging
import os
import time
import utils.tools as util

# 日志类 ， 传入config
class Log():
    def __init__(self,logconfig=None):
        self.config = logconfig
        
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
        if self.config["console_output"] == True:  # 默认为True，保持原有行为
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)

        return logger

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
        if self.config["console_output"] == True:  # 默认为True，保持原有行为
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def get_log_file(self):
       '''获取日志文件路径'''
       
       return self.log_dir
    
    def msg(self, message, level="INFO", logger_name="main"):
        
        if logger_name not in self.loggers:
            self.main_logger.warning(f"Logger {logger_name} not found, using main logger")
            self.create_log_file(logger_name)
            logger_name = "main"

        logger = self.loggers[logger_name]
        # logger.info(level)
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

    def create_log_file(self, log_file, path='') -> str:
        '''# 创建新的logger 返回log名称'''
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


