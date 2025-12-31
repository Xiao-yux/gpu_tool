import datetime
import glob
import inspect
import json
import os
import pathlib
import signal
import sys
import subprocess
import threading
import time
import termios
import tty
import select
import re
import multiprocessing as mp
import multiprocessing.synchronize
from typing import Any, Dict, List, Union, Optional
from pathlib import Path
class Tools:
    def __init__(self):
        ...

    @staticmethod
    def get_tmp_path() -> str:
        """获取临时目录
        return /usr/***/
        """
        temp_dir = os.path.join(os.path.dirname(__file__))
        _a = temp_dir.replace('utils','')
        return _a
    @staticmethod
    def get_dist_path() -> str:
        """获取程序所在目录

        """
        return str(pathlib.Path(sys.argv[0]).parent.resolve()) + '/'

    @staticmethod
    def poweoff():
        """关机"""
        os.system('sudo poweroff')

    @staticmethod
    def check_fd_log(logpath:str):
        """检查fd日志,并格式化输出
        logpath : fd 日志路径。
        """
        if logpath is None:
            logpath = os.getcwd()
        log = {
            'SN' : '',  # 机头SN
            'Result' :'',
            'GPU1' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU2' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU3' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU4' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU5' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU6' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU7' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'GPU8' : ['SN',{'checkinforom':'','connectivity':'','gpumem':'','gpustress':'','inforom':'','pcie':''},'PASS'],
            'fd':    {'inventory': '', 'nvlink': '', 'nvswitch': '', 'power': ''}
        }
        if not os.path.exists(os.path.join(logpath,"run.log")):
            return [f'路径不存在:{os.path.join(logpath,"run.log")}',True]

        def find_value(path: str, pattern: str):
            pat = rf"{re.escape(pattern)}\s*(.*?)\s*$"
            with open(path, "r", encoding="utf-8") as f:
                m = re.search(pat, f.read(), re.MULTILINE)
                f.close()
            return m.group(1) if m else None

        log['SN'] = find_value(os.path.join(logpath,"run.log"),'Serial Number')
        log['Result'] = find_value(os.path.join(logpath,"run.log"), 'Final Result:')

        #开始找单卡
        gpupath = ['checkinforom','connectivity','gpumem','gpustress','inforom','pcie']
        for a in gpupath:
            tmppath = os.path.join(logpath, a)
            pattern = os.path.join(tmppath, 'SXM[1-8]*', 'output.log')
            log_files = glob.glob(pattern, recursive=False)
            for f in log_files:
                s = f[len(tmppath):].strip('output.log')
                ss = s.strip('/')
                gp = ss[:4]   #SXM2_SN_********  取前四位
                str1 = 'GPU' + gp.strip('SXM')  #去除前3位
                log[str1][0] = ss
                log[str1][1][a] = find_value(f,"Error Code =")
                if log[str1][1][a] != '000000000000 (ok)':
                    log[str1][2]='FAIL'
        gpupath = ['inventory','nvlink','nvswitch','power']
        for a in gpupath:
            tmppath = os.path.join(logpath, a,"output.log")
            log['fd'][a] = find_value(tmppath,"Error Code =")
        return log

    def fd_log_print(self,path):
        a = self.check_fd_log(path)
        try:
            if a[1]:
                print(a[0])
                return
        except KeyError:
            pass
        self.print_report(a)


    @staticmethod
    def is_config_path() -> bool:
        """判断配置文件是否存在"""
        config_file= "/etc/gpu_tool/config.toml" #配置文件
        return os.path.exists(config_file)


    def run_nvidia_service(self):
        ser = ['nvidia-fabricmanager.service','nvidia-imex.service','nvidia-persistenced.service','nvidia-dcgm.service','openibd.service']
        for s in ser:
            cmd = "systemctl start " + s
            self.run_command(cmd)
    @staticmethod
    def get_gpu_count():
        """返回GPU数量"""

        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("检测不到 nvidia-smi，无法获取 GPU 数量")
            return 0

        if not os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return 0

    @staticmethod
    def async_run(func, *args,daemon: bool = False, **kwargs) -> threading.Thread:
        """
    异步运行函数

    Args:
        func: 要异步执行的函数
        *args: 函数的位置参数
        daemon: 是否设置为守护线程
        **kwargs: 函数的关键字参数

    Returns:
        threading.Thread: 创建的线程对象
    """
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = daemon
        thread.start()
        return thread

    @staticmethod
    def show_methods(cls):
        """打印类中所有用户定义的实例方法及其 docstring"""
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # 只保留定义在【当前类】里的，过滤掉继承来的
            if method.__qualname__.startswith(cls.__name__ + '.'):
                print(f'{name}{inspect.signature(method)}')
                print(method.__doc__ or '  # 无 docstring')
                print('-' * 40)

    @staticmethod
    def find_fail(path: str) -> bool:
        """
        判断文本文件中是否出现 Fail / fail / FAIL 等大小写形式。
        文件不存在直接返回 False。
        """
        if not os.path.isfile(path):
            return False

        # 预编译正则，忽略大小写
        pattern = re.compile(r'\bfail\b', re.IGNORECASE)

        # 逐行扫描，省内存
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if pattern.search(line):
                    return True
        return False

    @staticmethod
    def copy_file( src, dst)-> None:
        """复制文件"""
        os.system(f'cp {src} {dst}')

    def get_gpu_info(self)-> str:
        """返回GPU信息"""
        return os.popen(f"bash {self.get_tmp_path()}bash/nvidia_info.sh").read()
    def get_sys_info(self) -> str:
        """# 返回系统信息"""
        return os.popen(f'bash {self.get_tmp_path()}bash/sys_info.sh').read()
    def get_eth_info(self) -> str:
        """# 网卡硬盘信息"""
        return os.popen(f'bash {self.get_tmp_path()}bash/CX_DISK_INFO.sh').read()
    @staticmethod
    def input_chick():
        """输入回车继续"""
        input("按下回车键继续...")
        return
    @staticmethod
    def run_command(command: str, cmd = "1", out = False) -> int | None | str:
        """执行命令并返回输出
            1 : 使用subprocess.run
            2 ： 使用 os.popen
        """
        if cmd == "1":
            try:
                with subprocess.Popen(command,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,  # 将错误输出合并到标准输出
                                           text=True,

                                           shell=True,
                                           universal_newlines=True) as process:
                    full_output =[ ]
                    if out:
                        for line in process.stdout:  # 逐行读，不会死锁
                            line = line.rstrip()
                            print(line)
                            full_output.append(line)
                        process.wait()  # 确保进程结束
                    else:
                        stdout, _ = process.communicate()
                        full_output.append(stdout)
                return "\n".join(full_output) if full_output else ""
            except subprocess.CalledProcessError as e:
                return f"Error: {e.stderr.strip()}"

        return os.popen(command).read()

    def set_bmc_dhcp(self)-> bool:
        """设置BMC为DHCP获取IP"""
        self.run_command('ipmitool lan set 1 ipsrc dhcp')

        return True
    @staticmethod
    def get_pwd()-> str:
        """返回用户当前目录"""
        return os.popen('pwd').read().split('\n')[0]
    @staticmethod
    def get_serial_number():
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()

    @staticmethod
    def get_nvidia_bug_report(paths,logname):
        cmd = f'nvidia-bug-report.sh --output-file "{logname}"'
        subprocess.Popen(cmd,cwd=paths,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)

    @staticmethod
    def rest_gpu_server():
        # 重启GPU服务
        subprocess.run('systemctl restart nvidia-powerd', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-dcgm', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-fabricmanager', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-persistenced', shell=True, check=True)
        return True
    @staticmethod
    def check_fd_path(path):
        """检查目录非空"""
        if os.path.exists(path) and os.listdir(path):
            os.system(f"mv {path} {path}_{time.strftime('%Y-%m-%d-%H-%S', time.localtime())}_bak")
            return True
        return False
    @staticmethod
    def get_gpu_memory():
        """返回GPU显存信息"""
        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("检测不到 nvidia-smi，无法获取 GPU 显存")
            return 0

        if not os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return "NaN"

    @staticmethod
    def fd_arg_chines(chines):
        """fd 选择参数解析"""
        cmd = f"--test="
        for i in chines:
            cmd += i.data + ","
        cmd = cmd[:-1]  # 去除最后一个逗号
        return cmd
    @staticmethod
    def get_bash_path():
        """获取bash路径"""
        # temp_dir = Path(sys.path[1])
        # temp_dir = Path(__file__).resolve().parent
        temp_dir = os.path.join(os.path.dirname(__file__))
        _a = temp_dir.replace('utils', '')
        return f"{str(_a)}"+ "bash/"

    @staticmethod
    def print_report(s: dict) -> None:
        header = (
            "----------------------------------------------------------------------------------------------------\n"
            "| 机头SN : {sn:<40}  ||  Result : {result:<40} |\n"
            "|--------------------------------------------------------------------------------------------------\n"
            "|       {check:<20} {conn:<20} {mem:<20} {stress:<18} {info:<18} {pcie:<17} | Result | SN\n"
            "----------------------------------------------------------------------------------------------------"
        ).format(
            sn=s['SN'], result=s['Result'],
            check='checkinforom', conn='connectivity',
            mem='gpumem', stress='gpustress',
            info='inforom', pcie='pcie'
        )
        print(header)
        for i in range(1, 9):
            gpu = s[f'GPU{i}']
            vals = gpu[1]
            print("| GPU{i} | {check:<12} | {conn:<12} | {mem:<12} | {stress:<12} | {info:<12} | {pcie:<12} | {res:<6} | {sn:<13}".format(
                i=i,
                check=vals['checkinforom'] or '',
                conn=vals['connectivity'] or '',
                mem=vals['gpumem'] or '',
                stress=vals['gpustress'] or '',
                info=vals['inforom'] or '',
                pcie=vals['pcie'] or '',
                res=gpu[2] or 'FAIL',
                sn=gpu[0] or 'NA'
            ))
        print("----------------------------------------------------------------------------------------------------")
        gpupath = ['inventory', 'nvlink', 'nvswitch', 'power']
        for a in gpupath:
            print(f"|{a:<10}  = {s['fd'][a]}|")

def exitfun(func):
    """
    装饰器：按 ESC 或 q 立即结束被装饰函数的执行。
    """
    def _watch_keyboard(fd: int,
                        kill_evt: "mp.synchronize.Event") -> None:
        """键盘监听：发现 ESC/q 就置位 kill_evt"""
        while not kill_evt.is_set():
            if select.select([fd], [], [], 0.2)[0]:
                ch = os.read(fd, 1)
                if ch in (b'q', b'\x1b'):      # \x1b 是 ESC
                    kill_evt.set()

    def wrapper(*args, **kwargs):
        fd = sys.stdin.fileno()
        old_attr = termios.tcgetattr(fd)

        kill_evt: mp.synchronize.Event = mp.Event()
        proc = mp.Process(
            target=func,
            args=args,
            kwargs=kwargs,
            daemon=False                    # 非 daemon，我们需要显式杀
        )
        def _wrap():
            os.setsid()      # 新建会话+进程组
            func(*args, **kwargs)
        proc = mp.Process(target=_wrap, daemon=False)
        proc.start()
        try:
            tty.setcbreak(fd)
            watch = mp.Process(target=_watch_keyboard,
                               args=(fd, kill_evt),
                               daemon=True)
            watch.start()
            while not kill_evt.is_set() and proc.is_alive():
                proc.join(0.2)

            if proc.is_alive():
                pgid = os.getpgid(proc.pid)      # 拿到刚才新建的组
                # 保险：pgid 必须 > 1，且不等于当前进程组
                if pgid > 1 and pgid != os.getpgrp():
                    try:
                        os.killpg(pgid, signal.SIGTERM)
                        proc.join(timeout=3)
                    except (ProcessLookupError, OSError):
                        pass
                    if proc.is_alive():
                        try:
                            os.killpg(pgid, signal.SIGKILL)
                        except (ProcessLookupError, OSError):
                            pass
                else:
                    # 退化到只杀单进程
                    proc.terminate()
                    proc.join(timeout=1)
                    if proc.is_alive():
                        os.kill(proc.pid, signal.SIGKILL)
                print('\n[exitfun] 用户中断，子进程组已结束')

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)
            sys.stdout.flush()
            kill_evt.set()

            os.system("pkill -KILL -f memtester")
            os.system("pkill -KILL -f fio")
            os.system("pkill -KILL -f stress-ng")
            watch.join(timeout=0.5)

    return wrapper


class ipmitools():
    """ ipmi相关工具"""
    @staticmethod
    def sdr():
        """传感器数据"""
        return os.popen('ipmitool sdr').read()
    @staticmethod
    def fru():
        """电源信息"""
        return os.popen('ipmitool fru').read()
    @staticmethod
    def lan():
        """lan信息"""
        return os.popen('ipmitool lan print').read()
    @staticmethod
    def syslogtotty():
        """重定向系统日志到tty9"""
        subprocess.run('', shell=True, check=True)
    @staticmethod
    def user():
        """用户信息"""
        return os.popen('ipmitool user list 1').read()

class JsonDB:
    def __init__(self, file_path: str, auto_save: bool = False):
        self.file_path = os.path.abspath(file_path)
        self.ensure_file(self.file_path)
        self.auto_save = auto_save
        self._data: Dict[str, Any] = {}
        self._load()

    # ---------- 内部工具 ----------
    def _load(self) -> None:
        if os.path.getsize(self.file_path) == 0:  # 文件空
            self._data = {}
            return
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    PathLike = Union[str, bytes, os.PathLike]

    @staticmethod
    def ensure_file(path: PathLike,
                    *,
                    mkdir: bool = True,
                    content: Optional[str] = None,
                    encoding: str = "utf-8",
                    mode: str = "w",  # "w" / "a" / "x"  或 None（只创建空文件）
                    permissions: Optional[int] = None
                    ) -> tuple[bool, str]:
        """
        创建文件并写入内容（可选）。
        返回 (success, message)
        """
        try:
            # 1. 统一转成 Path 对象，并展开 ~ 和环境变量
            p = Path(path).expanduser().expanduser().resolve()

            # 2. 若目录不存在，按需创建
            if mkdir:
                parent = p.parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)

            # 3. 若仅想创建空文件且已存在，直接返回
            if mode is None and p.exists():
                return True, f"文件已存在: {p}"

            # 4. 写入/追加内容
            if mode in {"w", "a", "x"}:
                with p.open(mode, encoding=encoding) as f:
                    if content is not None:
                        f.write(content)
            elif mode is None:
                # 只创建空文件
                p.touch(exist_ok=True)
            else:
                return False, f"不支持的 mode: {mode}"

            # 5. 设置权限（可选）
            if permissions is not None:
                os.chmod(p, permissions)

            return True, f"文件已创建: {p}"

        except Exception as e:
            return False, f"创建文件失败: {e}"

    def _maybe_save(self) -> None:
        if self.auto_save:
            self.save()

    # ---------- 对外 API ----------
    def add(self, key: str, value: Any) -> None:
        """
        多次 add 同一 key，自动升级为数组并追加：
        第 1 次: add('user','alice')   -> {'user': 'alice'}
        第 2 次: add('user','bob')     -> {'user': ['alice', 'bob']}
        第 3 次: add('user','c')       -> {'user': ['alice', 'bob', 'c']}
        """
        if key not in self._data:
            # 第一次：直接存
            self._data[key] = value
        else:
            exist = self._data[key]
            if isinstance(exist, list):
                # 已经是数组，直接追加
                exist.append(value)
            else:
                # 升级成数组
                self._data[key] = [exist, value]
        self._maybe_save()
    def get(self,key):
        try:
            return self._data[key]
        except KeyError:
            return None

    def edit(self, key: str, value: Any) -> None:
        """整体覆盖，不做数组升级"""
        self._data[key] = value
        self._maybe_save()

    # 让对象像 dict 一样使用
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._maybe_save()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"JsonDB({self._data})"
if __name__ == '__main__':
    tools = Tools()
    a = "/mnt/c/Users/Administrator/Documents/work/gpu_tool/tmp/2"
    s = tools.check_fd_log(a)
    print(s)
    tools.print_report(s)