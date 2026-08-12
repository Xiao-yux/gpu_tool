import subprocess

# class run_command:
#     def __init__(self):
#         self.log = get_logger()
#         pass



def run_command(command,out=False):
    """运行命令"""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if out:
        print(result.stdout)
    return result.stdout