from pathlib import Path
from typing import List
import json
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from i18n.i18n import get_i18n
from utils.installpack import InstallPack
from utils.tool import Tools
from log.logger import get_logger
from runner.screen import TerminalManager
from config.model import PathConfig
from utils.nvsmi import nvsmi
from utils.ipmitool import ipmitools
from bash.bash import InfoBash

class Menu:
    def __init__(self, path: PathConfig):
        # 根据语言设置选择合适的菜单
        i18n = get_i18n()
        if i18n.lang == 'en':
            from menu.menuarg_en import MenuChessEn
            self.menu_chess = MenuChessEn()
        else:
            from menu.menuarg import MenuChess
            self.menu_chess = MenuChess()
        self.path = path
        self.i18n = i18n
        self.tool = Tools()
        self.log = get_logger()
        self.install = InstallPack()
        self.log.info('Menu initialized.')
        # self.autotest = Manager(path)
        self.defcheckinfo = i18n.get('check_info')
        self.gpu = nvsmi()
        self.ipmi = ipmitools()
        self.terminal_manager = TerminalManager()
        self.info = InfoBash() 

    def main_menu(self):
        """主菜单"""
        while True:
            pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.main_menu,allow_filter=False,
                            error_message=self.i18n.get('not_implemented')).prompt()
            if pro.data == "exit":
                os._exit(0)
            elif pro.data == "1":
                # self.autotest.runmenu()
                return
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

            self.log.info(f'用户选择: {pro}')
        return
    def system_set_menu(self):
        """设置菜单"""
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.setsystem_menu, error_message=self.i18n.get('not_implemented')).prompt()
        if pro.data == "exit":
            return
        elif pro.data == "1":
            self.apt_install_menu()
        elif pro.data == "2":
            self.bmc_set_menu()
        elif pro.data =="3":
            self.download_gpu()
        elif pro.data == "4":
            self.rtt_memu()
        self.log.info(f'用户选择BMC用户设置菜单: {pro}')
        return
    def rtt_memu(self):
        fd = f"\'{self.log.paths.run}/fd\'"
        p = ListPrompt(self.i18n.get('select_option'),choices=self.menu_chess.sys_tool_menu).prompt()
        if p.data == "1":
            a = os.path.exists(fd)
            self.log.info(f"{fd} is exist {a} \n",console=True)
            self.tool.check_fd_log(fd)

        return

    def bmc_set_menu(self):
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.bmc_set_menu,
                         validator=lambda x: x != self.menu_chess.bmc_set_menu[1], error_message=self.i18n.get('not_implemented')).prompt()
        if pro.data == "exit":
            return
        elif pro.data == "1":
            self.tool.set_bmc_dhcp()
        # cmd = f"ipmitool user {pro.data}"
        self.log.info(f'用户选择BMC用户设置菜单: {pro}')
        return

    def download_gpu(self):
        pro = ListPrompt(self.i18n.get('select_option'),choices=self.menu_chess.download_gpu).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            self.install.download_gpu_burn(self.path.download)
        if pro.data == "2":
            self.install.download_nccl_test(self.path.download)
        if pro.data == "3":
            self.install.download_nvband(self.path.download)
        if pro.data == "4":
            self.install.download_p2p(self.path.download)
        self.system_set_menu()


    def apt_install_menu(self):
        while True:
            pro = ListPrompt(self.i18n.get('select_option'),choices=self.menu_chess.apt_menu,allow_filter=False).prompt()
            if pro.data == "exit":
                break
            if pro.data == "1":
                self.log.info("安装cuda_keyring")
                self.install.apt_install_cuda_keyring()
            if pro.data == "2":
                self.log.info("安装nvidia驱动和cuda")
                self.install.apt_install_nvidia_pack()
            if pro.data == "3":
                self.log.info("安装mlnx 驱动")
                self.install.apt_install_mlnx_ofed_linux()
            if pro.data == "4":
                self.log.info("安装DOCA")
                self.install.apt_install_doca()
            if pro.data == "5":
                self.log.info("安装DCGMI")
                self.install.apt_install_dcgm()
            if pro.data == "6":
                self.log.info("安装libnccl")
                self.install.apt_install_libnccl()
            if pro.data == "7":
                self.install.apt_install_systest()
        return
    def gpu_test_menu(self):
        """GPU测试菜单"""
        while True:
            pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.gpu_test_menu).prompt()
            if pro.data == "exit":
                break
            if pro.data == "1":
                self.fd_menu()
            elif pro.data == "2":
                self.gpu_burn_menu()
            elif pro.data == "3":
                self.dcgmi_menu()
            elif pro.data == "4":
                a = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.nvband_menu).prompt()
                cmd = "./nvbandwidth"
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
                logname = "p2pBandwidthLatencyTest_test"
                self.run_command(cmd, path, logname)
            self.log.info(f'用户选择GPU测试菜单: {pro}')
        return

    def sys_info_menu(self):
        """系统信息菜单"""
        a =0
        while True:
            pro = ListPrompt(self.i18n.get('select_option'),default_select=a, choices=self.menu_chess.system_menu,allow_filter=False).prompt()
            if pro.data == "exit":
                break
            if pro.data == "1": #全部信息
                self.log.info(f"系统信息\n{self.info.get_sys_info()}", console=True)
                self.log.info(f"CPU信息\n{self.info.get_cpu_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
                self.log.info(f"内存信息\n{self.info.get_memory_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
                self.log.info(f"硬盘信息\n{self.info.get_disk_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
                self.log.info(f"网卡信息\n{self.info.get_net_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
                gpu ,ecc =self.info.get_gpu_info()
                self.log.info(f"GPU信息\n{gpu}", console=True)
                self.log.info(f"ECC信息\n{ecc}", console=True)
            elif pro.data == "2":  #系统信息
                a=1
                self.log.info(f"系统信息\n{self.info.get_sys_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "3":  #CPU 信息
                a=2
                self.log.info(f"CPU信息\n{self.info.get_cpu_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "4":  # 内存信息
                a=3
                self.log.info(f"内存信息\n{self.info.get_memory_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "5": # 硬盘信息
                a=4
                self.log.info(f"硬盘信息\n{self.info.get_disk_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "6":  # 网卡信息
                a=5
                self.log.info(f"网卡信息\n{self.info.get_net_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "7":  # GPU信息
                a=6
                self.log.info(f"GPU信息\n{self.info.get_gpu_info()}", console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "8": # IPMIlan信息
                a=7
                self.log.info(self.ipmi.lan(), console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            elif pro.data == "9": # fru
                a=8
                self.log.info(self.ipmi.fru(), console=True)
                input(f"{self.i18n.get('press_enter_continue')}")
            self.log.info(f'用户选择: {pro}')

        return

    def dcgmi_menu(self):
        """DCGMI测试菜单"""
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.dcgm_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            return
        cmd = f"dcgmi {pro.data}"
        self.log.info(f'用户选择DCGMI测试菜单: {pro}')
        self.run_command(cmd, logname="dcgmi_test",path=self.log.paths.run)
        self.main_menu()

    def gpu_burn_menu(self):
        """GPU烧机测试菜单"""
        pro = InputPrompt(self.i18n.get('input_time_gpu_burn'),default_text="0").prompt()
        if pro == "0":
            return
        
        # 解析时间输入
        time_str = pro.strip().upper()
        try:
            if time_str.endswith('S'):
                time = int(time_str[:-1])
            elif time_str.endswith('M'):
                time = int(time_str[:-1]) * 60
            elif time_str.endswith('H'):
                time = int(time_str[:-1]) * 3600
            else:
                # 默认为秒
                time = int(time_str)
        except (ValueError, IndexError):
            self.log.info(self.i18n.get('invalid_time_format'), console=True)
            self.gpu_test_menu()
            return 
        cmd = f"./{self.path.gpu_burn_exe} {time}"
        self.run_command(cmd, path=self.path.gpu_burn_path, logname="gpu_burn_test")
        self.log.info(f'用户选择GPU烧机测试菜单: {pro}')
        self.main_menu()

    def fd_menu(self):
        """Folding测试菜单"""
        cmd = f"{self.path.fd_path}/{self.path.fd_exe} "
        path = f"{self.path.fd_path}"
        self.tool.check_fd_path(f"\'{self.log.paths.run}/fd\'")
        logname = "fd_test"
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.fd_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            cmd += f"--no_bmc --level1 --log '{self.log.paths.run}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "2":
            cmd += f"--no_bmc --level2 --log '{self.log.paths.run}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "3":
            a = CheckboxPrompt(self.i18n.get('select_option'), choices=self.menu_chess.fd_test_arg_menu,annotation=self.defcheckinfo).prompt()
            if not a:
                self.gpu_test_menu()
            cmd += f"--no_bmc {self.tool.fd_arg_chines(a)} --log '{self.log.paths.run}/fd'"
            self.log.info(cmd)
            self.run_command(cmd, path, logname)
        elif pro.data == "4":
            arg = InputPrompt(f"请输入自定义参数: {cmd} [input] --log {self.log.paths.run}/fd").prompt()
            if not arg:
                self.gpu_test_menu()
            cmd += f"{arg} --log '{self.log.paths.run}/fd'"
            self.run_command(cmd, path, logname)
        self.log.info(f'用户选择Folding测试菜单: {pro}')
        self.main_menu()

    def run_command(self, command: str, path: str | Path = '/tmp', logname: str = "command", input_user=True):
        """运行命令并实时输出日志
        
        Args:
            command: 执行的命令
            path: 执行命令时的目录
            logname: 日志名称
            input_user: 是否需要用户按回车继续
        """
        if logname == "fd_test":
            if self.tool.check_fd_path(f"\'{self.log.paths.run}/fd\'"):
                self.tool.run_command(f"mv {self.log.paths.run}/fd {self.log.paths.run}/fd_$(date +%Y-%m-%d_%H-%M-%S)")
            self.tool.stop_nvidia_service()
            # self.tool.stop_openvswitch()
            self.tool.rm_nvidia_mod()
            # self.tool.rm_switch_mod()
            
        self.log.info(f"执行命令: {command}", console=True)
        try:
            
            # 使用TerminalManager在可用的TTY中执行命令
            try:

                # 在screen会话中执行命令
                screen_name = self.terminal_manager.execute_command(
                    command=command,
                    logname=logname,
                    path=path
                )
                if logname != "fd_test":
                    self.log.info(f"{self.i18n.get('screen_created')}: {screen_name}\n", file_name=logname, console=True)


            except RuntimeError as e:
                self.log.info(f"{self.i18n.get('screen_execution_failed')} {e}", file_name=logname, console=True)
                os._exit(1)

            self.log.info(self.i18n.get("screen_session_created") + "\n", file_name=logname)
            self.log.info(f"{self.i18n.get('log_path')}: {self.log.paths.run}/{logname}\n", console=True)
            self.terminal_manager.wait_for_command_completion(screen_name)
            self.log.info(self.i18n.get("command_end") + "\n", file_name=logname)
            if input_user:
                input(self.i18n.get("press_enter_continue"))
            return
        except Exception as e:
            self.log.info(f"{self.i18n.get('run_command')} {e}")
            print(f"{self.i18n.get('ececution_failed')} {e}")
        
        if input_user:
            input(self.i18n.get("press_enter_continue"))

    def nccl_menu(self):
        cmd = f"./{self.path.nccl_exe} "
        path = f"{self.path.nccl_path}"
        logname = "nccl_test"
        cmd += f"-b 256M -e {self.tool.get_gpu_memory()} -f 2 -g {self.tool.get_gpu_count()}"
        self.run_command(cmd, path, logname)

    def system_test_menu(self):
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.sys_test_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            a = InputPrompt("输入测试时间(秒),默认300秒:").prompt()
            if not a:
                a = "300"
            cmd = f"stress-ng --cpu 0 --cpu-method all --cache 0 --matrix 0 --memcpy 0 --mq 0 --pipe 0 --fork 0 --switch 0 --vm 0 --vm-bytes 2G --iomix 4 --iomix-bytes 1g --timeout {a}s  --metrics-brief --tz --perf --verify --times --log-file '{self.log.paths.run}/stress_ng.log'"
            self.run_command(cmd, logname="system_stress_test")
        if pro.data == "2":

            a = int(os.popen("export LC_ALL=C.UTF-8 && free -m | grep Mem | awk '{print ($2)}'").read())
            cmd = f"memtester {a - 2048}M 1"
            self.log.info(cmd)
            self.run_command(cmd, logname="memtester_test")
        if pro.data == "3":
            self.disk_speed_test_menu()
        return

    def disk_speed_test_menu(self):
        """硬盘速度测试"""
        a = self.tool.run_command("lsblk -d -o NAME,TYPE,TRAN,PATH,SIZE,SERIAL,MODEL -J")
        
        self.log.info(f"diskdata:{a}")
        try:
            if not isinstance(a, str):
                a = str(a)
            data = json.loads(a)
        except json.JSONDecodeError as e:
            self.log.info("解析硬盘信息失败，请检查lsblk命令输出是否正确。", console=True)
            self.log.info(f"错误:{e},data:{a}", console=True)
            return []
        self.log.info(f"diskdata3:{data}")

        choices: List[Choice] = []
        for dev in data.get("blockdevices", []):
            self.log.info(f"diskdata2:{dev}")
            if dev.get("type") == "disk":
                if dev.get("tran") not in ["nvme", "sata", "sas"]:
                    continue
                name = dev.get("name")
                tran = dev.get("tran")
                size = dev.get("size")
                path = dev.get("path")
                sn = dev.get("serial")
                model = dev.get("model")
                self.log.info(f"diskdata:{name}-{model}-{sn}-{tran}-{size}")
                choices.append(Choice(f"{name}-{model}-{sn}-{tran}-{size}", [path, sn, tran, size]))
                self.log.info(f"choicesdata:{choices}")

        if not choices:
            print("无 nvme,sata,sas硬盘。(usb会被排除)")
            return None


        pro_disk = CheckboxPrompt(f"{self.i18n.get('select_disk')}", choices=choices,annotation=self.defcheckinfo).prompt()

        for disk in pro_disk:
            #1 顺序写大文件
            cmd = f"fio --name=seqwrite --filename={disk.data[0]} --size=5G --rw=write --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #2 顺序读大文件
            cmd2 = f"fio --name=seqread --filename={disk.data[0]} --size=5G --rw=read --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #3 随机读 4K
            cmd3 = f"fio --name=randread --filename={disk.data[0]} --size=5G --rw=randread --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"
            #4 混合读写
            cmd4 = f"fio --name=randrw --filename={disk.data[0]} --size=5G --rw=randrw --rwmixread=70 --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"

            self.log.info("正在测试 顺序写大文件\n", console=True)
            self.run_command(cmd, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.info("正在测试 顺序读大文件\n", console=True)
            self.run_command(cmd2, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.info("正在测试 随机读 4K\n", console=True)
            self.run_command(cmd3, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.info("正在测试 混合读写\n", console=True)
            self.run_command(cmd4, logname=f"disk_speed_test_{disk.data[1]}")
        return None

    def job(self) -> None:
        """每 5 分钟会被调用的任务函数"""

        self.log.info(self.gpu.get_gpu_info(), file_name="time_5_save_info")
