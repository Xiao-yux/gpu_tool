import subprocess
from sys import argv


def run_fd(cmd,path):
    subprocess.run(f"cd {path} && bash {cmd}", shell=True,text=True)
    
    
if __name__ == '__main__':
    cmd = argv[2]
    path = argv[1]
    # for a in argv:
    #     print(a)
        
    print(f": cd {path} && bash {cmd} :")
    run_fd(cmd,path)
    