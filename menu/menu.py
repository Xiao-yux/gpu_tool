import subprocess
import time
import pty
import select
import tty
import termios
from typing import Dict, List
import json
from noneprompt import ListPrompt, Choice, InputPrompt, CheckboxPrompt
import os
from menu.menuarg import MenuChess
from menu.menuarg_en import MenuChessEn
from core.i18n import get_i18n
from utils.installpack import InstallPack
from utils.tool import Tools
from core.log import get_logger
from testclass.testmanager import Manager
from core.terminal_manager import TerminalManager

class Menu:
    def __init__(self, path: Dict, i18n=None):
        # 根据语言设置选择合适的菜单
        if i18n is None:
            i18n = get_i18n()
        
        if i18n.language == 'en':
            self.menu_chess = MenuChessEn()
        else:
            self.menu_chess = MenuChess()
        self.path = path
        self.i18n = i18n
        self.tool = Tools(i18n)
        self.log = get_logger()
        self.install = InstallPack()
        self.log.msg('Menu initialized.')
        self.autotest = Manager(path)
        self.defcheckmsg = i18n.get('CHECK_MSG', "(按↑或↓移动，空格选择，回车确认)")
        self.terminal_manager = TerminalManager() 

    def main_menu(self):
        """主菜单"""
        pro = ListPrompt(self.i18n.get('MAIN_MENU_TITLE', "请选择操作:"), choices=self.menu_chess.main_menu,allow_filter=False,
                          error_message=self.i18n.get('NOT_IMPLEMENTED', "暂未完成")).prompt()
        if pro.data == "exit":
            os._exit(0)
        elif pro.data == "1":
            self.autotest.runmenu()
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
        self.main_menu()
    def system_set_menu(self):
        """BMC用户设置菜单"""
        pro = ListPrompt(self.i18n.get('SETTINGS_MENU_TITLE', "请选择设置项:"), choices=self.menu_chess.setsystem_menu, error_message=self.i18n.get('NOT_IMPLEMENTED', "暂未完成")).prompt()
        if pro.data == "exit":
            self.main_menu()
        elif pro.data == "1":
            self.apt_install_menu()
        elif pro.data == "2":
            self.bmc_set_menu()
        elif pro.data =="3":
            self.download_gpu()
        elif pro.data == "4":
            self.rtt_memu()
        self.log.msg(f'用户选择BMC用户设置菜单: {pro}')
        self.main_menu()
    def rtt_memu(self):
        fd = f"\'{self.log.get_log_file()}/fd\'"
        p = ListPrompt(self.i18n.get('SELECT', "请选择:"),choices=self.menu_chess.sys_tool_menu).prompt()
        if p.data == "1":
            a = os.path.exists(fd)
            self.log.msg(f"{fd} is exist {a} \n",outconsole=True)
            self.tool.check_fd_log(fd)

        self.main_menu()

    def bmc_set_menu(self):
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.bmc_set_menu,
                         validator=lambda x: x != self.menu_chess.bmc_set_menu[1], error_message="暂未完成").prompt()
        if pro.data == "exit":
            self.main_menu()
        elif pro.data == "1":
            self.tool.set_bmc_dhcp()
        cmd = f"ipmitool user {pro.data}"
        self.log.msg(f'用户选择BMC用户设置菜单: {pro}')
        self.main_menu()

    def download_gpu(self):
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"),choices=self.menu_chess.download_gpu).prompt()
        if pro.data == "exit":
            self.main_menu()
        if pro.data == "1":
            self.install.download_gpu_burn(self.path["download"])
        if pro.data == "2":
            self.install.download_nccl_test(self.path["download"])
        if pro.data == "3":
            self.install.download_nvband(self.path["download"])
        if pro.data == "4":
            self.install.download_p2p(self.path["download"])
        self.system_set_menu()


    def apt_install_menu(self):
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"),choices=self.menu_chess.apt_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            self.main_menu()
        if pro.data == "1":
            self.log.msg("安装cuda_keyring")
            self.install.apt_install_cuda_keyring()
        if pro.data == "2":
            self.log.msg("安装nvidia驱动和cuda")
            self.install.apt_install_nvidia_pack()
        if pro.data == "3":
            self.log.msg("安装mlnx 驱动")
            self.install.apt_install_mlnx_ofed_linux()
        if pro.data == "4":
            self.log.msg("安装DOCA")
            self.install.apt_install_doca()
        if pro.data == "5":
            self.log.msg("安装DCGMI")
            self.install.apt_install_dcgm()
        if pro.data == "6":
            self.log.msg("安装libnccl")
            self.install.apt_install_libnccl()
        if pro.data == "7":
            self.install.apt_install_systest()
        self.apt_install_menu()
    def gpu_test_menu(self):
        """GPU测试菜单"""
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.gpu_test_menu).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            self.fd_menu()
        elif pro.data == "2":
            self.gpu_burn_menu()
        elif pro.data == "3":
            self.dcgmi_menu()
        elif pro.data == "4":
            a = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.nvband_menu).prompt()
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
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.system_menu,allow_filter=False).prompt()
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
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.dcgm_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            self.gpu_test_menu()
        cmd = f"dcgmi {pro.data}"
        self.log.msg(f'用户选择DCGMI测试菜单: {pro}')
        self.run_command(cmd, logname="dcgmi_test",path=self.log.get_log_file())
        self.main_menu()

    def gpu_burn_menu(self):
        """GPU烧机测试菜单"""
        pro = InputPrompt(self.i18n.get('INPUT_TIME_WITH_UNIT', "请输入时间-默认S(单位(秒/分/小时)-(S/M/H))-0是退出:  "),default_text="0").prompt()
        if pro == "0":
            self.gpu_test_menu()
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
            self.log.msg(self.i18n.get('INVALID_TIME_FORMAT', "无效的时间格式。请输入数字后跟 S(秒)、M(分)或 H(小时)。"), outconsole=True)
            self.gpu_test_menu()
            return 
        cmd = f"./{self.path['gpu_burn_exe']} {time}"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="gpu_burn_test")
        self.log.msg(f'用户选择GPU烧机测试菜单: {pro}')
        self.main_menu()

    def fd_menu(self):
        """Folding测试菜单"""
        cmd = f"{self.path['fd_path']}/{self.path['fd_exe']} "
        path = f"{self.path['fd_path']}"
        self.tool.check_fd_path(f"\'{self.log.get_log_file()}/fd\'")
        logname = self.log.create_log_file("fd_test")
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.fd_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            self.gpu_test_menu()
        if pro.data == "1":
            cmd += f"--no_bmc --level1 --log '{self.log.get_log_file()}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "2":
            cmd += f"--no_bmc --level2 --log '{self.log.get_log_file()}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "3":
            a = CheckboxPrompt("选择单项测试项目:", choices=self.menu_chess.fd_test_arg_menu,annotation=self.defcheckmsg).prompt()
            if not a:
                self.gpu_test_menu()
            cmd += f"--no_bmc {self.tool.fd_arg_chines(a)} --log '{self.log.get_log_file()}/fd'"
            self.log.msg(cmd)
            self.run_command(cmd, path, logname)
        elif pro.data == "4":
            arg = InputPrompt(f"请输入自定义参数: {cmd} [input] --log {self.log.get_log_file()}/fd").prompt()
            if not arg:
                self.gpu_test_menu()
            cmd += f"{arg} --log '{self.log.get_log_file()}/fd'"
            self.run_command(cmd, path, logname)
        self.log.msg(f'用户选择Folding测试菜单: {pro}')
        self.main_menu()

    def run_command(self, command: str, path: str = '/tmp', logname: str = "command", input_user=True):
        """运行命令并实时输出日志
        
        Args:
            command: 执行的命令
            path: 执行命令时的目录
            logname: 日志名称
            input_user: 是否需要用户按回车继续
        """
        if logname == "fd_test":
            if self.tool.check_fd_path(f"\'{self.log.get_log_file()}/fd\'"):
                self.tool.run_command(f"mv {self.log.get_log_file()}/fd {self.log.get_log_file()}/fd_$(date +%Y-%m-%d_%H-%M-%S)")
            self.tool.stop_nvidia_service()
            self.tool.stop_openvswitch()
            self.tool.rm_nvidia_mod()
            self.tool.rm_switch_mod()
            
        self.log.msg(f"执行命令: {command}", outconsole=True)
        try:
            
            # 使用TerminalManager在可用的TTY中执行命令
            try:

                # 在screen会话中执行命令
                screen_name = self.terminal_manager.execute_command(
                    command=command,
                    logname=logname,
                    path=path
                )

                self.log.msg(f"{self.i18n.get('SCREEN_SESSION_CREATED', 'Screen session created:')}: {screen_name}\n", logger_name=logname, outconsole=True)
                self.log.msg(f"{self.i18n.get('SCREEN_SESSION_VIEW', 'Use screen -r to view session')}: screen -r {screen_name}\n", logger_name=logname, outconsole=True)

            except RuntimeError as e:
                self.log.msg(f"{self.i18n.get('SCREEN_EXECUTION_FAILED', 'Screen execution failed:')} {e}, {self.i18n.get('USING_NORMAL_MODE', 'using normal mode to execute command')}", logger_name=logname, outconsole=True)
                os._exit(1)

            self.log.msg(self.i18n.get("SCREEN_SESSION_WAITING", "Screen session created in background, waiting for command to complete") + "\n", logger_name=logname)
            self.log.msg(f"{self.i18n.get('LOG_PATH', 'Log path:')}: {self.log.get_log_file()}/{logname}\n", outconsole=True)
            self.terminal_manager.wait_for_command_completion(screen_name)
            self.log.msg(self.i18n.get("COMMAND_COMPLETED", "Command execution completed, screen session retained, returning to main menu") + "\n", logger_name=logname)
            if input_user:
                input(self.i18n.get("PRESS_ENTER_CONTINUE", "Press Enter to continue..."))
            return
        except Exception as e:
            self.log.msg(f"{self.i18n.get('RUN_COMMAND_FAILED', 'Run command failed:')} {e}")
            print(f"{self.i18n.get('EXECUTION_FAILED', 'Execution failed:')} {e}")
        
        if input_user:
            input(self.i18n.get("PRESS_ENTER_CONTINUE", "Press Enter to continue..."))

    def nccl_menu(self):
        cmd = f"./{self.path['nccl_exe']} "
        path = f"{self.path['nccl_path']}"
        logname = self.log.create_log_file("nccl_test")
        cmd += f"-b 256M -e {self.tool.get_gpu_memory()} -f 2 -g {self.tool.get_gpu_count()}"
        self.run_command(cmd, path, logname)

    def system_test_menu(self):
        pro = ListPrompt(self.i18n.get('SELECT', "请选择:"), choices=self.menu_chess.sys_test_menu,allow_filter=False).prompt()
        if pro.data == "exit":
            self.main_menu()
        if pro.data == "1":
            a = InputPrompt("输入测试时间(秒),默认300秒:").prompt()
            if not a:
                a = "300"
            cmd = f"stress-ng --cpu 0 --cpu-method all --cache 0 --matrix 0 --memcpy 0 --mq 0 --pipe 0 --fork 0 --switch 0 --vm 0 --vm-bytes 2G --iomix 4 --iomix-bytes 1g --timeout {a}s  --metrics-brief --tz --perf --verify --times --log-file '{self.log.get_log_file()}/stress_ng.log'"
            self.run_command(cmd, logname="system_stress_test")
        if pro.data == "2":

            a = int(os.popen("export LC_ALL=C.UTF-8 && free -m | grep Mem | awk '{print ($2)}'").read())
            cmd = f"memtester {a - 4096}M 1"
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
            if not isinstance(a, str):
                a = str(a)
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

        if not choices:
            print("无 nvme,sata,sas硬盘。(usb会被排除)")
            return None


        pro_disk = CheckboxPrompt("请选择测试硬盘(不要选有分区的盘):", choices=choices,annotation=self.defcheckmsg).prompt()

        for disk in pro_disk:
            #1 顺序写大文件
            cmd = f"fio --name=seqwrite --filename={disk.data[0]} --size=5G --rw=write --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #2 顺序读大文件
            cmd2 = f"fio --name=seqread --filename={disk.data[0]} --size=5G --rw=read --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            #3 随机读 4K
            cmd3 = f"fio --name=randread --filename={disk.data[0]} --size=5G --rw=randread --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"
            #4 混合读写
            cmd4 = f"fio --name=randrw --filename={disk.data[0]} --size=5G --rw=randrw --rwmixread=70 --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"

            self.log.msg("正在测试 顺序写大文件\n", outconsole=True)
            self.run_command(cmd, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 顺序读大文件\n", outconsole=True)
            self.run_command(cmd2, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 随机读 4K\n", outconsole=True)
            self.run_command(cmd3, logname=f"disk_speed_test_{disk.data[1]}")
            self.log.msg("正在测试 混合读写\n", outconsole=True)
            self.run_command(cmd4, logname=f"disk_speed_test_{disk.data[1]}")
        self.system_test_menu()
        return None

    def job(self) -> None:
        """每 5 分钟会被调用的任务函数"""

        self.log.msg(self.tool.run_command("nvidia-smi"),logger_name="time_5_save_info")
