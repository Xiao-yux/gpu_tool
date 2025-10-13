from noneprompt import CancelledError, ListPrompt, Choice, InputPrompt,CheckboxPrompt
import time
import subprocess
from utils.putlin import SingleLineDisplay
import os

version = "1.0.3"


class Menu:
    def __init__(self,config):
        self.config = config.return_config()
        self.path= config.get_config_value("CONFIG")
        self.log = config.log
        self.tool = config.tool
        self.log.msg("初始化 CLI 菜单")
        self.disp = SingleLineDisplay("欢迎使用菜单...\n", show=True)
        self.disp.update(f"当前版本: {version}\n", show=True)
        self.tobak = self.main_menu  #上一级菜单
        self.torun = self.main_menu   #下一级菜单
        self.boxtxt = "空格键选择, 回车键确认, Ctrl+C 退出程序"
        self.is_gpu_available() #检查系统
    def main_menu(self):
        choices: list[Choice] = []
        choices.append(Choice("系统信息", "1"))
        choices.append(Choice("FD压测", "2"))
        choices.append(Choice("GPUburn压测", "3"))
        choices.append(Choice("Dcgmi测试", "4"))
        choices.append(Choice("Nccl测试", "5"))
        choices.append(Choice("关机", "6"))
        choices.append(Choice("退出", "7"))
        prompt = ListPrompt("请选择:",choices).prompt()

        if prompt.data == "1":
            self.torun = self.system_info
        elif prompt.data == "2":
            self.torun = self.fd_test
        elif prompt.data == "3":
            self.torun = self.gpu_burn_test
        elif prompt.data == "4":
            self.torun = self.dcgmi_test
        elif prompt.data == "5":
            self.torun = self.nccl_test
        elif prompt.data == "6":
            subprocess.run(['poweroff'])
        elif prompt.data == "7":
            os._exit(0)
        self.torun()
    def system_info(self):
        self.tobak = self.main_menu
        choices: list[Choice] = []
        choices.append(Choice("查看CPU 内存信息", "1"))
        choices.append(Choice("查看GPU信息", "2"))
        choices.append(Choice("查看硬盘网卡信息", "3"))
        choices.append(Choice("查看nvlink拓扑", "5"))
        choices.append(Choice("查看impi ip设置信息", "6"))
        choices.append(Choice("返回", "4"))
        prompt = ListPrompt("请选择:",choices).prompt()
        if prompt.data == "1":
            a = self.tool.get_sys_info()
        elif prompt.data == "2":
            a = self.tool.get_gpu_info()
        elif prompt.data == "3":
            a = self.tool.get_eth_info()
        elif prompt.data == "4":
            self.tobak()
        elif prompt.data == "5":
            a = os.popen("nvidia-smi topo -m").read()
        elif prompt.data == "6":
            a = os.popen("ipmitool lan print").read()
        print(a)
        self.log.msg(a,logger_name="sysinfo")
        input("按回车键返回菜单...")
        self.tobak()
    def fd_test(self):
        self.tobak = self.main_menu
        logname = "fieldiag.log"
        self.log.create_log_file(logname)
        fdpath = self.path["fd_path"]
        defarg = f"--no_bmc --log {self.log.get_log_file()}/fd"
        arg =f"{self.path['fd_exe']}"
        choices: list[Choice] = []
        choices.append(Choice("运行Level1 测试", "1"))
        choices.append(Choice("运行Level2 测试", "2"))
        choices.append(Choice("自定义参数测试", "3"))
        choices.append(Choice("返回", "4"))
        prompt = ListPrompt("请选择:",choices).prompt()
        if prompt.data == "1":
            cmd = f"{arg} --level1 {defarg}"
        elif prompt.data == "2":
            cmd = f"{arg} --level2 {defarg}"
        elif prompt.data == "3":
            a = self.fd_test_arg()
            self.log.msg(f"选择的自定义参数: {a}",logger_name="fieldiag")
            cmd = f"{arg} {a} --log {self.log.get_log_file()}/fd"
        elif prompt.data == "4":
            self.tobak()
        self.run_command(cmd,fdpath,logname)
    def fd_test_arg(self):
        self.tobak = self.fd_test
        arg = {
    "运行系统集成测试(--sit)": "--sit",
    "不运行任何BMC相关任务(--no_bmc)": "--no_bmc",
    "跳过运行测试前的操作系统检查(--skip_os_check)": "--skip_os_check",
    "遇到第一个错误时失败(--fail_on_first_error)": "--fail_on_first_error",
    "使用系统中预装的驱动(--skip_driver_load)": "--skip_driver_load",
    "通知diag内核处于锁定状态(--lockdown)": "--lockdown",
    "将--log文件夹打包为tgz(--tar_custom_log_dir)": "--tar_custom_log_dir",
    "仅在指定的NVSwitch设备上运行测试(--only_nvswitch_devs=<b:d.f>[,<b:d.f>...])": "--only_nvswitch_devs=",
    "仅在指定的GPU设备上运行测试(--only_gpu_devs=<b:d.f>[,<b:d.f>...])": "--only_gpu_devs=",
    "运行IST测试(--ist)": "--ist",
    "运行GPU现场诊断测试(--gpufielddiag)": "--gpufielddiag",
    "GPU现场诊断参数(--gpu_fd_args <args>)": "--gpu_fd_args",
    "禁用Pex检查(--disable_pex_checks)": "--disable_pex_checks",
    "启用DRA分析(--enable_dra)": "--enable_dra",
    "skucheck JSON文件的绝对路径(--sku_json <path>)": "--sku_json",
    "运行1级测试(--level1)": "--level1",
    "运行2级测试(--level2)": "--level2",
    "运行指定虚拟ID的测试(--test <vID>[,<vID>...])": "--test",
    "跳过指定虚拟ID的测试(--skip_tests <vID>[,<vID>...])": "--skip_tests",
    "返回" : "exit"
}
        choices: list[Choice] = []
        cmd=""
        for k,v in arg.items():
            choices.append(Choice(k,v))
        prompt = CheckboxPrompt("请选择自定义参数:",choices,default_select=[1,15],annotation=self.boxtxt).prompt()
        for i in prompt:
            self.log.msg(f"选择了参数: {i.name} {i.data}",logger_name="fieldiag")
            if i.data == "--only_nvswitch_devs=":
                a = InputPrompt("请输入指定的NVSwitch设备 (格式:b:d.f,b:d.f...):").prompt()
                i.data += f"{a}"
            if i.data == "--only_gpu_devs=":
                a = InputPrompt("请输入指定的GPU设备 (格式:b:d.f,b:d.f...):").prompt()
                i.data += f"{a}"
            if i.data == "--gpu_fd_args":
                a = InputPrompt("请输入GPU现场诊断参数:").prompt()
                i.data += f" {a}"
            if i.data == "--sku_json":
                a = InputPrompt("请输入skucheck JSON文件的绝对路径:").prompt()
                i.data += f" {a}"
            if i.data == "--test":
                a = InputPrompt("请输入要运行的虚拟ID (格式:vID,vID...):").prompt()
                i.data += f" {a}"
            if i.data == "--skip_tests":
                a = InputPrompt("请输入要跳过的虚拟ID (格式:vID,vID...):").prompt()
                i.data += f" {a}"
            if i.data == "exit":
                self.tobak()
                return
            cmd += i.data +" "
        return cmd
        
    def gpu_burn_test(self):
        self.tobak = self.main_menu
        choices: list[Choice] = []
        choices.append(Choice("10分钟", "600"))
        choices.append(Choice("30分钟", "1800"))
        choices.append(Choice("1小时", "3600"))
        choices.append(Choice("2小时", "7200"))
        choices.append(Choice("4小时", "14400"))
        choices.append(Choice("8小时", "28800"))
        choices.append(Choice("16小时", "57600"))
        choices.append(Choice("24小时", "86400"))
        choices.append(Choice("返回", "exit"))
        prompt = ListPrompt("请选择运行时间:",choices).prompt()
        if prompt.data == "exit":
            self.tobak()
            return
        logname = "gpuburn.log"
        self.log.create_log_file(logname)
        gpuburnpath = self.path["gpu_burn_path"]
        arg = f"{self.path['gpu_burn_exe']} {prompt.data} "
        self.run_command(arg,gpuburnpath,logname)
    def dcgmi_test(self):
        self.tobak = self.main_menu
        choices: list[Choice] = []
        choices.append(Choice("DCGMI 1级测试(系统验证，约几秒钟)", "diag -r 1"))
        choices.append(Choice("DCGMI 2级测试(扩展系统验证，约 2 分钟)", "diag -r 2"))
        choices.append(Choice("DCGMI 3级测试(系统硬件诊断，约 15 分钟)", "diag -r 3"))
        choices.append(Choice("DCGMI 4级测试(更长时间的系统硬件诊断)", "diag -r 4"))
        choices.append(Choice("DCGMI discovery", "discovery -l"))
        choices.append(Choice("自定义测试", "6"))
        choices.append(Choice("返回", "exit"))
        prompt = ListPrompt("请选择:",choices).prompt()
        if prompt.data == "6":
            print('''
        topo        GPU 拓扑信息（dcgmi topo -h 查看更多）
        stats       进程统计信息（dcgmi stats -h 查看更多）
        diag        系统验证/诊断（dcgmi diag -h 查看更多）
        policy      策略管理（dcgmi policy -h 查看更多）
        health      健康监控（dcgmi health -h 查看更多）
        config      配置管理（dcgmi config -h 查看更多）
        group       GPU 组管理（dcgmi group -h 查看更多）
        fieldgroup  字段组管理（dcgmi fieldgroup -h 查看更多）
        discovery   发现系统中的 GPU（dcgmi discovery -h 查看更多）
        introspect  收集 DCGM 本身的信息（dcgmi introspect -h 查看更多）
        nvlink      显示 NvLink 链路状态和错误计数（dcgmi nvlink -h 查看更多）
        dmon        GPU 统计监控（dcgmi dmon -h 查看更多）
        modules     控制并列出 DCGM 模块
        profile     控制并列出 DCGM 性能分析指标
        set         配置 hostengine 设置''')
            a = InputPrompt("请输入自定义参数: dcgmi ").prompt()
            arg = f"dcgmi {a}"
        elif prompt.data == "exit":
            self.tobak()
            return
        else:
            arg = f"dcgmi {prompt.data}"

        self.run_command(arg,logname="dcgmi")
    def is_gpu_available(self):
        """检查系统"""
        
       
        if not os.popen("lspci | grep -i nvidia").read():
            print("未检测到 GPU，部分功能将不可用")
            self.log.msg("未检测到 GPU，部分功能将不可用")
            
        if not os.path.exists("/usr/bin/nvidia-smi"):
            print("未检测到 nvidia-smi，请确保已正确安装 NVIDIA 驱动，部分功能将不可用")
            self.log.msg("未检测到 nvidia-smi，请确保已正确安装 NVIDIA 驱动，部分功能将不可用")
        #检测gpuburn
        
        if not os.path.exists(f"{self.path['gpu_burn_path']}/{self.path['gpu_burn_exe']}"):
            print(f"未检测到 {self.path['gpu_burn_path']}/{self.path['gpu_burn_exe']}，请确保已正确安装 gpu-burn，GPUburn 功能将不可用")
            self.log.msg(f"未检测到 {self.path['gpu_burn_exe']}，请确保已正确安装 gpu-burn，GPUburn 功能将不可用")
        #检测nccl
        if not os.path.exists(f"{self.path['nccl_path']}/{self.path['nccl_exe']}"):
            print(f"未检测到 {self.path['nccl_path']}/{self.path['nccl_exe']}，请确保已正确安装 NCCL，NCCL 测试功能将不可用")
            self.log.msg(f"未检测到 {self.path['nccl_exe']}，请确保已正确安装 NCCL，NCCL 测试功能将不可用")
        #检测fieldiag
        if not os.path.exists(f"{self.path['fd_path']}/{self.path['fd_exe']}"):
            print(f"未检测到 {self.path['fd_path']}/{self.path['fd_exe']}，请确保已正确安装 Fielddiag，FD 测试功能将不可用")
            self.log.msg(f"未检测到 {self.path['fd_exe']}，请确保已正确安装 Fielddiag，FD 测试功能将不可用")
        #检测dcgmi
        if not os.path.exists("/usr/bin/dcgmi"):
            print("未检测到 dcgmi，请确保已正确安装 DCGM，DCGMI 测试功能将不可用")
            self.log.msg("未检测到 dcgmi，请确保已正确安装 DCGM，DCGMI 测试功能将不可用")
        #检测nccllib
        if not os.popen("dpkg -l | grep -i libnccl2").read():
            print("未检测到 libnccl2，请确保已正确安装 NCCLlib，NCCL 测试功能将不可用")
            self.log.msg("未检测到 libnccl2，请确保已正确安装 NCCL，NCCL 测试功能将不可用")
        if not os.popen("dpkg -l | grep -i libnccl-dev").read():
            print("未检测到 libnccl-dev，请确保已正确安装 NCCLlib，NCCL 测试功能将不可用")
            self.log.msg("未检测到 libnccl-dev，请确保已正确安装 NCCL，NCCL 测试功能将不可用")
    def nccl_test(self):
        gpu_count = self.tool.get_gpu_count()
        arg = f"{self.path['nccl_exe']} -b 256M -e 20G -f 2 -g {gpu_count}"
        self.log.msg(f"检测到 GPU 数量: {gpu_count}",logger_name="nccl")
        if int(gpu_count) < 1:
            self.log.msg("未检测到 GPU，无法运行 NCCL 测试",logger_name="nccl")
            print("未检测到 GPU，无法运行 NCCL 测试")
            input("按回车键返回菜单...")
            self.tobak()
        self.run_command(arg,path=self.path["nccl_path"],logname="nccl")

    
    def run_command(self, command: str,path: str = None,logname: str = "command"):
        """运行命令并实时输出日志"""
        if path is None:
            print(f"执行命令: {command}")
            
        else:
            print(f"执行命令: {path}/{command}")
            command = f"{path}/{command}"
        try:
            self.log.create_log_file(logname)
            self.log.msg(f"执行命令: {command}",logger_name=logname)
            print("执行开始")
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将错误输出合并到标准输出
                text=True,
                cwd=path,
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
                    print(output.strip())
                    self.log.msg(output.strip(),logger_name=logname)  # 同时记录到日志
            return_code = process.poll()
            self.log.msg(f"命令执行结束, 返回码: {return_code}")
            print("执行结束")
            print(f"日志路径: {self.log.get_log_file()}/{logname}")
            # 按下回车继续
            if self.path['fd_exe'] in command:
                self.tool.rest_gpu_server()
            input("按回车键返回菜单...")
        except Exception as e:
            self.log.msg(f"运行命令失败: {e}")
            print(f"执行失败: {e}")

        
        self.tobak()
            
            
    def run(self):
        self.log.msg("运行主菜单")
        try:
            self.main_menu()
        except CancelledError:
            self.log.msg("用户取消了操作")
        except KeyboardInterrupt:
            self.log.msg("用户取消了操作")

        self.log.msg("程序已退出")