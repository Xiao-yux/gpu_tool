
import tqdm
import utils.tool as utils
from log.logger import get_logger
from runner.local import run_command
class InstallPack:
    def __init__(self):
        self.tool = utils.Tools()
        self.log = get_logger()
        self.logname = "install_pack"
    def apt_install_nvidia_pack(self):
        self.apt_update_package()
        pack = ['nvidia-driver-580-server','nvidia-fabricmanager-580','cuda-toolkit-13','nvidia-imex-580']
        tq = tqdm.tqdm(pack)
        for pack in tq:
            cmd = f'sudo apt-get install -y {pack}'
            self.log.info(f"正在执行{cmd}", file_name=self.logname, console=True)
            self.log.info(run_command(cmd,out=True), file_name=self.logname)

    def apt_install_systest(self):
        """安装系统测试工具(fio,stress,memtester)"""
        pack = ['fio','stress','stress-ng','memtester']
        for pack in tqdm.tqdm(pack):
            cmd = f'sudo apt-get install -y {pack}'
            self.log.info(f"正在安装{cmd}", file_name=self.logname, console=True)
            self.log.info(run_command(cmd, out=True), file_name=self.logname)

    def download_gpu_burn(self,path):
        url = "https://github.com/wilicc/gpu-burn"
        cmd = f"git clone {url}"
        print(f"下载位置: {path}")
        self.tool.run_command(cmd,out=True,path=path)

    def download_nccl_test(self,path):
        url = "https://github.com/NVIDIA/nccl-tests"
        cmd = f"git clone {url}"
        print(f"下载位置: {path}")
        self.tool.run_command(cmd, out=True, path=path)

    def download_nvband(self, path):
        url = "https://github.com/NVIDIA/nvbandwidth"
        cmd = f"git clone {url}"
        print(f"下载位置: {path}")
        self.tool.run_command(cmd, out=True, path=path)



    def download_p2p(self, path):
        url = "https://github.com/NVIDIA/cuda-samples"
        cmd = f"git clone {url}"
        print(f"下载位置: {path}")
        self.tool.run_command(cmd, out=True, path=path)
        print("需自行编译，编译后p2pBandwidthLatencyTest 程序位置在： cuda-samples/build/Samples/5_Domain_Specific/p2pBandwidthLatencyTest")

    def apt_install_dcgm(self):
        self.apt_update_package()
        cmd = "sudo apt-get install -y datacenter-gpu-manager-4-cuda-all"
        self.log.info(run_command(cmd,out=True), file_name=self.logname )

    def apt_install_libnccl(self):
        self.apt_update_package()
        cmd = 'sudo apt-get install -y libnccl2 libnccl-dev'
        self.log.info(run_command(cmd, out=True), file_name=self.logname)

    def apt_install_cuda_keyring(self):
        url = 'https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb'
        cmd = f'wget -c -O ~/cuda-keyring_1.1-1_all.deb {url}'
        cmd2 = 'dpkg -i ~/cuda-keyring_1.1-1_all.deb'
        self.log.info(run_command(cmd, out=True), file_name=self.logname)
        self.log.info(run_command(cmd2, out=True), file_name=self.logname)

    def apt_install_doca(self):
        self.apt_update_package()
        url = 'https://content.mellanox.com/DOCA/DOCA_v3.1.0/host/doca-host_3.1.0-091000-25.07-ubuntu2204_amd64.deb'
        cmd = f'wget -c -O ~/doca.deb {url}'
        tar = 'dpkg -i ~/doca.deb'
        self.log.info(run_command(cmd, out=True), file_name=self.logname)
        self.log.info(run_command(tar, out=True), file_name=self.logname)
        self.log.info(run_command('apt install -y doca-all', out=True), file_name=self.logname)

    def apt_install_mlnx_ofed_linux(self):
        """ubuntu22 MLNX_OFED_LINUX"""
        self.apt_update_package()
        url = 'https://content.mellanox.com/ofed/MLNX_OFED-24.10-3.2.5.0/MLNX_OFED_LINUX-24.10-3.2.5.0-ubuntu22.04-x86_64.tgz'
        cmd = f'wget -c -O ~/MLNX.tgz {url}'
        #解压
        tar = 'cd ~ && tar -zxvf ~/MLNX.tgz'
        #MLNX依赖
        cmd2 = ('apt-get install -y gcc g++ make perl autoconf dkms libltdl-dev m4 gfortran automake swig tk quilt '
                'debhelper libnl-route-3-dev graphviz flex bison libgfortran5 tcl libfuse2 pkg-config chrpath '
                'libnl-3-dev autotools-dev linux-headers-$(uname -r)')
        cmd3 = 'cd ~/MLNX && ./mlnxofedinstall --force'
        a = [cmd,tar,cmd2,cmd3]
        for i in a:
            b= self.tool.run_command(i,out=True)
            self.log.info(b, file_name=self.logname)


    def apt_update_package(self):
        """更新软件包"""
        cmd = 'sudo apt-get update'
        print("正在 apt-get update")
        self.tool.run_command(cmd)