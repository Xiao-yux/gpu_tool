from bash.bash import InfoBash
from bash.date_Modus import dmicode_to_json
# 使用第一行作为表头


if __name__ == '__main__':
    date = None
    # with open("bash/2", "r", encoding="utf-8") as f:
    #     date = f.read()
    # a= dmicode_to_json(date)
    info = InfoBash()
    # info.dmidecode = a
    info.get_sys_info()
    info.get_cpu_info()
    info.get_memory_info()

    
