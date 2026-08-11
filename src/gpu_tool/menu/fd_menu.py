import os
import time

from config.model import PathConfig
from i18n.i18n import get_i18n
from log.logger import get_logger
from noneprompt import CheckboxPrompt, Choice, InputPrompt, ListPrompt
from runner.local import run_command


class FdMenu:
    def __init__(self, config: PathConfig):
        self.path = config
        self.log = get_logger()
        self.i18n = get_i18n()

    def HGX_menu(self):
        HGX_version = "629-24287-XXXX-FLD-41741"
        fd_exe = "fieldiag.sh"
        cmd = f"{self.path.fd_path}/{fd_exe} "
        path = f"{self.path.fd_path}"
        if self.check_fd_path(f"\'{self.log.paths.run}/fd\'"): 
            #备份目录
            run_command(f"mv \'{self.log.paths.run}/fd\' \'{self.log.paths.run}/fd_{time.strftime('%Y%m%d%H%M%S')}\'")
            
        logname = "fd_test"
        pro = ListPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_menu(),allow_filter=False).prompt()
        if pro.data == "exit":
            return
        if pro.data == "1":
            cmd += f"--no_bmc --level1 --log '{self.log.paths.run}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "2":
            cmd += f"--no_bmc --level2 --log '{self.log.paths.run}/fd'"
            self.run_command(cmd, path, logname)
        elif pro.data == "3":
            a = CheckboxPrompt(self.i18n.get('select_option'), choices=self.menu_chess.get_fd_test_arg_menu(),annotation=self.defcheckinfo).prompt()
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
        pass
    
    def B200_menu(self):
        pass
    
    def B300_menu(self):
        pass
    
    def check_fd_path(self, path):
        return bool(os.path.exists(path) and os.listdir(path))