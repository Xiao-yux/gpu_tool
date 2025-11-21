from utils.config import Config
import utils.menu as menu
from art import tprint, text2art
from utils.update import Update
from utils.syscheck import CheckSystem


def main():
    cfg = Config()
    tx1="GPU Tool"
    args = Config.parse_arguments(cfg.get_config_value('CONFIG')['version'])
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
    print(text2art(tx1, chr_ignore=True))
    cfg.log.msg('运行菜单')
    CheckSystem(cfg)
    Update(cfg)
    men = menu.Menu(cfg)
    men.run()

if __name__ == '__main__':
    main()
