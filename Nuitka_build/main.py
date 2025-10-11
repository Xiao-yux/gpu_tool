import utils.config as config 
import utils.menu as menu
from art import tprint, text2art


if __name__ == '__main__':
    # 初始化配置
    print(text2art("Aisuan",chr_ignore=True)) 
    cfg = config.Config()
    
    
    cfg.log.msg('运行菜单')
    
    
    men = menu.Menu(cfg)
    men.run()