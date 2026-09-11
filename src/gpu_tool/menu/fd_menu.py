import os
import re

from config.model import PathConfig
from i18n.i18n import get_i18n
from log.logger import get_logger
from noneprompt import CheckboxPrompt, Choice, InputPrompt, ListPrompt
from runner.local import run_command


class FdMenu:
    def __init__(self,conifg:PathConfig):
        self.path = conifg.fd_path
        run = {}
        self.log = get_logger()
        self.i18n = get_i18n()
        self.defcheckinfo = self.i18n.get('check_info')
        if self.i18n.lang == 'en':
            from menu.menuarg_en import MenuChessEn
            self.menu_chess = MenuChessEn()
        else:
            from menu.menuarg import MenuChess
            self.menu_chess = MenuChess()
            
    def HGX_menu(self,path):
        fd_path = os.path.join(self.path, path)
        fd_exe = self.check_fd_exe(fd_path)
        cmd =f"./{fd_exe} "
        #print(f"fd_exe: {fd_exe}")
        logname = "fd_test"
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_menu(),allow_filter=False).prompt()
        #print(f"pro.data: {pro.data}")
        if fd_exe == "fieldiag.sh":
            if pro.data == "exit":
                return
            if pro.data == "1":
                cmd += f"--level1 --no_bmc "
            elif pro.data == "2":
                cmd += f"--level2 --no_bmc "
            elif pro.data == "3":
                a = CheckboxPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_test_arg_menu(),annotation=self.defcheckinfo).prompt()
                if not a:
                    return
                cmd += f"{self.fd_arg_chines(a)} --no_bmc "
                self.log.info(cmd)
            elif pro.data == "4":
                arg = InputPrompt(f"请输入自定义参数: {cmd}").prompt()
                if not arg:
                    return
                cmd += f"{arg}"
        run ={"cmd": cmd,"logname": logname,"path": fd_path}
        if fd_exe == "partnerdiag":
            if pro.data == "exit":
                return
            if pro.data == "1":
                cmd += f"--field --level1 --no_bmc "
            elif pro.data == "2":
                cmd += f"--field --level2 --no_bmc "
            elif pro.data == "3":
                a = CheckboxPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_test_arg_menu(),annotation=self.defcheckinfo).prompt()
                if not a:
                    return
                cmd += f"{self.fd_arg_chines(a)} --no_bmc "
                self.log.info(cmd)
            elif pro.data == "4":
                arg = InputPrompt(f"请输入自定义参数: {cmd} [input] ").prompt()
                if not arg:
                    return
                cmd += f"{arg}"
            run ={"cmd": cmd,"logname": logname,"path": fd_path}
        return run

        
    def B200_menu(self,path):
        fd_path = os.path.join(self.path, path)
        cmd = "./partnerdiag "
        logname = "fd_test"
        spik ="--skip_tests=ibstressmad,EyeGradeBgStop,ThetaBgStop,EyeGradeBgStart,ThetaBgStart"
        res = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_b200_menu(),allow_filter=False).prompt()
        if res.data == "exit":
            return
        if res.data == "1":
            cmd += f"--field --level1 {spik} --no_bmc "
        elif res.data == "2":
            cmd += f"--field --level2 {spik} --no_bmc "
        elif res.data == "3":
            print("未完成")
        elif res.data == "4":
            arg = InputPrompt(f"请输入自定义参数: {cmd} [input] ").prompt()
            if not arg:
                return
            cmd += f"{arg} "
        run ={"cmd": cmd,"logname": logname,"path": fd_path}
        return run

    def B300_menu(self,path):
        fd_path = os.path.join(self.path, path)
        cmd = "./partnerdiag "
        logname = "fd_test"
        spik = "--skip_tests=CX8IBconnectivity,ibstress"
        res = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_b200_menu(),allow_filter=False).prompt()
        if res.data == "exit":
            return
        if res.data == "1":
            cmd += f"--field --level1 {spik} --run_on_error --no_bmc "
        elif res.data == "2":
            cmd += f"--field --level2 {spik} --run_on_error --no_bmc "
        elif res.data == "3":
            print("未完成")
        elif res.data == "4":
            arg = InputPrompt(f"请输入自定义参数: {cmd} [input] ").prompt()
            if not arg:
                return
            cmd += f"{arg} "
        run ={"cmd": cmd,"logname": logname,"path": fd_path}
        return run
    
    def check_fd_path(self, path):
        return bool(os.path.exists(path) and os.listdir(path))
    
    def fd_arg_chines(self, chines):
        """fd 选择参数解析"""
        cmd = "--test="
        for i in chines:
            cmd += i.data + ","
        cmd = cmd[:-1]  # 去除最后一个逗号
        return cmd
    
    def check_fd_exe(self, path):
        h = ["fieldiag.sh","partnerdiag"]
        h_pattern = r'\b(' + '|'.join(h) + r')\b'
        for i in os.listdir(path):
            match = re.search(h_pattern, i)
            if match:
                return i
        return "fieldiag.sh"
    def check_fd_version(self, path):
        """检查fd目录下的版本返回 1,2,3
        1 : H 系列卡
        2 : B200 
        3 : B300 
        """
        h= ["h100","h200","h20","h800"]
        b200= ["spec_blackwell-hgx-8-gpu_field_level2.json","spec_blackwell-hgx-8-gpu_field_level1.json","sku_blackwell-hgx-8-gpu_field.json"]
        b300= ["b300","b300-nvl8"]
        fd_path = os.path.join(self.path, path)
        h_pattern = r'\b(' + '|'.join(h) + r')\b'
        b200_pattern = r'\b(' + '|'.join(b200) + r')\b'
        b300_pattern = r'\b(' + '|'.join(b300) + r')\b'
        for i in os.listdir(fd_path):
            #print(i)
            match = re.search(h_pattern, i)
            if match:
                #print(f"匹配成功，匹配到的内容是: {match.group()}") 
                return 1
            if re.search(b200_pattern, i):
                #print(f"匹配成功，匹配到的内容是: {i}") 
                return 2
            if re.search(b300_pattern, i):
                #print(f"匹配成功，匹配到的内容是: {i}") 
                return 3

    def main_menu(self):
        list_file = [name for name in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, name))]
        #print(list_file)
        choices: list[Choice] =[]
        for i in list_file:
            choices.append(Choice(i, i))
        prompt = ListPrompt("请选择要执行的FD测试:", choices)
        res = prompt.prompt()
        #print(f"您选择了: {res}")
        version = self.check_fd_version(res.data)
        #print(version)
        if os.path.exists(os.path.join(self.log.paths.run, "fd")):
            os.system(f"mv {os.path.join(self.log.paths.run, 'fd')} {os.path.join(self.log.paths.run, 'fd')}_{self.log.get_time()}")
            return {}
        if version == 1:
            return self.HGX_menu(res.data)
        elif version == 2:
            return self.B200_menu(res.data)
        elif version == 3:
            return self.B300_menu(res.data)
        return {}


    

if __name__ == "__main__":
    # fd = FdMenu()
    # fd.main_menu()
    pass