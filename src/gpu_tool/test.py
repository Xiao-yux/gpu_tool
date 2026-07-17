from bash.bash import InfoBash,GPUInfo
from bash.date_Modus import dmicode_to_json,nvidia_to_json
# 使用第一行作为表头


if __name__ == '__main__':
    date = None
    with open("bash/nvidia-smi.log", "r", encoding="utf-8") as f:
        date = f.read()
    a= nvidia_to_json(date)
    with open("bash/dmidecode.log", "r", encoding="utf-8") as f:
        date = f.read()
    b= dmicode_to_json(date)
    info = InfoBash()
    info.nvidia_smi = a
    info.dmidecode = b
    info.get_sys_info()
    # info.get_cpu_info()
    # info.get_memory_info()
    # info.get_gpu_info()

    
