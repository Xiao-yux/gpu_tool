import json
import os
import signal
import subprocess
import time
from typing import List
from core.log import Log
from utils.tool import Tools, exitfun


class TestFun:

    def __init__(self,path,log:Log):
        self.path = path
        self.log = log
        self.tool = Tools()

    def fieldiag_level1(self,no_bmc = True) -> bool:
        """
        运行 fd level1 测试
        """
        cmd = f"{self.path['fd_exe']} --level1"
        if no_bmc:
            cmd += " --no_bmc"
        cmd += f" --log {self.log.get_log_file()}/fd-{time.strftime('%Y%m%d-%H%M')}"
        self.run_command(cmd,logname="auto_fd1")
        return True

    def fieldiag_level2(self,no_bmc = True) -> bool:
        """
        运行 fd level2 测试
        """
        cmd = f"{self.path['fd_exe']} --level2"
        if no_bmc:
            cmd += " --no_bmc"
        cmd += f" --log '{self.log.get_log_file()}/fd-{time.strftime('%Y%m%d-%H%M')}'"
        self.run_command(cmd,logname="auto_fd2")
        return True

    def test1(self):
        """测试1"""
        func = [self.dcgmi_4,self.nccl_test,self.p2pBandwidthLatencyTest,self.nvbandwidth,self.fieldiag_level2]
        return func

    def test2(self):
        """测试2"""
        func = [self.dcgmi_3, self.p2pBandwidthLatencyTest, self.fieldiag_level2]
        return func

    def gpu_burn_1H(self):
        """gpu_burn 1小时"""
        cmd = f"./{self.path['gpu_burn_exe']} 3600"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="auto_gpu_burn")
    def gpu_burn_2H(self):
        """gpu_burn 2小时"""
        cmd = f"./{self.path['gpu_burn_exe']} 7200"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="auto_gpu_burn")
    def gpu_burn_4H(self):
        """gpu_burn 4小时"""
        cmd = f"./{self.path['gpu_burn_exe']} 14400"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="auto_gpu_burn")
    def gpu_burn_6H(self):
        """gpu_burn 6小时"""
        cmd = f"./{self.path['gpu_burn_exe']} 21600"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="auto_gpu_burn")
    def gpu_burn_12H(self):
        """gpu_burn 12小时"""
        cmd = f"./{self.path['gpu_burn_exe']} 43200"
        self.run_command(cmd, path=self.path['gpu_burn_path'], logname="auto_gpu_burn")

    def save_debug(self):
        """触发nvidia_bug_report日志收集"""
        self.log.msg(self.tool.get_nvidia_bug_report(f"{self.log.log_dir}",logname=f"nvidia-bug-report-{time.strftime('%Y-%m-%d-%H:%M:%S')}.log.gz"), logger_name=self.log.create_log_file(f"nvidia_bug_report", "system"))
    def nccl_test(self):
        """nccl test"""
        cmd = f"./{self.path['nccl_exe']} "
        path = f"{self.path['nccl_path']}"
        logname = self.log.create_log_file("auto_nccl_test")
        cmd += f"-b 256M -e {self.tool.get_gpu_memory()} -f 2 -g {self.tool.get_gpu_count()}"
        self.run_command(cmd, path, logname)

    def p2pBandwidthLatencyTest(self):
        cmd = "./p2pBandwidthLatencyTest"
        path = f"{self.tool.get_bash_path()}"
        logname = self.log.create_log_file("auto_p2pBandwidthLatencyTest_test")
        self.run_command(cmd, path, logname)

    def nvbandwidth(self):
        cmd = f"./nvbandwidth"
        path = f"{self.tool.get_bash_path()}"
        self.run_command(cmd, path, logname="auto_nvbandwidth")

    def nvbandwidth_test(self):
        """带宽测试大全"""
        func = [self.nvbandwidth, self.p2pBandwidthLatencyTest, self.nccl_test]
        return func

    def dcgmi_1(self):
        """dcgmi 1级"""
        cmd = f"dcgmi diag -r 1"
        self.run_command(cmd, logname="auto_dcgmi_1")

    def dcgmi_2(self):
        """dcgmi 2级"""
        cmd = f"dcgmi diag -r 2"
        self.run_command(cmd, logname="auto_dcgmi_2")

    def dcgmi_3(self):
        """dcgmi 3级"""
        cmd = f"dcgmi diag -r 3"
        self.run_command(cmd, logname="auto_dcgmi_3")

    def dcgmi_4(self):
        """dcgmi 4级"""
        cmd = f"dcgmi diag -r 4"
        self.run_command(cmd, logname="auto_dcgmi_4")
    def poweroff(self):
        """添加重启"""
        self.run_command("reboot")
    def cpu_test(self):
        """CPU 10分钟测试"""
        cmd = f"stress-ng --cpu 0 --cpu-method all --cache 0 --matrix 0 --memcpy 0 --mq 0 --pipe 0 --fork 0 --switch 0 --vm 0 --vm-bytes 2G --iomix 4 --iomix-bytes 1g --timeout 600s  --metrics-brief --tz --perf --verify --times"
        self.run_command(cmd, logname="aotu_stress_ng.log")

    def disk_speed_test(self):
        """硬盘速度测试"""
        a = self.tool.run_command("lsblk -d -o NAME,TYPE,TRAN,PATH,SIZE,SERIAL,MODEL -J")
        self.log.msg(f"diskdata:{a}")
        try:
            data = json.loads(a)
        except json.JSONDecodeError as e:
            self.log.msg("解析硬盘信息失败，请检查lsblk命令输出是否正确。", outconsole=True)
            self.log.msg(f"错误:{e},data:{a}", outconsole=True)
            return []
        self.log.msg(f"diskdata3:{data}")

        disk : List = []
        for dev in data.get("blockdevices", []):
            self.log.msg(f"diskdata2:{dev}")
            if dev.get("type") == "disk":
                if dev.get("tran") not in ["nvme", "sata", "sas"]:
                    continue
                disk.append(dev.get("path"))

        for d in disk:
            cmd = f"fio --name=seqwrite --filename={d} --size=5G --rw=write --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            # 2 顺序读大文件
            cmd2 = f"fio --name=seqread --filename={d} --size=5G --rw=read --bs=1M --ioengine=libaio --direct=1 --numjobs=1 --runtime=30 --time_based --group_reporting"
            # 3 随机读 4K
            cmd3 = f"fio --name=randread --filename={d} --size=5G --rw=randread --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"
            # 4 混合读写
            cmd4 = f"fio --name=randrw --filename={d} --size=5G --rw=randrw --rwmixread=70 --bs=4k --ioengine=libaio --direct=1 --numjobs=8 --iodepth=32 --runtime=30 --time_based --group_reporting"

            self.log.msg("正在测试 顺序写大文件", outconsole=True)
            self.run_command(cmd, logname=f"auto_disk_speed_test_{d}")
            self.log.msg("正在测试 顺序读大文件", outconsole=True)
            self.run_command(cmd2, logname=f"auto_disk_speed_test_{d}")
            self.log.msg("正在测试 随机读 4K", outconsole=True)
            self.run_command(cmd3, logname=f"auto_disk_speed_test_{d}")
            self.log.msg("正在测试 混合读写", outconsole=True)
            self.run_command(cmd4, logname=f"auto_disk_speed_test_{d}")
        return None

    @exitfun
    def run_command(self, command: str, path: str = '/tmp', logname: str = "TestFun"):
        """运行命令并实时输出日志
        command : 执行的命令
        path : 执行命令时的目录
        logname : 日志名称
        """
        logname = self.log.create_log_file(logname)
        enve = os.environ.copy()
        enve['LC_ALL'] = 'C.UTF-8'
        self.log.msg(f"执行命令{command}", outconsole=True)
        try:
            self.log.msg(f"执行命令: {command}", logger_name=logname)
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将错误输出合并到标准输出
                text=True,
                cwd=path,
                env=enve,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            # 非阻塞读，避免 readline 卡死
            os.set_blocking(process.stdout.fileno(), False)
            if process.stdout is None:
                raise subprocess.SubprocessError("无法创建进程或获取输出流")
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    time.sleep(0.1)
                    self.log.msg(output.strip(), logger_name=logname, outconsole=True)  # 同时记录到日志
                    if logname != "auto_fd2":
                        if time.time() // 300 != globals().setdefault('_last_slot', -1):
                            globals()['_last_slot'] = time.time() // 300
                            self.log.msg(self.tool.run_command("nvidia-smi"),logger_name="time_5_save_info")
            return_code = process.poll()
            self.log.msg(f"命令执行结束, 返回码: {return_code}")
            self.log.msg(f"日志路径: {self.log.get_log_file()}/{logname}", outconsole=True)
            self.log.msg(f"\n", outconsole=True)
        except Exception as e:
            self.log.msg(f"运行命令失败: {e}")
            print(f"执行失败: {e}")