from bash.bash import InfoBash,tab_print
from bash.date_Modus import dmicode_to_json
# 使用第一行作为表头


if __name__ == '__main__':
    date = None
    with open("bash/2", "r", encoding="utf-8") as f:
        date = f.read()
    a= dmicode_to_json(date)
    info = InfoBash()
    info.dmidecode = a
    # for b in range(len(a['type_7'])):
    #     print(f"{b} {a['type_7'][b]}")
    b=info.get_sys_info()
    # print(info.find_type_by_handle("0x00CA"))
    tab_print(b)