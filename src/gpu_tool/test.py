from bash.bash import InfoBash
from runner.screen import TerminalManager
from i18n.i18n import init_i18n
from log.logger import init_logger
from config.loader import load
from bash.date_Modus import dmicode_to_json,nvidia_to_json
from testmanager.test_config import TestFun

if __name__ == '__main__':
    info = InfoBash()
    date = None
    # with open("tmp/nvidia-smi.log", "r", encoding="utf-8") as f:
    #     date = f.read()
    # a= nvidia_to_json(date)
    # info.nvidia_smi = a
    
    # with open("tmp/dmidecode.log", "r", encoding="utf-8") as f:
    #     date = f.read()
    # b= dmicode_to_json(date)
    # info.dmidecode = b
    config = load()
    init_i18n()
    init_logger(config.log)
    test_fun = TestFun()
    print(test_fun.get_name_test("tests"))
 