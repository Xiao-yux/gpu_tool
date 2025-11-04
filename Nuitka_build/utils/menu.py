from noneprompt import CancelledError, ListPrompt, Choice, InputPrompt,CheckboxPrompt
import time
import subprocess
import os
from utils.menuarg import MenuChess


class Menu:
    def __init__(self,config):
        self.config = config.return_config()
        self.path= config.get_config_value("CONFIG")
        self.log = config.log
        self.tool = config.tool
        self.log.msg("初始化 CLI 菜单")
        self.MenuChess = MenuChess()  #初始化菜单选项
        self.disp = config.display
        self.disp.update("欢迎使用 CLI 菜单\n")
        self.disp.update(f"当前版本: {self.path['version']}\n", show=True)
        self.tobak = self.main_menu  #上一级菜单
        self.torun = self.main_menu   #下一级菜单
        self.boxtxt = "空格键选择, 回车键确认, Ctrl+C 退出程序"
    def main_menu(self):
        choices: list[Choice] = self.MenuChess.main_menu
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
        elif prompt.data == "exit":
            os._exit(0)
        elif prompt.data == "8":
            self.torun = self.nvband_test
        elif prompt.data == "11":
            self.torun = self.set_system
        self.torun()
    def system_info(self):
        self.tobak = self.main_menu
        choices: list[Choice] = self.MenuChess.system_menu
        prompt = ListPrompt("请选择:",choices).prompt()
        if prompt.data == "1":
            a = self.tool.get_sys_info()
        elif prompt.data == "2":
            a = self.tool.get_gpu_info()
        elif prompt.data == "3":
            a = self.tool.get_eth_info()
        elif prompt.data == "exit":
            self.tobak()
        elif prompt.data == "5":
            a = os.popen("nvidia-smi topo -m").read()
        elif prompt.data == "6":
            a = os.popen("ipmitool lan print").read()
        self.log.msg(f"运行时系统信息:\n{a}",logger_name="run_system_info")
        print(a)
        input("按回车键返回菜单...")
        self.tobak()
    def fd_test(self):
        self.tobak = self.main_menu
        logname = "fieldiag.log"
        self.log.create_log_file(logname)
        fdpath = self.path["fd_path"]
        defarg = f"--no_bmc --log {self.log.get_log_file()}/fd"
        arg =f"{self.path['fd_exe']}"
        choices: list[Choice] = self.MenuChess.fd_menu
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
            a = CheckboxPrompt("请选择单项测试:",self.MenuChess.fd_test_arg_menu,annotation=self.boxtxt).prompt()
            cmd = f"{arg} --test="
            for i in a:
                if i.data == "exit":
                    self.tobak()
                    return
                self.log.msg(f"选择了参数: {i.name} {i.data}",logger_name="fieldiag")
                cmd += i.data +","
            cmd = cmd[:-1]  # 去除最后一个逗号
            cmd += f" --log {self.log.get_log_file()}/fd"
        elif prompt.data == "exit":
            self.tobak()
        self.run_command(cmd,fdpath,logname)
    def fd_test_arg(self):
        self.tobak = self.fd_test
        choices: list[Choice] = self.MenuChess.fd_args_menu
        cmd=""
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
                a = InputPrompt("请输入要运行的虚拟ID (格式: id1,id2...):").prompt()
                i.data += f"='{a}'"
            if i.data == "--skip_tests":
                a = InputPrompt("请输入要跳过的虚拟ID (格式:vID,vID...):").prompt()
                i.data += f"='{a}'"
            if i.data == "exit":
                self.tobak()
                return
            cmd += i.data +" "
        return cmd
        
    def gpu_burn_test(self):
        self.tobak = self.main_menu
        choices: list[Choice] = self.MenuChess.gpu_burn_menu
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
        choices: list[Choice] = self.MenuChess.dcgm_menu

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
    def nvband_test(self):
        self.tobak = self.main_menu
        choices: list[Choice] = self.MenuChess.nvband_menu
        prompt = ListPrompt("请选择测试项目:",choices,max_height=8).prompt()
        if prompt.data == "exit":
            self.tobak()
            return
        logname = "nvband"
        nvbandpath = self.tool.get_tmp_path() + "bash/nvbandwidth"
        if prompt.data == "-1":
            arg = f"{nvbandpath}"
        if prompt.data != "-1":
            arg = f"{nvbandpath} -t {prompt.data}"
        self.run_command(command=arg,logname=logname)
    def set_system(self):
        self.tobak = self.main_menu

        self.log.msg("进入系统设置菜单")
        print("系统设置菜单")
        choices: list[Choice] = self.MenuChess.setsystem_menu

        prompt = ListPrompt("请选择:",choices=choices,validator=lambda x: x != choices[1],error_message="暂不可用").prompt()

        if prompt.data == "1":
            self.tool.set_bmc_dhcp()
            self.log.msg("已设置BMC为DHCP获取IP地址")
            input("按回车键返回菜单...")
            self.tobak()
        elif prompt.data == "2":
            user = InputPrompt("请选择BMC用户名:").prompt()
            password = InputPrompt("请输入BMC新密码:").prompt()
            self.tool.set_bmc_password(user,password)
            input("按回车键返回菜单...")
            self.tobak()
        elif prompt.data == "exit":
            self.tobak()
    
    def nccl_test(self):
        gpu_count = self.tool.get_gpu_count()
        arg = f"{self.path['nccl_exe']} -b 256M -e 20G -f 2 -g {gpu_count}"
        self.log.create_log_file("nccl")
        print(f"检测到 GPU 数量: {gpu_count}")
        self.log.msg(f"检测到 GPU 数量: {gpu_count}",logger_name="nccl")
        if int(gpu_count) < 1:
            self.log.msg("未检测到 GPU，无法运行 NCCL 测试",logger_name="nccl")
            print("未检测到 GPU，无法运行 NCCL 测试")
            input("按回车键返回菜单...")
            self.tobak()
        self.run_command(arg,path=self.path["nccl_path"],logname="nccl")

    
    def run_command(self, command: str,path: str = None,logname: str = "command"):
        """运行命令并实时输出日志"""
        logname = self.log.create_log_file(logname)
        if path is None:
            print(f"执行命令: {command}")
            
        else:
            print(f"执行命令: {path}/{command}")
            command = f"{path}/{command}"
        try:
            
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