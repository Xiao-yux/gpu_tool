import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import utils.tool as utils
from log.logger import get_logger


class TerminalManager:
    """命令执行 管理"""

    def __init__(self):
        self.log = get_logger()
        self.log.info("初始化 TerminalManager")
        self.screens: dict[str, dict] = {}  # 存储所有 会话信息
        self.last_progress_line = ""
        self.last_size= 0
        self.progress_active = False
        self.tool = utils.Tools()


    def _generate_screen_name(self, logname: str) -> str:
        """生成 会话名称

        Args:
            logname: 日志名称

        Returns:
            str: 会话名称
        """
        result = subprocess.run(f"-ls | grep {logname}", shell=True, text=True,capture_output=True)
        # 如果没有匹配的会话，直接返回 logname_1
        if result.returncode != 0 or not result.stdout.strip():
            return f"{logname}_1"
        
        # 提取所有已存在的会话名称
        existing_sessions = []
        for line in result.stdout.split('\n'):
            if line.strip():
                # -ls 的输出格式通常是: "12345.logname_id (Date Time)"
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
                    max_id = max(max_id, id_num)
                except (ValueError, IndexError):
                    continue
        
        # 返回新的会话名称，id为最大值+1
        return f"{logname}_{max_id + 1}"

    def execute_command(self, command: str, logname: str = "command", path: str | Path= "/tmp") -> str:
        """在 会话中执行命令

        Args:
            command: 要执行的命令
            logname: 日志名称，用于生成 会话名称
            path: 执行命令的路径

        Returns:
            str: 会话名称
        """
        # 生成 会话名称
        # if logname =="fd_test":
        #     self.fd_run(command, path)
        #     return "fd_test"
        if logname != "fd_test":
            self.tool.run_command("nvidia-smi -pm 1")
            
        screen_name = self._generate_screen_name(logname)
        
        # 创建日志文件路径
        log_file = f"{self.log.paths.run}/{logname}.log"
        
        self.log.info(f"执行命令: {command}", file_name=f"run/{logname}")
        self.log.info(f"执行目录: {path}", file_name=f"run/{logname}")
        # 构建 命令

        end_marker = f"__SCREEN_COMMAND_COMPLETE_{logname}__"
        #print(f"执行命令: {command}，path: {path},logname: {logname}")
        full_command = f"cd {path} && {{ {command}; }}; echo {end_marker}"
        #print(f"完整命令: {full_command}")
        self.screens[screen_name] = {
            "end_marker": end_marker,
            "log_file": log_file,
            "logname": logname,
            "path": path
            }  
        try:
            # 启动命令,输出重定向到日志文件
            with open(log_file, 'a',encoding="utf-8", errors='ignore') as f:
                subprocess.Popen(
                full_command,
                shell=True,
                stdout=f,
                stderr=f,
                # start_new_session=True,
                cwd=path
            )
            return screen_name
            
        except subprocess.CalledProcessError as e:
            self.log.info(f"创建会话失败: {e}")
            raise RuntimeError(f"创建会话失败: {e}")


    def wait_for_command_completion(self, screen_name: str) -> bool:
        """等待 命令结束并输出会话执行信息到屏幕上"""
        if screen_name not in self.screens:
            self.log.info(f"会话 {screen_name} 不存在")
            return False

        screen_info = self.screens[screen_name]
        marker = screen_info.get('end_marker')
        log_file = screen_info.get('log_file')
        log_name = f"run" + "/" + (screen_info.get('logname') or "unknown")
        # self.log.info(f"日志文件创建路径: {log_name}", file_name=log_name,console=True)
        if not log_file:
            self.log.info(f"会话 {screen_name} 的日志信息不完整", console=True)
            return False
        
        if not marker:
            self.log.info(f"会话 {screen_name} 没有设置结束标记", console=True)
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
                               
                                sys.stdout.write(line)
                                sys.stdout.flush() # 强制刷新缓冲区，确保立即显示
                                #self.log.info(line, file_name=log_name) # 也记录到日志中
                    
                    # 情况2：文件变小了（可能是 清空了日志或重启了）
                    elif current_size < _file_size:
                        print("[Info] 检测到日志文件被重置或截断，重新开始监控...")
                        try:
                            _file_size = os.path.getsize(log_file)
                        except FileNotFoundError:
                            _file_size = 0
                    
                    # 情况3：文件大小没变，休眠一下减少 CPU 占用
                    time.sleep(0.01)

                except KeyboardInterrupt:
                    print("\n[Info] 用户停止监控。")
                    break
                except FileNotFoundError as e:
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
