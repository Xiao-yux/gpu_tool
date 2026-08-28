from bash.bash import InfoBash
from runner.screen import TerminalManager
from i18n.i18n import init_i18n
from log.logger import init_logger
from config.loader import load
from bash.date_Modus import dmicode_to_json,nvidia_to_json


if __name__ == '__main__':
    info = InfoBash()
    date = None
    with open("tmp/nvidia-smi.log", "r", encoding="utf-8") as f:
        date = f.read()
    a= nvidia_to_json(date)
    info.nvidia_smi = a
    
    with open("tmp/dmidecode.log", "r", encoding="utf-8") as f:
        date = f.read()
    b= dmicode_to_json(date)
    info.dmidecode = b
    
    # with open("bash/lspci.log", "r", encoding="utf-8") as f:
    #     date = f.read()
    # c= create_pci_info_dict(date)
    # info.lspci=c
    gpu = info.get_gpu_info(json=True)
    if isinstance(gpu,dict):
        for i in gpu['gpus']:
            print(i)
    
    #print(info.get_sys_info())
    #print(info.get_cpu_info())
    #print(info.get_memory_info())
    # d,dd = info.get_gpu_info()
    # print(d)
    # print(dd)
    # print(info.get_power_info())
    # print(info.get_net_info())
    #print(info._get_disk_info())
    
    # config = load()
    # i18n = init_i18n()
    # log = init_logger(config.log)
    # terminal = TerminalManager()
    # a = terminal.execute_command("./fieldiag.sh --level2 --no_bmc --log '/home/houmao/log/fd'", logname="fd_test", path="/home/houmao/gpu-tests-tool/fieldiag/629-24287-XXXX-FLD-41741/")
    # terminal.wait_for_command_completion(a)