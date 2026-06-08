import subprocess
import os
import shlex
import sys
import time
from typing import Dict
from core.log import get_logger
import utils.tool

class TerminalManager:
    """使用 screen 命令管理持久化的终端会话"""

    def __init__(self):
        self.log = get_logger()
        self.screens: Dict[str, Dict] = {}  # 存储所有 screen 会话信息
        self.last_progress_line = ""
        self.last_size= 0
        self.progress_active = False
        self.tool = utils.tool.Tools
        self._initialize_screen()  # 初始化 screen 环境

    def _initialize_screen(self) -> None:
        """初始化 screen 环境"""
        try:
            # 检查 screen 是否已安装
            result = subprocess.run(
                ["which", "screen"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                self.log.msg("screen 未安装，请先安装 screen 命令")
                return
            
            # 确保屏幕日志目录存在
            # log_dir = os.path.join(os.path.expanduser("~"), "screen_logs")
            # os.makedirs(log_dir, exist_ok=True)
            
            self.log.msg("screen 环境初始化完成")
        except Exception as e:
            self.log.msg(f"初始化 screen 环境失败: {e}")



    def _generate_screen_name(self, logname: str) -> str:
        """生成 screen 会话名称

        Args:
            logname: 日志名称

        Returns:
            str: screen 会话名称
        """
        result = subprocess.run(f"screen -ls | grep {logname}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 如果没有匹配的会话，直接返回 logname_1
        if result.returncode != 0 or not result.stdout.strip():
            return f"{logname}_1"
        
        # 提取所有已存在的会话名称
        existing_sessions = []
        for line in result.stdout.split('\n'):
            if line.strip():
                # screen -ls 的输出格式通常是: "12345.logname_id (Date Time)"
                # 我们需要提取出 "logname_id" 部分
                parts = line.split('.')
                if len(parts) > 1:
                    session_name = parts[1].split()[0]  # 获取 logname_id 部分
                    existing_sessions.append(session_name)
        
        # 找出最大的id值
        max_id = 0
        for session in existing_sessions:
            if session.startswith(logname + "_"):
                try:
                    id_part = session.split("_")[-1]
                    id_num = int(id_part)
                    if id_num > max_id:
                        max_id = id_num
                except (ValueError, IndexError):
                    continue
        
        # 返回新的会话名称，id为最大值+1
        return f"{logname}_{max_id + 1}"

    def execute_command(self, command: str, logname: str = "command", path: str = "/tmp") -> str:
        """在 screen 会话中执行命令

        Args:
            command: 要执行的命令
            logname: 日志名称，用于生成 screen 会话名称
            log_callback: 日志回调函数，用于接收命令输出
            path: 执行命令的路径

        Returns:
            str: screen 会话名称
        """
        # 生成 screen 会话名称
        # if logname =="fd_test":
        #     self.fd_run(command, path)
        #     return "fd_test"
        if logname == "dcgmi_test":
            self.tool.run_command("nvidia-smi -pm 1")
            
        screen_name = self._generate_screen_name(logname)
        
        # 创建日志文件路径
        log_file = self.get_rand_log_name(logname)
        
        # 构建 screen 命令
        # 使用 -L -Logfile 参数记录输出到日志文件
        # 使用 -dmS 参数创建 detached 模式的会话
        # 保持 screen 会话打开，并在命令完成后写一个完成标志文件
        end_marker = f"__SCREEN_COMMAND_COMPLETE_{logname}__"

        quoted_command = shlex.quote(
            f"cd {path} && {{ {command}; }}; echo {end_marker} ; exec bash"
        )
        screen_cmd = f"screen -L -Logfile {shlex.quote(log_file)} -dmS {shlex.quote(screen_name)} bash -lc {quoted_command}"
        self.screens[screen_name] = {
            "end_marker": end_marker,
            "log_file": log_file,
            "logname": logname,
            "path": path
            }  
        try:
            # 执行 screen 命令创建会话
            subprocess.run(
                screen_cmd,
                shell=True
            )
            
            return screen_name
            
        except subprocess.CalledProcessError as e:
            self.log.msg(f"创建 screen 会话失败: {e}")
            raise RuntimeError(f"创建 screen 会话失败: {e}")

    def fd_run(self, command: str, path: str = "/tmp"):
        cmd = f"python3 {self.tool.get_bash_path()}run_fd.py '{shlex.quote(path)}' {shlex.quote(command)}"
        
        subprocess.run(cmd, shell=True,text=True)
        return True
        

    def wait_for_command_completion(self, screen_name: str) -> bool:
        """等待 screen 命令结束"""
        if screen_name not in self.screens:
            self.log.msg(f"Screen 会话 {screen_name} 不存在")
            return False

        screen_info = self.screens[screen_name]
        marker = screen_info.get('end_marker')
        log_file = screen_info.get('log_file')
        log_name = screen_info.get('logname') or "unknown"

        if not log_file:
            self.log.msg(f"Screen 会话 {screen_name} 的日志信息不完整", outconsole=True)
            return False
        
        if not marker:
            self.log.msg(f"Screen 会话 {screen_name} 没有设置结束标记", outconsole=True)
            return False
        #等待日志文件被创建
        while not os.path.exists(log_file):
            time.sleep(0.5)
        _file_size = 0

        try:
            while True:
                try:
                    current_size = os.path.getsize(log_file)
                    
                    # 情况1：文件变大了，读取新增内容
                    if current_size > _file_size:
                        with open(log_file, 'r', encoding="utf-8", errors='ignore') as f:
                            f.seek(_file_size)
                            while True:
                                # readline 读取一行，如果没有新行会返回空字符串
                                line = f.readline()
                                if not line:
                                    # 更新指针位置并退出内层循环，等待下一次文件检查
                                    _file_size = f.tell()
                                    break
                                if marker in line:
                                    return True
                                # 实时输出到屏幕，去掉末尾的换行符再 print，避免双换行
                                sys.stdout.write(line)
                                sys.stdout.flush() # 强制刷新缓冲区，确保立即显示
                                self.log.msg(line, logger_name=log_name) # 也记录到日志中
                    
                    # 情况2：文件变小了（可能是 screen 清空了日志或重启了）
                    elif current_size < _file_size:
                        print(f"[Info] 检测到日志文件被重置或截断，重新开始监控...")
                        try:
                            _file_size = os.path.getsize(log_file)
                        except FileNotFoundError:
                            _file_size = 0
                    
                    # 情况3：文件大小没变，休眠一下减少 CPU 占用
                    time.sleep(0.05)

                except KeyboardInterrupt:
                    print("\n[Info] 用户停止监控。")
                    break
                except Exception as e:
                    # 防止因为偶尔的文件锁定或权限问题导致程序退出
                    print(f"[Error] 读取日志发生错误: {e}")
                    time.sleep(1)
                    return False

        finally:
            print("[Info] 监控结束。")
        return True
        

    def get_rand_log_name(self, base_name: str) -> str:
        """生成一个基于 base_name 的随机日志名称"""
        return f"/tmp/{base_name}_{int(time.time())}_{os.getpid()}.log"
