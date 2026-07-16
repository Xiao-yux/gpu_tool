from tabulate import tabulate
from bash.date_Modus import sysInfo,dmicode_to_json,MenmoryInfo
from runner.local import run_command

class InfoBash:
    def __init__(self):
        self.dmidecode = dmicode_to_json(self.get_dmidecode())
        
    
    def get_sys_info(self):
        """获取系统信息"""
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
            ["制造商", sysdate.manufacturer,"产品名称", sysdate.product_name,"序列号", sysdate.sn,"类型", sysdate.type,"高度", sysdate.hight],
            ["BIOS供应商", sysdate.bios_vendor,"BIOS发布日期", sysdate.bios_release_date,"BIOS版本", sysdate.bios_version,"BIOS修订", sysdate.bios_revision],
        ]
        date = self.tab_format(tmp)
        print(date)
        return True
    def get_cpu_info(self):
        sysdate = sysInfo()
        if self.dmidecode['type_4'] and len(self.dmidecode['type_4']) > 0:
            for cpu in self.dmidecode['type_4']:
                tmp = cpu['fields']
                a = f"CPU槽位:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU型号:{tmp.get('Version')}  CPU核心数:{tmp.get('Core Count')}  CPU线程数:{tmp.get('Thread Count')} \nCPU频率:{tmp.get('Max Speed')}  L1缓存:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  L2缓存:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  L3缓存:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}"

                sysdate.cpuinfo.append(a)
        else:
            tmp = self.dmidecode['type_4']['fields']
            sysdate.cpuinfo.append(f"CPU槽位:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU型号:{tmp.get('Version')}  CPU核心数:{tmp.get('Core Count')}  CPU线程数:{tmp.get('Thread Count')} \nCPU频率:{tmp.get('Max Speed')}  L1缓存:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  L2缓存:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  L3缓存:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}")
        date = self.tab_format([sysdate.cpuinfo])
        print(date)
        return True
    
    def get_memory_info(self):
        info = MenmoryInfo()
        title = ["slot","Manufacturer","Product Name","Size","Type","Speed","Max Speed","Serial Number",""]
        str = []
        count = 0
        date = self.dmidecode['type_17']
        for i in date:
            info.slot = i['fields'].get("Locator")
            info.manufacturer = i['fields'].get("Manufacturer")
            info.product_name = i['fields'].get("Part Number")
            info.size = i['fields'].get("Size")
            info.type = i['fields'].get("Type")
            info.speed = i['fields'].get("Configured Memory Speed")
            info.maxspeed = i['fields'].get("Speed")
            info.sn = i['fields'].get("Serial Number")
            if info.size =="No Module Installed":
                pass
            else:
                count += 1
                str.append([info.slot,info.manufacturer,info.product_name,info.size,info.type,info.speed,info.maxspeed,info.sn,f"{count}"])
                continue
            str.append([info.slot,info.manufacturer,info.product_name,info.size,info.type,info.speed,info.maxspeed,info.sn,""])
        date = tabulate(str, tablefmt="rounded_outline",headers=title,stralign="center",numalign="center")
        print(date)
        return True
      
      
    def find_type_by_handle(self, target_handle) -> dict:
        """根据 handle 查找对应的块信息。"""
        def search(node):  
            if isinstance(node, dict):  
                if node.get("handle") == target_handle:  
                    return node  
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

    def tab_format(self,data,tablefmt="rounded_grid"):
        return tabulate(data, tablefmt=tablefmt,stralign="center",numalign="center")
        