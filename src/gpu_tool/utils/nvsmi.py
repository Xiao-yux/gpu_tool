from runner.local import run_command
from i18n.i18n import get_i18n

class nvsmi:
    def __init__(self):
        self.i18n = get_i18n()

    def get_gpu_info(self,arg =""):
        """获取GPU信息 nvidia-smi {arg}"""
        return run_command(f"nvidia-smi {arg}")

    def get_gpu_topo(self):
        """获取GPU拓扑结构"""
        return run_command("nvidia-smi topo -m")

    def get_gpu_info_by_id(self, id):
        ...

    def get_gpu_info_by_name(self, name):
        ...

    def get_gpu_info_by_uuid(self, uuid):
        ...

    def get_gpu_info_by_serial(self, serial):
        pass
