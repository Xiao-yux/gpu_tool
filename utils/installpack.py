
import tqdm
import utils.tool
class InstallPack:
    def __init__(self,log):
        self.tool = utils.tool.Tools()
        self.log = log
        self.logname = "install_pack"
    def apt_install_nvidia_pack(self):
        self.apt_update_package()
        pack = ['nvidia-driver-580-server','nvidia-fabricmanager-580','cuda-toolkit-13','nvidia-imex-580']
        tq = tqdm.tqdm(pack)
        for pack in tq:
            cmd = f'sudo apt-get install -y {pack}'
            self.log.msg(f"正在执行{cmd}",logger_name=self.logname,outconsole=True)
            self.log.msg(self.tool.run_command(cmd,out=True),logger_name=self.logname)

    def apt_install_dcgm(self):
        self.apt_update_package()
        cmd = f"sudo apt-get install -y datacenter-gpu-manager-4-cuda-all"
        self.log.msg(self.tool.run_command(cmd,out=True), logger_name=self.logname )

    def apt_install_libnccl(self):
        self.apt_update_package()
        cmd = f'sudo apt-get install -y libnccl2 libnccl-dev'
        self.log.msg(self.tool.run_command(cmd, out=True), logger_name=self.logname)

    def apt_install_cuda_keyring(self):
        url = 'https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb'
        cmd = f'wget -c -O ~/cuda-keyring_1.1-1_all.deb {url}'
        cmd2 = f'dpkg -i ~/cuda-keyring_1.1-1_all.deb'
        self.log.msg(self.tool.run_command(cmd,out=True), logger_name=self.logname )
        self.log.msg(self.tool.run_command(cmd2,out=True), logger_name=self.logname )

    def apt_install_doca(self):
        self.apt_update_package()
        url = 'https://content.mellanox.com/DOCA/DOCA_v3.1.0/host/doca-host_3.1.0-091000-25.07-ubuntu2204_amd64.deb'
        cmd = f'wget -c -O ~/doca.deb {url}'
        tar = f'dpkg -i ~/doca.deb'
        self.log.msg(self.tool.run_command(cmd,out=True), logger_name=self.logname )
        self.log.msg(self.tool.run_command(tar,out=True), logger_name=self.logname )
        self.log.msg(self.tool.run_command('apt install -y doca-all', out=True), logger_name=self.logname)

    def apt_install_mlnx_ofed_linux(self):
        """ubuntu22 MLNX_OFED_LINUX"""
        self.apt_update_package()
        url = 'https://content.mellanox.com/ofed/MLNX_OFED-24.10-3.2.5.0/MLNX_OFED_LINUX-24.10-3.2.5.0-ubuntu22.04-x86_64.tgz'
        cmd = f'wget -c -O ~/MLNX.tgz {url}'
        #解压
        tar = f'cd ~ && tar -zxvf ~/MLNX.tgz'
        #MLNX依赖
        cmd2 = ('apt-get install -y gcc g++ make perl autoconf dkms libltdl-dev m4 gfortran automake swig tk quilt '
                'debhelper libnl-route-3-dev graphviz flex bison libgfortran5 tcl libfuse2 pkg-config chrpath '
                'libnl-3-dev autotools-dev linux-headers-$(uname -r)')
        cmd3 = 'cd ~/MLNX && ./mlnxofedinstall --force'
        a = [cmd,tar,cmd2,cmd3]
        for i in a:
            b= self.tool.run_command(i,out=True)
            self.log.msg(b,logger_name=self.logname)


    def apt_update_package(self):
        """更新软件包"""
        cmd = f'sudo apt-get update'
        print("正在 apt-get update")
        self.tool.run_command(cmd)