import glob
import inspect
import os
import re
import subprocess
import sys
import threading
from pathlib import Path


class Tools:
    def __init__(self):
        pass


    @staticmethod
    def get_tmp_path() -> Path:
        """获取程序临时目录 root path
        return /usr/***/
        """
        temp_dir = os.path.join(os.path.dirname(__file__))
        _a = temp_dir.replace('utils','')
        return Path(_a)
    @staticmethod
    def get_bash_path() -> Path:
        """获取bash脚本目录"""
        return Tools.get_tmp_path() / "bash"
    @staticmethod
    def get_dist_path() -> Path:
        """获取程序所在目录

        """
        return Path(sys.argv[0]).parent.resolve()

    def get_memort_ecc(self):
        """获取内存ECC状态"""
        return os.popen(f"bash edac-util -v | grep -i edac-util").read()
    

    @staticmethod
    def poweoff():
        """关机"""
        subprocess.run('poweroff', shell=True, check=True)

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
                s = f[len(tmppath):].removesuffix('output.log')
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
            if isinstance(a, list):
                print(a[0])
                return
        except KeyError:
            pass
        self.print_report(a)

    def run_nvidia_service(self):
        ser = ['nvidia-fabricmanager.service','nvidia-imex.service','nvidia-persistenced.service','nvidia-dcgm.service','openibd.service']
        for s in ser:
            cmd = "systemctl start " + s
            threading.Thread(target=self.run_command, args=(cmd,)).start()
    def get_gpu_count(self):
        """返回GPU数量"""

        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("No nvidia-smi detected, cannot get GPU count")
            return 0
        sub_list = ["NVIDAI","NVML"]
        b = os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits').read()
        if not any(sub in b for sub in sub_list):
            return os.popen('nvidia-smi --query-gpu=count --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return 0

    @staticmethod
    def is_glob_dir(path: str , dirname: str) -> bool:
        """检查路径下是否存在以 dirname 开头的目录"""
        logs_dirs = [d for d in glob.glob(f"{path}/{dirname}*") if os.path.isdir(d)]
        if logs_dirs:
            return True
        return False
    
    
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
    def show_methods(clss):
        """打印类中所有用户定义的实例方法及其 docstring"""
        for name, method in inspect.getmembers(clss, predicate=inspect.isfunction):
            # 只保留定义在【当前类】里的，过滤掉继承来的
            if method.__qualname__.startswith(clss.__name__ + '.'):
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

    def get_gpu_info(self,arg='')-> str:
        """返回GPU信息"""
        return os.popen(f"bash {self.get_tmp_path()}/bash/nvidia_info.sh {arg}").read()
    
    
    def get_query_gpu(self):
        return self.run_command(f"{self.get_tmp_path()}/bash/deviceQuery")
        
        
    def get_sys_info(self,arg='') -> str:
        """# 返回系统信息"""
        return os.popen(f'bash {self.get_tmp_path()}/bash/sys_info.sh {arg}').read()
    def get_eth_info(self,arg='') -> str:
        """# 网卡硬盘信息"""
        return os.popen(f'bash {self.get_tmp_path()}/bash/CX_DISK_INFO.sh {arg}').read()
    def input_chick(self):
        """输入回车继续"""
        input("按下回车键继续...")
    @staticmethod
    def run_command(command: str, cmd = "1", out = False,path="/tmp") -> int | None | str:
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
                                           cwd=path,
                                           shell=True,
                                           universal_newlines=True) as process:
                    full_output =[ ]
                    if out:
                        if process.stdout is None:
                            return ""
                        for line in process.stdout:  # 逐行读，不会死锁
                            line = line.rstrip()
                            # print(line)
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
    def get_nvidia_bug_report(paths):
        cmd = f'cd {paths} && nvidia-bug-report.sh'
        subprocess.Popen(cmd,cwd=paths,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)

    @staticmethod
    def rest_gpu_server():
        # 重启GPU服务
        subprocess.run('systemctl restart nvidia-powerd', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-dcgm', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-fabricmanager', shell=True, check=True)
        subprocess.run('systemctl restart nvidia-persistenced', shell=True, check=True)
        return True
    
    def stop_nvidia_service(self):
        """停止NVIDIA相关服务"""
        ser = ['nvidia-fabricmanager.service','nvidia-imex.service','nvidia-persistenced.service',
               'nvidia-dcgm.service','openibd.service','nvidia-powerd.service','systemd-udevd.service','systemd-udevd-kernel.socket',
               'systemd-udevd-control.socket']
        for s in ser:
            cmd = "systemctl stop " + s
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                pass
    
    def rm_nvidia_mod(self):
        """移除NVIDIA模块"""
        try:
            cmd = "rmmod nvidia_drm"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nvidia_uvm"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nvidia_modeset"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nvidia"
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove NVIDIA modules: {e}")
        
    def rm_switch_mod(self):
        """移除交换机模块"""
        try:
            cmd = "rmmod openvswitch"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nsh"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nf_nat"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nf_conncount"
            subprocess.run(cmd, shell=True, check=True)
            cmd = "rmmod nf_conntrack"
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove switch modules: {e}")

    def stop_openvswitch(self):
        """停止openvswitch服务"""
        a = ["openvswitch-switch.service","switcheroo-control.service","openibd.service"]
        for s in a:
            cmd = "systemctl stop " + s
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                pass

    @staticmethod
    def check_fd_path(path):
        """检查目录非空"""
        return bool(os.path.exists(path) and os.listdir(path))
    
    
    def get_gpu_memory(self):
        """返回GPU显存信息"""
        if not os.path.exists('/usr/bin/nvidia-smi'):
            print("No nvidia-smi detected, cannot get GPU memory")
            return 0

        if not os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | grep -i nvidia').read():
            return os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits').read().split('\n')[0]
        else:
            return 0

    @staticmethod
    def fd_arg_chines(chines):
        """fd 选择参数解析"""
        cmd = "--test="
        for i in chines:
            cmd += i.data + ","
        cmd = cmd[:-1]  # 去除最后一个逗号
        return cmd

    @staticmethod
    def print_report(s) -> None:
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






if __name__ == '__main__':
    tools = Tools()
    a = "/mnt/c/Users/Administrator/Documents/work/gpu_tool/tmp/2"
    s = tools.check_fd_log(a)
    print(s)
    tools.print_report(s)