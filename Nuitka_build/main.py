import utils.config as config 
import utils.menu as menu
import threading
if __name__ == '__main__':
    # 初始化配置
    cfg = config.Config()
    print(cfg.get_config_value('log'))