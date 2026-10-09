import time
start_time = time.time()
print(start_time)
from bash.bash import InfoBash
from runner.screen import TerminalManager
from i18n.i18n import init_i18n
from log.logger import init_logger
from config.loader import load
from bash.date_Modus import dmicode_to_json,nvidia_to_json
from testmanager.testmanager import Manager
print(f"import time {time.time() - start_time}")
start_time = time.time()
if __name__ == '__main__':
    print(f"INFOBASH {time.time() - start_time}")
    start_time = time.time()
    
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
    print(f"init config {time.time() - start_time}")
    start_time = time.time()
    
    config = load()
    
    print(f"config loaded {time.time() - start_time}")
    start_time = time.time()
    init_i18n()
    
    print(f"i18n initialized {time.time() - start_time}")
    start_time = time.time()
    
    init_logger(config.log)
    test_fun = Manager()
    print(f"test manager initialized {time.time() - start_time}")
    print(test_fun.test.get_name_test("CPU测试"))
 