import os
import subprocess
import toml

class FRPRun:
    def __init__(self):
        self.con = []
        self.runshell = None
        self.path = f"{os.path.join(os.path.dirname(__file__))}/frp_0.63.0_linux_amd64"
        self.clean_config()
        # self.edit_config("192.168.1.1",888)

    def run(self, ip: str, port: int):
        cmd = f"{self.path}/frpc -c {self.path}/frpc.toml"
        self.edit_config(ip, port)
        
        if self.runshell is not None:
            print("已经在运行了")
            a= self.stop()
            print(f"正在重新启动,{a}")
            
        self.runshell = subprocess.Popen(cmd, shell=True)
    
    def edit_config(self, ip: str, port: int):
        tomlpath= f"{self.path}/frpc.toml"
        if not os.path.exists(tomlpath):
            print("配置文件不存在")
            return
        a = toml.load(tomlpath)
        a[self.rand_name()] = {
            "name": f"{ip}",
            "type": "tcp",
            "localIP": f"{ip}",
            "localPort": f"{port}",
            "remotePort": f"{self.rand_prot()}"
        }
        with open(tomlpath, 'w') as f:
            toml.dump(a, f)
        f.close()
        return True
    
    def stop(self):
        if self.runshell is not None:
            self.runshell.terminate()
            self.runshell = None
        return True
    def rand_name(self) -> str:
        import random
        import string
        a = "web-"+''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.con.append(a)
        return a
    
    def rand_prot(self) -> int:
        """生成随机端口号20000-25000之间，并且不重复
        """
        import random
        port = random.randint(20000, 25000)
        return port
    
    def clean_config(self):
        """程序启动时清理上次的 web-开头的配置项
        """
        a = """serverAddr = "yuuur.cn"
serverPort = 7000
user = "houmao-web"

[auth]
method = "token"
token = "1409109991"

[log]
level = "info"
maxDays = 5
to = ""

[transport]
protocol = "tcp"
tcpMux = true"""
        tomlpath= f"{self.path}/frpc.toml"
        with open(tomlpath, 'w') as f:
            f.write(a)
        f.close()
        return True
    
FRPRun()