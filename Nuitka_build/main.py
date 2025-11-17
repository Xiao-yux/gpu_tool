from utils.config import Config
import utils.menu as menu
from art import tprint, text2art
import argparse
from utils.update import Update
from utils.syscheck import CheckSystem
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
    parser.add_argument('--no_log', action='store_true', help='不显示log')
    parser.add_argument('--get_gpu_info', action='store_true', help='获取GPU信息')
    parser.add_argument('--get_sys_info', action='store_true', help='获取CPU和内存信息')
    parser.add_argument('--get_eth_info', action='store_true', help='获取网卡和硬盘信息')
    parser.add_argument('--version', action='version', version=f'{ver}', help='显示版本信息')
    parser.add_argument('--dispname', action='store', help='自定义颜文字')
    
    return parser.parse_args()

def main():
    cfg = Config()
    tx1="GPU 工具菜单"
    args = parse_arguments(cfg.get_config_value('CONFIG')['version'])
    if args.dispname:
        tx1 = args.dispname
    if args.get_gpu_info:
        print(cfg.tool.get_gpu_info())
        return
    if args.get_sys_info:
        print(cfg.tool.get_sys_info())
        return
    if args.get_eth_info:
        print(cfg.tool.get_eth_info())
        return
    if args.no_log:
        cfg.log.msg('运行菜单')
        Update(cfg)
        CheckSystem(cfg)
        men = menu.Menu(cfg)
        men.run()
        
    
    print(text2art(tx1, chr_ignore=True))
    cfg.log.msg('运行菜单')
    CheckSystem(cfg)
    Update(cfg)
    men = menu.Menu(cfg)
    men.run()

if __name__ == '__main__':
    main()
