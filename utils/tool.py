import glob
import inspect
import os
import pathlib
import sys
import subprocess
import threading
import time
import termios
import tty
import select
import re


class Tools:
    def __init__(self):
        ...

    @staticmethod
    def get_tmp_path() -> str:
        """获取临时目录
        return /usr/***/
        """
        temp_dir = os.path.join(os.path.dirname(__file__))
        a = temp_dir.replace('utils','')
        return a
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
        '''判断配置文件是否存在'''
        config_file= "/etc/gpu_tool/config.toml" #配置文件
        return os.path.exists(config_file)

    @staticmethod
    def get_gpu_count():
        '''返回GPU数量'''

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
        '''复制文件'''
        os.system(f'cp {src} {dst}')

    def get_gpu_info(self)-> str:
        '''返回GPU信息'''
        return os.popen(f"bash {self.get_tmp_path()}bash/nvidia_info.sh").read()
    def get_sys_info(self) -> str:
        '''# 返回系统信息'''
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
    def run_command(command: str, cmd = "1") -> int | None | str:
        """执行命令并返回输出
            1 : 使用subprocess.run
            2 ： 使用 os.popen
        """
        if cmd == "1":
            try:
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                return f"Error: {e.stderr.strip()}"
        elif cmd == "2":
            return os.popen(command).read()
        return os.popen(command).read()

    def set_bmc_dhcp(self)-> bool:
        '''设置BMC为DHCP获取IP'''
        self.run_command('ipmitool lan set 1 ipsrc dhcp')

        return True
    @staticmethod
    def get_pwd()-> str:
        '''返回用户当前目录'''
        return os.popen('pwd').read().split('\n')[0]
    @staticmethod
    def get_serial_number():
        # 返回主板序列号
        return os.popen('dmidecode -s system-serial-number').read()

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
        return f"{str(pathlib.Path(sys.argv[0]).parent.resolve())}"+ "/bash/"

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
    def _watcher(fd, ev: threading.Event):
        while not ev.is_set():
            if select.select([fd], [], [], 0.2)[0]:
                if os.read(fd, 1) in (b'q', b'\x1b'):
                    ev.set()

    def wrapper(*args, **kwargs):
        fd = sys.stdin.fileno()
        old_attr = termios.tcgetattr(fd)
        exit_ev = threading.Event()
        try:
            tty.setcbreak(fd)
            th = threading.Thread(target=_watcher, args=(fd, exit_ev), daemon=True)
            th.start()
            kwargs['_exit_flag'] = exit_ev
            return func(*args, **kwargs)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)
            sys.stdout.flush()

    return wrapper


class ipmitools():
    """ ipmi相关工具"""

    def sdr():
        '''传感器数据'''
        return os.popen('ipmitool sdr').read()
    def fru():
        '''电源信息'''
        return os.popen('ipmitool fru').read()
    def lan():
        '''lan信息'''
        return os.popen('ipmitool lan print').read()
    def syslogtotty():
        '''重定向系统日志到tty9'''
        subprocess.run('', shell=True, check=True)
    def user():
        '''用户信息'''
        return os.popen('ipmitool user list 1').read()


if __name__ == '__main__':
    tools = Tools()
    a = "/mnt/c/Users/Administrator/Documents/work/gpu_tool/tmp/2"
    s = tools.check_fd_log(a)
    print(s)
    tools.print_report(s)