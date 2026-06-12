from gpu_tool.log.logger import get_logger
import subprocess

class run_command:
    def __init__(self):
        self.log = get_logger()
        
    def run(self, command,out=False):
        """运行命令"""
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if out:
            print(result.stdout)
        return result.stdout