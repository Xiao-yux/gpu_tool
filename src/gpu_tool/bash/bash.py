from rich import box
from rich.console import Console
from rich.table import Table
from bash.date_Modus import sysInfo,dmicode_to_json
from runner.local import run_command

class InfoBash:
    def __init__(self):
        self.dmidecode = dmicode_to_json(self.get_dmidecode())
        pass
    
    def get_sys_info(self):
        """获取系统信息,传入dmidecode数据"""
        #系统信息模板
        sysdate = sysInfo()
        sysdate.manufacturer = self.dmidecode["type_0"]['fields'].get("Manufacturer")
        sysdate.product_name = self.dmidecode["type_1"]['fields'].get("Product Name","")
        sysdate.sn = self.dmidecode["type_1"]['fields'].get("Serial Number","")
        sysdate.hight = self.dmidecode["type_3"]['fields'].get("Height","")
        sysdate.type = self.dmidecode["type_3"]['fields'].get("Type","")
        sysdate.bios_release_date = self.dmidecode["type_0"]['fields'].get("Release Date","")
        sysdate.bios_vendor = self.dmidecode["type_0"]['fields'].get("Vendor","")
        sysdate.bios_version = self.dmidecode["type_0"]['fields'].get("Version","")
        sysdate.bios_revision = self.dmidecode["type_0"]['fields'].get("BIOS Revision","")
        if self.dmidecode['type_4'] and len(self.dmidecode['type_4']) > 0:
            for cpu in self.dmidecode['type_4']:
                tmp = cpu['fields']
                a = [f"CPU槽位:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU型号:{tmp.get('Version')}  CPU核心数:{tmp.get('Core Count')}  CPU线程数:{tmp.get('Thread Count')} \nCPU频率:{tmp.get('Max Speed')}  L1缓存:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  L2缓存:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  L3缓存:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}"]

                sysdate.cpuinfo.append(a)
        else:
            tmp = self.dmidecode['type_4']['fields']
            sysdate.cpuinfo =  [f"CPU槽位:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU型号:{tmp.get('Version')}  CPU核心数:{tmp.get('Core Count')}  CPU线程数:{tmp.get('Thread Count')} \nCPU频率:{tmp.get('Max Speed')}  L1缓存:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  L2缓存:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  L3缓存:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}"]
        tmp = [
            ["系统信息"], #标题
            ["制造商", sysdate.manufacturer,"产品名称", sysdate.product_name,"序列号", sysdate.sn,"类型", sysdate.type,"高度", sysdate.hight],
            ["BIOS供应商", sysdate.bios_vendor,"BIOS发布日期", sysdate.bios_release_date,"BIOS版本", sysdate.bios_version,"BIOS修订", sysdate.bios_revision],
            ["CPU信息"],  #标题
        ]
        return tmp

    

    def find_type_by_handle(self, target_handle) -> dict:
        """根据 handle 查找对应的块信息。"""
        def search(node):  # 定义一个名为search的函数，用于在数据结构中查找特定handle的节点
            if isinstance(node, dict):  # 检查当前节点是否为字典类型
                if node.get("handle") == target_handle:  # 检查字典中是否存在handle键且其值等于target_handle
                    return node  # 如果找到匹配的节点，则返回该节点
                for value in node.values():
                    result = search(value)
                    if result is not None:
                        return result
            elif isinstance(node, list):
                for item in node:
                    result = search(item)
                    if result is not None:
                        return result
            return None

        return search(self.dmidecode) or {}
    
    def get_dmidecode(self):
        """获取dmidecode数据"""
        dmidecode = run_command("dmidecode")
        return dmidecode

def tab_print(data):
    console = Console()
    table = Table(show_header=False, box=box.SQUARE, border_style="bright_white")

    if not data:
        console.print("[dim]No data[/dim]")
        return

    if data and isinstance(data[0], list):
        max_cols = max(len(row) for row in data if isinstance(row, list))
        for _ in range(max_cols):
            table.add_column(justify="center", no_wrap=True)

        for row in data:
            if not isinstance(row, list):
                continue
            cells = [str(item) for item in row]
            table.add_row(*cells)
    else:
        table.add_column(justify="center", no_wrap=True)
        table.add_row(str(data))

    console.print(table)
    