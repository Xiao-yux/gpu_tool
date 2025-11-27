import argparse
import sys

from art import text2art

from utils.tool import Tools

class GpuToolApi:
    def __init__(self,version):
        self.version = version
        self.tool = Tools()
        self.run()

    def run(self):
        tx1 = "GPU Tool"
        args = self.parse_arguments(self.version)
        if args.disp_name:
            tx1 = args.dispname
        if args.get_gpu_info:
            print(self.tool.get_gpu_info())
            sys.exit(0)
        if args.get_sys_info:
            print(self.tool.get_sys_info())
            sys.exit(0)
        if args.get_eth_info:
            print(self.tool.get_eth_info())
            sys.exit(0)
        print(text2art(tx1, chr_ignore=True))
        return
    @staticmethod
    def parse_arguments(ver=None):
        """
        解析命令行参数。
        """
        s = f'''菜单v{ver}
    项目地址：https://github.com/Xiao-yux/gpu_tool'''

        parser = argparse.ArgumentParser(
            description=s,
            formatter_class=argparse.RawDescriptionHelpFormatter  # 保持描述中的换行
        )

        # 添加参数
        parser.add_argument('--get_gpu_info', action='store_true', help='获取GPU信息')
        parser.add_argument('--get_sys_info', action='store_true', help='获取CPU和内存信息')
        parser.add_argument('--get_eth_info', action='store_true', help='获取网卡和硬盘信息')
        parser.add_argument('--version', action='version', version=f'{ver}', help='显示版本信息')
        parser.add_argument('--disp_name', action='store', help='自定义颜文字')

        return parser.parse_args()