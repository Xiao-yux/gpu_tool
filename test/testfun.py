

class TestFun:

    def __init__(self,config):
        self.config = config

    def fieldiag_level1(self,no_bmc = True) -> bool:
        cmd = f"{self.config['fd_exe']} --level1"
        if no_bmc:
            cmd += " --no_bmc"

