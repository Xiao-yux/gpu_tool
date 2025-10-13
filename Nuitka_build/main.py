import utils.config as config 
import utils.menu as menu
from art import tprint, text2art
import argparse

def parse_arguments(ver=None):
    """
    解析命令行参数。
    """
    s = f'''菜单v{ver}
项目地址：https://github.com/Xiao-yux/text_gpu_tool'''
    
    parser = argparse.ArgumentParser(
        description=s,
        formatter_class=argparse.RawDescriptionHelpFormatter  # 保持描述中的换行
    )
    
    # 添加参数
    parser.add_argument('--get_gpu_info', action='store_true', help='获取GPU信息')
    parser.add_argument('--get_sys_info', action='store_true', help='获取CPU和内存信息')
    parser.add_argument('--get_eth_info', action='store_true', help='获取网卡和硬盘信息')
    
    return parser.parse_args()

def main():
    cfg = config.Config()
    args = parse_arguments(cfg.get_config_value('CONFIG')['version'])

    if args.get_gpu_info:
        print(cfg.tool.get_gpu_info())
        return
    if args.get_sys_info:
        print(cfg.tool.get_sys_info())
        return
    if args.get_eth_info:
        print(cfg.tool.get_eth_info())
        return
        
    print(text2art("Aisuan", chr_ignore=True))
    cfg.log.msg('运行菜单')
    men = menu.Menu(cfg)
    men.run()

if __name__ == '__main__':
    main()
