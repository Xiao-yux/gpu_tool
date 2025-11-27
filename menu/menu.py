import subprocess
from typing import Dict, List
import json
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from utils.tool import Tools
from core.log import Log


class Menu:
    def __init__(self, path: Dict, log: Log):
        self.menu_chess = MenuChess()
        self.path = path
        self.tool = Tools()
        self.log = log
        self.log.msg('Menu initialized.')

    def main_menu(self):
        """主菜单"""
        pro = ListPrompt("请选择操作:", choices=self.menu_chess.main_menu,
                         validator=lambda x: x != self.menu_chess.main_menu[0], error_message="暂未完成").prompt()
        if pro.data == "exit":
            os._exit(0)
        elif pro.data == "2":
            self.sys_info_menu()
        elif pro.data == "3":
            self.gpu_test_menu()
        elif pro.data == "4":
            self.system_test_menu()
        elif pro.data == "5":
            self.system_set_menu()
        elif pro.data == "6":
            self.tool.run_command("poweroff")

        self.log.msg(f'用户选择: {pro}')

    def system_set_menu(self):
        """BMC用户设置菜单"""
        pro = ListPrompt("请选择BMC用户设置项:", choices=self.menu_chess.setsystem_menu,
                         validator=lambda x: x != self.menu_chess.setsystem_menu[1], error_message="暂未完成").prompt()
        if pro.data == "exit":
            self.main_menu()
        elif pro.data == "1":
            self.tool.set_bmc_dhcp()
        cmd = f"ipmitool user {pro.data}"
        self.log.msg(f'用户选择BMC用户设置菜单: {pro}')
        self.main_menu()

    def gpu_test_menu(self):
        """GPU测试菜单"""
        pro = ListPrompt("请选择GPU测试项:", choices=self.menu_chess.gpu_test_menu).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            self.fd_menu()
        elif pro.data == "2":
            self.gpu_burn_menu()
        elif pro.data == "3":
            self.dcgmi_menu()
        elif pro.data == "4":
            a = ListPrompt("请选择NVBAND测试项:", choices=self.menu_chess.nvband_menu).prompt()
            cmd = f"./nvbandwidth"
            path = f"{self.tool.get_bash_path()}"
            if a.data == "-1":
                self.run_command(cmd, path, logname="nvband_test")
            else:
                cmd += f" {a.data}"
                self.run_command(cmd, path, logname="nvband_test")
        elif pro.data == "5":
            self.nccl_menu()
        elif pro.data == "6":
            cmd = "./p2pBandwidthLatencyTest"
            path = f"{self.tool.get_bash_path()}"
            logname = self.log.create_log_file("p2pBandwidthLatencyTest_test")
            self.run_command(cmd, path, logname)
        self.log.msg(f'用户选择GPU测试菜单: {pro}')
        self.main_menu()

    def sys_info_menu(self):
        """系统信息菜单"""
        pro = ListPrompt("请选择系统信息查看项:", choices=self.menu_chess.system_menu).prompt()
        if pro.data == "exit":
            self.main_menu()
        if pro.data == "1":
            self.log.msg(self.tool.get_sys_info(), outconsole=True)
        elif pro.data == "2":
            self.log.msg(self.tool.get_gpu_info(), outconsole=True)
        elif pro.data == "3":
            self.log.msg(self.tool.get_eth_info(), outconsole=True)
        elif pro.data == "4":
            self.log.msg(self.tool.run_command("nvidia-smi topo -m",cmd="2"), outconsole=True)
        elif pro.data == "5":
            self.log.msg(self.tool.run_command("ipmitool lan print",cmd="2"), outconsole=True)
        self.log.msg(f'用户选择: {pro}')
        self.tool.input_chick()
        self.main_menu()

    def dcgmi_menu(self):
        """DCGMI测试菜单"""
        pro = ListPrompt("请选择DCGMI测试项:", choices=self.menu_chess.dcgm_menu).prompt()
        if pro.data == "exit":
            self.gpu_test_menu()
        cmd = f"dcgmi {pro.data}"
        self.log.msg(f'用户选择DCGMI测试菜单: {pro}')
        self.run_command(cmd, logname="dcgmi_test")
        self.main_menu()

    def gpu_burn_menu(self):
        """GPU烧机测试菜单"""
        pro = ListPrompt("请选择GPU烧机测试项:", choices=self.menu_chess.gpu_burn_menu).prompt()
        if pro.data == "exit":
            self.gpu_test_menu()
        cmd = f"./{self.path['gpu_burn_exe']} {pro.data}"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="gpu_burn_test")
        self.log.msg(f'用户选择GPU烧机测试菜单: {pro}')
        self.main_menu()

    def fd_menu(self):
        """Folding测试菜单"""
        cmd = f"{self.path['fd_exe']} "
        path = f"{self.path['fd_path']}"
        self.tool.check_fd_path(f"{self.log.get_log_file()}/fd")
        logname = self.log.create_log_file("fd_test")
        pro = ListPrompt("请选择Folding测试项:", choices=self.menu_chess.fd_menu).prompt()
        print(pro)
        if pro.data == "exit":
            self.gpu_test_menu()
        if pro.data == "1":
            cmd += f"--no_bmc --level1 --log {self.log.get_log_file()}/fd"
            self.run_command(cmd, path, logname)
        elif pro.data == "2":
            cmd += f"--no_bmc --level2 --log {self.log.get_log_file()}/fd"
            self.run_command(cmd, path, logname)
        elif pro.data == "3":
            a = CheckboxPrompt("选择单项测试项目:", choices=self.menu_chess.fd_test_arg_menu).prompt()
            cmd += f"{self.tool.fd_arg_chines(a)}"
            self.log.msg(cmd)
            self.run_command(cmd, path, logname)
        elif pro.data == "4":
            arg = InputPrompt(f"请输入自定义参数: {cmd} [input] --log {self.log.get_log_file()}/fd").prompt()
            cmd += f"{arg} --log {self.log.get_log_file()}/fd"
            self.run_command(cmd, path, logname)
        self.log.msg(f'用户选择Folding测试菜单: {pro}')
        self.main_menu()

    def run_command(self, command: str, path: str = '/tmp', logname: str = "command"):
        """运行命令并实时输出日志
        command : 执行的命令
        path : 执行命令时的目录
        logname : 日志名称
        """
        logname = self.log.create_log_file(logname)
        enve = os.environ.copy()
        enve['LC_ALL'] = 'C.UTF-8'
        self.log.msg(f"执行命令{command}", outconsole=True)
        try:

            self.log.msg(f"执行命令: {command}", logger_name=logname)
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将错误输出合并到标准输出
                text=True,
                cwd=path,
                env=enve,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            if process.stdout is None:
                raise subprocess.SubprocessError("无法创建进程或获取输出流")
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log.msg(output.strip(), logger_name=logname, outconsole=True)  # 同时记录到日志
            return_code = process.poll()
            self.log.msg(f"命令执行结束, 返回码: {return_code}")
            self.log.msg(f"日志路径: {self.log.get_log_file()}/{logname}", outconsole=True)
            self.log.msg(f"\n", outconsole=True)
            # 按下回车继续
            self.tool.input_chick()
        except Exception as e:
            self.log.msg(f"运行命令失败: {e}")
            print(f"执行失败: {e}")

    def nccl_menu(self):
        cmd = f"./{self.path['nccl_exe']} "
        path = f"{self.path['nccl_path']}"
        logname = self.log.create_log_file("nccl_test")
        cmd += f"-b 256M -e {self.tool.get_gpu_memory()} -f 2 -g {self.tool.get_gpu_count()}"
        self.run_command(cmd, path, logname)

    def system_test_menu(self):
        pro = ListPrompt("请选择系统其他测试项:", choices=self.menu_chess.sys_test_menu).prompt()
        if pro.data == "exit":
            self.main_menu()
        if pro.data == "1":
            a = InputPrompt("输入测试时间(秒),默认300秒:").prompt()
            if not a:
                a = "300"
            cmd = f"stress-ng --cpu 0 --cpu-method all --cache 0 --matrix 0 --memcpy 0 --mq 0 --pipe 0 --fork 0 --switch 0 --vm 2 --vm-bytes 80% --iomix 4 --iomix-bytes 1g --timeout {a}s  --metrics-brief --tz --perf --verify --times --log-file '{self.log.get_log_file()}/stress_ng.log'"
            self.run_command(cmd, logname="system_stress_test")
        if pro.data == "2":
            a = int(os.popen("free -m | grep Mem | awk '{print ($2)}'").read())
            self.log.msg(a)
            cmd = f"memtester {a - 4096}M"
            self.log.msg(cmd)
            self.run_command(cmd, logname="memtester_test")
        if pro.data == "3":
            self.disk_speed_test_menu()
        self.main_menu()

    def disk_speed_test_menu(self):
        """硬盘速度测试"""
        a = self.tool.run_command("lsblk -d -o NAME,TYPE,TRAN,PATH,SIZE,SERIAL,MODEL -J")
        self.log.msg(f"diskdata:{a}")
        try:
            data = json.loads(a)
        except json.JSONDecodeError as e:
            self.log.msg("解析硬盘信息失败，请检查lsblk命令输出是否正确。", outconsole=True)
            self.log.msg(f"错误:{e},data:{a}", outconsole=True)
            return []
        self.log.msg(f"diskdata3:{data}")

        choices: List[Choice] = []
        for dev in data.get("blockdevices", []):
            self.log.msg(f"diskdata2:{dev}")
            if dev.get("type") == "disk":
                if dev.get("tran") not in ["nvme", "sata", "sas"]:
                    continue
                name = dev.get("name")
                tran = dev.get("tran")
                size = dev.get("size")
                path = dev.get("path")
                sn = dev.get("serial")
                model = dev.get("model")
                self.log.msg(f"diskdata:{name}-{model}-{sn}-{tran}-{size}")
                choices.append(Choice(f"{name}-{model}-{sn}-{tran}-{size}", [path, sn, tran, size]))
                self.log.msg(f"choicesdata:{choices}")
        pro_disk = CheckboxPrompt("请选择测试硬盘(不要选有分区的盘):", choices=choices).prompt()
        for disk in pro_disk:
            #1 顺序写大文件
            cmd = f"fio --name=seqwrite --filename={disk.data[0]} --size=5G --rw=write --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #2 顺序读大文件
            cmd2 = f"fio --name=seqread --filename={disk.data[0]} --size=5G --rw=read --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #3 随机读 4K
            cmd3 = f"fio --name=randread --filename={disk.data[0]} --size=5G --rw=randread --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"
            #4 混合读写
            cmd4 = f"fio --name=randrw --filename={disk.data[0]} --size=5G --rw=randrw --rwmixread=70 --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"

            self.log.msg("正在测试 顺序写大文件", outconsole=True)
            self.run_command(cmd, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 顺序读大文件", outconsole=True)
            self.run_command(cmd2, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 随机读 4K", outconsole=True)
            self.run_command(cmd3, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 混合读写", outconsole=True)
            self.run_command(cmd4, logname=f"disk_speed_test_{disk.data[1]}")
        self.system_test_menu()
        return None
