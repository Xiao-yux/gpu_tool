from bash.bash import InfoBash
from bash.date_Modus import dmicode_to_json,nvidia_to_json,create_pci_info_dict



if __name__ == '__main__':
    date = None
    with open("bash/nvidia-smi.log", "r", encoding="utf-8") as f:
        date = f.read()
    a= nvidia_to_json(date)
    with open("bash/dmidecode.log", "r", encoding="utf-8") as f:
        date = f.read()
    b= dmicode_to_json(date)
    with open("bash/lspci.log", "r", encoding="utf-8") as f:
        date = f.read()
    c= create_pci_info_dict(date)
    info = InfoBash()
    info.nvidia_smi = a
    info.dmidecode = b
    info.lspci=c
    # print(info.get_sys_info())
    # print(info.get_cpu_info())
    # print(info.get_memory_info())
    # print(info.get_gpu_info())
    # print(info.get_power_info())
    # print(info.get_net_info())
    print(info._get_disk_info())