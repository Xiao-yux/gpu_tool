import argparse
import sys

from _version import __version__
from art import text2art
from bash.bash import InfoBash
from utils.show_xid import show_xid
from utils.tool import Tools


class GpuToolApi:
    def __init__(self):
        self.version = __version__
        self.tool = Tools()
        self.info = InfoBash()
        self.xid_path = f"{self.tool.get_bash_path()}/Xid-Catalog.zh-CN.xlsx"
        self.run()

    def run(self):
        tx1 = "GPU Tool"
        args = self.parse_arguments(self.version)
        if args.disp_name:
            tx1 = args.disp_name
        if args.get_gpu_info:
            gpu,ecc = self.info.get_gpu_info()
            print(gpu)
            print(ecc)
            sys.exit(0)
        if args.get_sys_info:
            print(self.info.get_sys_info())
            print(self.info.get_cpu_info())
            print(self.info.get_memory_info())
            sys.exit(0)
        if args.get_eth_info:
            print(self.info.get_net_info())
            print(self.info.get_disk_info())
            print(self.info.get_power_info())
            sys.exit(0)
        if args.check_fd_log:
            self.tool.fd_log_print(args.check_fd_log)
            sys.exit(0)
        if args.xid is not None:
            show_xid(self.xid_path,args.xid)
            sys.exit(0)
        print(text2art(tx1, chr_ignore=True))
        print(f"\033[92mv{__version__}\033[0m")
    @staticmethod
    def parse_arguments(ver=None):
        """
        解析命令行参数。
        """
        # print("\033[1;m\033[05mT\033[25m\033[1;m")
        s = f'''菜单v\033[1;m\033[05m{ver}\033[25m\033[1;m
    项目地址：https://github.com/Xiao-yux/gpu_tool'''

        parser = argparse.ArgumentParser(
            description=s,
            formatter_class=argparse.RawDescriptionHelpFormatter  # 保持描述中的换行
        )

        # 添加参数
        parser.add_argument('--get_gpu_info', action='store_true', help='获取GPU信息')
        parser.add_argument('--get_sys_info', action='store_true', help='获取系统,cpu,内存信息')
        parser.add_argument('--get_eth_info', action='store_true', help='获取网卡和硬盘,电源信息')
        parser.add_argument('--version', action='version', version=f'{ver}', help='显示版本信息')
        parser.add_argument('--disp_name', action='store', help='自定义颜文字')
        parser.add_argument('--check_fd_log', metavar='FD_LOG_PATH',help='分析fd日志')
        parser.add_argument('--xid', metavar='id', type=int, help='查询XID错误码帮助信息')
        return parser.parse_args()
