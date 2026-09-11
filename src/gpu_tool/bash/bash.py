import json
import re

from bash.date_Modus import (
    DiskInfo,
    GPUInfo,
    MenmoryInfo,
    PoweInfo,
    create_pci_info_dict,
    dmicode_to_json,
    nvidia_to_json,
    parse_smartctl_output,
    parse_smartctl_stat_output,
    sysInfo,
)
from i18n.i18n import get_i18n
from runner.local import run_command
from tabulate import tabulate


class InfoBash:
    def __init__(self):
        self.dmidecode = dmicode_to_json(self.get_dmidecode())
        self.nvidia_smi = nvidia_to_json(self.get_nvidia_smi())
        self.lspci = self._get_lspci()
        self.disk = self._get_disk_dict()
        self.i18n = get_i18n()

    def get_sys_info(self):
        """获取系统信息"""
        #系统信息模板
        try:
            return self._get_sys_info()
        except Exception as e:
            return f"{e}"
    def get_gpu_info(self,json=False):
        """获取GPU信息,返回 gpuinfo,eccinfo"""
        try:
            if json:
                return nvidia_to_json(self.get_nvidia_smi())
            else:
                return self._get_gpu_info()
        except Exception as e:
            return f"{e}"
    
    def get_gpu_ecc_count(self):
        """获取GPU ECC错误计数"""
        try:
            return self._get_ecc_count()
        except Exception as e:
            return f"{e}"
    
    def get_memory_info(self):
        """获取内存信息"""
        try:
            return self._get_memory_info()
        except Exception as e:
            return f"{e}"
    def get_power_info(self):
        """获取电源信息"""
        try:
            return self._get_power_info()
        except Exception as e:
            return f"{e}"
    def get_cpu_info(self):
        """获取CPU信息"""
        try:
            return self._get_cpu_info()
        except Exception as e:
            return f"{e}"
    def get_disk_info(self):
        """获取磁盘信息"""
        try:
            return self._get_disk_info()
        except Exception as e:
            return f"{e}"
 
    def _get_sys_info(self):
        """获取系统信息"""
        #系统信息模板
        sysdate = sysInfo()
        sysdate.manufacturer = self.retlace_txt(self.dmidecode.get('type_1', {}).get('fields', {}).get('Manufacturer', 'Unknown'))
        sysdate.product_name = self.retlace_txt(self.dmidecode.get('type_1', {}).get('fields', {}).get('Product Name', 'Unknown'))
        sysdate.sn = self.dmidecode.get('type_1', {}).get('fields', {}).get('Serial Number', 'Unknown')
        sysdate.hight = self.retlace_txt(self.dmidecode.get('type_3', {}).get('fields', {}).get('Height', 'Unknown'))
        sysdate.type = self.retlace_txt(self.dmidecode.get('type_3', {}).get('fields', {}).get('Type', 'Unknown'))
        sysdate.bios_release_date = self.dmidecode.get('type_0', {}).get('fields', {}).get('Release Date', 'Unknown')
        sysdate.bios_vendor = self.retlace_txt(self.retlace_txt(self.dmidecode.get('type_0', {}).get('fields', {}).get('Vendor', 'Unknown')))
        sysdate.bios_version = self.dmidecode.get('type_0', {}).get('fields', {}).get('Version', 'Unknown')
        sysdate.bios_revision = self.dmidecode.get('type_0', {}).get('fields', {}).get('BIOS Revision', 'Unknown')
        tmp = [
            [f"{self.i18n.get('vendor')}", sysdate.manufacturer,f"{self.i18n.get('product_name')}", sysdate.product_name,f"{self.i18n.get('serial_number')}",
             sysdate.sn,f"{self.i18n.get('type')}", sysdate.type,f"{self.i18n.get('hight')}", sysdate.hight],
            [f"BIOS{self.i18n.get('vendor')}", sysdate.bios_vendor,f"BIOS{self.i18n.get('release_date')}", sysdate.bios_release_date,
             f"BIOS{self.i18n.get('version')}", sysdate.bios_version,f"BIOS{self.i18n.get('rversion')}", sysdate.bios_revision],
        ]
        date = self.tab_format(tmp)
        # print(date)
        # self.refresh_dmi() # 刷新数据
        return date
    
    def highlight_non_zero(self,data):
        """
        递归遍历字典，将非零的数值用 <> 包裹并标红
        """
        if isinstance(data, dict):
            # 如果是字典，递归处理每一个值
            return {k: self.highlight_non_zero(v) for k, v in data.items()}
        elif isinstance(data, (int, float)):
            # 如果是数字，判断是否非零
            if data != 0:
                return f'\033[91m<{data}>\033[0m'
            else:
                return data
        else:
            # 如果是其他类型（如字符串 'No'），原样返回
            return data
    
    
    def _get_gpu_info(self,ecccount=False):
        """GPU信息 返回 GPU,ECC  信息"""
        gpu = GPUInfo()
        title=[f"{self.i18n.get('gpu_id')}","Bus ID",f"{self.i18n.get('slot')}"
               ,f"{self.i18n.get('gpu_name')}"
               , f"GPU{self.i18n.get('serial_number')}",
             f"{self.i18n.get('vbios_version')}",
               f"{self.i18n.get('pcie_gen')}",f"{self.i18n.get('gpu_memory_usage')}",
               f"{self.i18n.get('gpu_power')}",f"{self.i18n.get('gpu_temp')}"]
        date = []
        slot = self.get_slot()
        ecc_title= [ f"{self.i18n.get('gpu_id')}","ECC Mode",
                    "Volatile","UE","UE","CE","UE",
                    "Aggregate","UE","UE","CE","UE",
                    "SRAM Sources","","","","","rows_ue","rows_ce"]
        ecc_error = []
        # print(self.nvidia_smi['gpus'][0])
        for i in self.nvidia_smi['gpus']:
            gpu.bus_id = i['PCI'].get("Bus Id")
            gpu.GPU_ID = f"{i['Minor Number']}"
            gpu.Product_Name = i['Product Name']
            gpu.Product_Architecture = i['Product Architecture']
            gpu.Serial_Number = i['Serial Number']
            gpu.GPU_UUID = i['GPU UUID']
            gpu.Vbios_Version = i['VBIOS Version']
            gpu.PCIe_Generation = i['PCI']['GPU Link Info']['PCIe Generation'].get("Current")
            gpu.Link_Width = i['PCI']['GPU Link Info']['Link Width'].get("Current")
            gpu.Memory_Usage = [i['FB Memory Usage']['Total'],i['FB Memory Usage']['Used']]
            gpu.ECC_Mode = i['ECC Mode'].get("Current")
            i['ECC Errors'] = self.highlight_non_zero(i['ECC Errors'])
            gpu.ECC_Errors = i['ECC Errors']
            gpu.ECC_rows_error_ce = i['Remapped Rows']['Correctable Error']
            gpu.ECC_rows_error_ue = i['Remapped Rows']['Uncorrectable Error']
            gpu.GPU_Current_Temp = i['Temperature']['GPU Current Temp']
            gpu.GPU_Power = [i['GPU Power Readings']['Max Power Limit'],i['GPU Power Readings']['Average Power Draw']]
            date.append([gpu.GPU_ID,gpu.bus_id[4:].lower(),f"{slot.get(gpu.bus_id[4:].lower())}",gpu.Product_Name,
                         gpu.Serial_Number,
                         gpu.Vbios_Version,
                         f"Pcie {gpu.PCIe_Generation} {gpu.Link_Width}",f"{gpu.Memory_Usage[1]}/{gpu.Memory_Usage[0]}",
                         f"{gpu.GPU_Power[1]}/{gpu.GPU_Power[0]}",gpu.GPU_Current_Temp])
            ecc_error.append([gpu.GPU_ID,gpu.ECC_Mode,gpu.ECC_Errors['Volatile']['SRAM Correctable'],gpu.ECC_Errors['Volatile']['SRAM Uncorrectable Parity'],
                              gpu.ECC_Errors['Volatile']['SRAM Uncorrectable SEC-DED'],gpu.ECC_Errors['Volatile']['DRAM Correctable'],gpu.ECC_Errors['Volatile']['DRAM Uncorrectable'],
                              gpu.ECC_Errors['Aggregate']['SRAM Correctable'],gpu.ECC_Errors['Aggregate']['SRAM Uncorrectable Parity'],
                              gpu.ECC_Errors['Aggregate']['SRAM Uncorrectable SEC-DED'],gpu.ECC_Errors['Aggregate']['DRAM Correctable'],
                              gpu.ECC_Errors['Aggregate']['DRAM Uncorrectable'],gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM L2'],
                              gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM SM'],gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM Microcontroller'],
                              gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM PCIE'],gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM Other'],
                              gpu.ECC_rows_error_ue,gpu.ECC_rows_error_ce])
        ss = tabulate(date, headers=title, tablefmt='rounded_outline',stralign="center",numalign="center")
        ecc = tabulate(ecc_error, headers=ecc_title, tablefmt='rounded_outline',stralign="center",numalign="center")
        self.refresh_nvidia() # 刷新数据
        return ss,ecc

    def _get_ecc_count(self):
        """GPU信息 返回 GPU,ECC  信息"""
        gpu = GPUInfo()
        self.refresh_nvidia()
        count = 0
        for i in self.nvidia_smi['gpus']:
            gpu.ECC_Mode = i['ECC Mode'].get("Current")
            gpu.ECC_Errors = i['ECC Errors']
            gpu.ECC_rows_error_ce = i['Remapped Rows']['Correctable Error']
            gpu.ECC_rows_error_ue = i['Remapped Rows']['Uncorrectable Error']
            if i['ECC Mode'].get("Current") == "Enabled":
                count = (count 
                        + gpu.ECC_Errors['Volatile']['SRAM Correctable']
                        + gpu.ECC_Errors['Volatile']['SRAM Uncorrectable Parity']
                        + gpu.ECC_Errors['Volatile']['SRAM Uncorrectable SEC-DED']
                        + gpu.ECC_Errors['Volatile']['DRAM Correctable']
                        + gpu.ECC_Errors['Volatile']['DRAM Uncorrectable']
                        + gpu.ECC_Errors['Aggregate']['SRAM Correctable']
                        + gpu.ECC_Errors['Aggregate']['SRAM Uncorrectable Parity']
                        + gpu.ECC_Errors['Aggregate']['SRAM Uncorrectable SEC-DED']
                        + gpu.ECC_Errors['Aggregate']['DRAM Correctable']
                        + gpu.ECC_Errors['Aggregate']['DRAM Uncorrectable']
                        + gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM L2']
                        + gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM SM']
                        + gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM Microcontroller']
                        + gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM PCIE']
                        + gpu.ECC_Errors['Aggregate Uncorrectable SRAM Sources']['SRAM Other']
                        + gpu.ECC_rows_error_ue
                        + gpu.ECC_rows_error_ce)
  
        return count
      

    def _get_cpu_info(self):
        sysdate = sysInfo()
        # print(self.dmidecode['type_4'][1])
        if self.dmidecode == {}:
            return self.tab_format([["无CPU信息"]])
        if isinstance(self.dmidecode['type_4'],list):
            for cpu in self.dmidecode['type_4']:
                tmp = cpu['fields']
                a = f"CPU{self.i18n.get('socket')}:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU{self.i18n.get('ver')}:{tmp.get('Version')}  CPU{self.i18n.get('core_count')}:{tmp.get('Core Count')}  CPU{self.i18n.get('thread_count')}:{tmp.get('Thread Count')} \nCPU{self.i18n.get('clock')}:{tmp.get('Max Speed')}  {self.i18n.get('L1_cache')}:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  {self.i18n.get('L2_cache')}:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  {self.i18n.get('L3_cache')}:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}"

                sysdate.cpuinfo.append(a)
        else:
            tmp = self.dmidecode['type_4']['fields']
            sysdate.cpuinfo.append(f"CPU{self.i18n.get('socket')}:{tmp.get('Socket Designation')}   SN:{tmp.get('Serial Number')}\nCPU{self.i18n.get('ver')}:{tmp.get('Version')}  CPU{self.i18n.get('core_count')}:{tmp.get('Core Count')}  CPU{self.i18n.get('thread_count')}:{tmp.get('Thread Count')} \nCPU{self.i18n.get('clock')}:{tmp.get('Max Speed')}  {self.i18n.get('L1_cache')}:{self.find_type_by_handle(tmp.get('L1 Cache Handle'))['fields']['Maximum Size']}  {self.i18n.get('L2_cache')}:{self.find_type_by_handle(tmp.get('L2 Cache Handle'))['fields']['Maximum Size']}  {self.i18n.get('L3_cache')}:{self.find_type_by_handle(tmp.get('L3 Cache Handle'))['fields']['Maximum Size']}")
        date = self.tab_format([sysdate.cpuinfo])
        # print(date)
        # self.refresh_dmi() # 刷新数据
        return date
    
    def _get_memory_info(self):
        info = MenmoryInfo()
        title = [f"{self.i18n.get('slot')}",f"{self.i18n.get('vendor')}",
                 f"{self.i18n.get('product_name')}",f"{self.i18n.get('size')}",f"{self.i18n.get('type')}",
                 f"{self.i18n.get('m_dlock')}",f"{self.i18n.get('max_clock')}",f"{self.i18n.get('serial_number')}",""]
        str = []
        count = 0
        if self.dmidecode == {}:
            return self.tab_format([["无内存信息"]])
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
        # print(date)
        return date
    
    
    def get_smart_txt(self) -> str:
            tran = ['null','usb',None]
            txt =""
            for i in self.disk['blockdevices']:
                # print(i)
                if i['tran'] not in tran:
                    a = run_command(f"smartctl --all {i['path']}")
                    txt += f"{a}\n\n"
            return txt
        
    def _get_smart_info(self,test=False) -> list[dict]:
        tmp = []
        c:int = 0
        if test:
            with open("tmp/stat.txt", "r", encoding="utf-8") as f:
                s = f.read()
            a = [parse_smartctl_stat_output(s)]
            return a
        tran = ['null','usb',None]
        for i in self.disk['blockdevices']:
            # print(i)
            if i['tran'] not in tran:
                a = run_command(f"smartctl --all {i['path']}")
                if i['tran'] == 'nvme':
                    tmp.append(parse_smartctl_output(a))
                if i['tran'] == 'sata':
                    tmp.append(parse_smartctl_stat_output(a))
                tmp[c]['disk_type'] = i['tran']
                c += 1
        return tmp
    
    
    def _get_disk_info(self):
        a = self._get_smart_info()
        #print(a)
        title = [self.i18n.get('disk_name'), self.i18n.get('serial_number'), self.i18n.get('capacity'),
                 self.i18n.get('firmware_version'),
                 self.i18n.get('temperature'), self.i18n.get('total_read_size'),
                 self.i18n.get('total_write_size'), self.i18n.get('power_cycles'), self.i18n.get('power_on_hours'),
                 self.i18n.get('unsafe_shutdowns'), self.i18n.get('disk_tron')]
        date = DiskInfo()
        tmp = []
        # with open("bash/sma1", "r", encoding="utf-8") as f:
        #     s = f.read()
        # a = [parse_smartctl_output(s)]
        # print(a)
        def get_size(date):
            match = re.search(r'\[(.*?)\]', date)
            if match:
                # group(1) 获取第一个括号内捕获的内容
                result = match.group(1)
                return result
            else:
                return "None"
        def format_written_capacity(raw_value, sector_size=512):
            """
            将 Total_LBAs_Written 的 RAW_VALUE 格式化为人类可读的容量字符串。
            
            规则:
                - 按 1000^3 字节 = 1 GB 计算
                - 写入量 >= 1000 GB (即 1 TB) 时，返回 "xxx.xx TB"
                - 否则返回 "xxx.xx GB"
            
            参数:
                raw_value:   SMART 输出的 Total_LBAs_Written RAW_VALUE（LBA 扇区数）
                sector_size: 扇区大小，默认 512 字节（4Kn 盘传 4096）
            
            返回:
                格式化字符串，如 "473.34 GB" 或 "12.50 TB"
            """
            total_gb = int(raw_value) * sector_size / (1000 ** 3)
            
            if total_gb >= 1000:
                return f"{total_gb / 1000:.2f} TB"
            return f"{total_gb:.2f} GB"
        for i in a:
            if i['disk_type'] == 'sata':
                date.modu_name = i['disk_info'].get("Device Model","")
                date.serial_number = i['disk_info'].get('Serial Number',"")
                date.size = get_size(i['disk_info'].get('User Capacity',""))
                date.firmware_version = i['disk_info'].get('Firmware Version',"")
                date.nvme_version = i['disk_info'].get('SATA Version is',"")
                date.temper = i['smart_info'].get('Temperature_Celsius',"")
                date.critical_warning = i['smart_info'].get('Reported_Uncorrect',"")
                date.date_units_read  = format_written_capacity(i['smart_info'].get('Total_LBAs_Read',0)) 
                date.date_units_written  = format_written_capacity(i['smart_info'].get('Total_LBAs_Written',0)) #Total_LBAs_Written
                date.power_cycles = i['smart_info'].get('Power_Cycle_Count',"")
                date.power_on_hours = i['smart_info'].get('Power_On_Hours',"")
                date.unsafe_shutdowns = "None"
                date.smart_test = i['disk_type']
                tmp.append([date.modu_name,date.serial_number,date.size,
                                    date.firmware_version,date.temper,
                                    date.date_units_read,date.date_units_written,date.power_cycles,date.power_on_hours,
                                    date.unsafe_shutdowns,date.smart_test])
            if i['disk_type'] == 'nvme':
                date.modu_name = i['disk_info'].get('Model Number',"")
                date.serial_number = i['disk_info'].get('Serial Number',"")
                date.size = get_size(i['disk_info'].get('Total NVM Capacity',""))
                date.firmware_version = i['disk_info'].get('Firmware Version',"")
                date.nvme_version = i['disk_info'].get('NVMe Version',"")
                date.temper = i['smart_info'].get('Temperature',"")
                date.critical_warning = i['smart_info'].get('Critical Warning',"")
                date.date_units_read  = get_size(i['smart_info'].get('Data Units Read',""))
                date.date_units_written  = get_size(i['smart_info'].get('Data Units Written',""))
                date.power_cycles = i['smart_info'].get('Power Cycles',"")
                date.power_on_hours = i['smart_info'].get('Power On Hours',"")
                date.unsafe_shutdowns = i['smart_info'].get('Unsafe Shutdowns',"")
                date.smart_test = i['disk_type']
                tmp.append([date.modu_name,date.serial_number,date.size,
                    date.firmware_version,date.temper,
                    date.date_units_read,date.date_units_written,date.power_cycles,date.power_on_hours,
                    date.unsafe_shutdowns,date.smart_test])
        
        if tmp == []:
            tmp.append([self.i18n.get("no_disk_info")])
        return tabulate(tmp,headers=title,tablefmt="rounded_outline",stralign="center",numalign="center")
    
    
    
    def _get_power_info(self):
        power = PoweInfo()
        title = [f"{self.i18n.get('slot')}",f"{self.i18n.get('name')}",f"{self.i18n.get('manufacturer')}",
                 f"{self.i18n.get('serial_number')}",f"{self.i18n.get('rversion')}",f"{self.i18n.get('type')}",
                 f"{self.i18n.get('max_power')}",f"{self.i18n.get('status')}",f"{self.i18n.get('plugged')}",
                 f"{self.i18n.get('hot_replaceable')}"]
        date =[]
        if self.dmidecode.get('type_39',[]) == []:
            date.append([self.i18n.get("no_power_info")])
            return tabulate(date,headers=title,tablefmt="rounded_outline",stralign="center",numalign="center")
        for i in self.dmidecode['type_39']:
            power.location = i['fields'].get("Location")
            power.name = i['fields'].get("Name")
            power.manufacturer = i['fields'].get("Manufacturer")
            power.sn = i['fields'].get("Serial Number")
            power.rversion = i['fields'].get("Revision")
            power.type = i['fields'].get("Type")
            power.maxpower = i['fields'].get("Max Power Capacity")
            power.status = i['fields'].get("Status")
            power.plugged = i['fields'].get("Plugged")
            power.hot_replaceable = i['fields'].get("Hot Replaceable")
            date.append([power.location,power.name,power.manufacturer,power.sn,power.rversion,
                         power.type,power.maxpower,power.status,power.plugged,power.hot_replaceable])
        ss = tabulate(date,headers=title,tablefmt="rounded_outline",stralign="center",numalign="center")
        # print(ss)
        return ss
    def get_slot(self):
        date ={}
        if self.dmidecode.get('type_9',[]) == []:
            return {}
        for i in self.dmidecode['type_9']:
            # print(f"{i['fields']['Bus Address']} : {i['fields']['Designation']}")
            date[i['fields']['Bus Address']] = i['fields']['Designation']
        return date
        
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
    def get_nvidia_smi(self):
        """获取nvidia-smi数据"""
        nvidia_smi = run_command("nvidia-smi -q")
        return nvidia_smi
    
    def refresh_dmi(self):
        """刷新dmidecode数据"""
        self.dmidecode = dmicode_to_json(self.get_dmidecode())
    
    def refresh_nvidia(self):
        """刷新nvidia-smi数据"""
        self.nvidia_smi = nvidia_to_json(self.get_nvidia_smi())
    def tab_format(self,data,tablefmt="rounded_grid"):
        return tabulate(data, tablefmt=tablefmt,stralign="center",numalign="center")
        
    def retlace_txt(self,str: str):
        """ 替换文本"""
        txt = {
            "American Megatrends International, LLC.":"美商安迈有限公司",
            "Rack Mount Chassis":"机架式服务器",
            "Supermicro":"超微"
        }
        return txt.get(str,str)
        
    def get_net_info(self):
        """获取网络设备信息"""
        # 临时存放结构化数据的列表，用于排序
        structured_data = [] 
        
        net_id = self._get_net_pci()  # 网络设备pci id
        if net_id == []:
            return self.tab_format([["无网卡信息"]])
        for i in net_id:
            info_text = self.lspci.get(i, '')
            if not info_text:
                continue
                
            # ... 前面提取变量的代码保持不变 ...
            name = info_text.split('\n', 1)[0].strip()
            
            product_name_match = re.search(r'Product Name:\s*(.+)', info_text)
            Product_Name = product_name_match.group(1).rstrip() if product_name_match else ''
            
            part_number_match = re.search(r'\[PN\]\s*Part number:\s*(.+)', info_text)
            Part_number = part_number_match.group(1).rstrip() if part_number_match else ''
            
            serial_number_match = re.search(r'\[SN\]\s*Serial number:\s*(.+)', info_text)
            Serial_number = serial_number_match.group(1).rstrip() if serial_number_match else ''
            
            numa_match = re.search(r'NUMA node:\s*(.+)', info_text)
            MuMa = numa_match.group(1).strip() if numa_match else ''  # 注意: 你之前的注释里写的是MUMA，这里按你代码里的MuMa来
            
            pci_match = re.search(r'\[V0\]\s*Vendor specific:\s*(.+)', info_text)
            pci = pci_match.group(1).strip() if pci_match else ''
            
            lnksta_match = re.search(r'LnkSta:\s*(.+)', info_text)
            LnkSta = lnksta_match.group(1).strip() if lnksta_match else ''
            
            # 1. 先将提取的数据以字典形式存入列表
            structured_data.append({
                'name': name,
                'Product_Name': Product_Name,
                'Part_number': Part_number,
                'Serial_number': Serial_number,
                'MuMa': MuMa,
                'LnkSta': LnkSta,
                'pci': pci
            })
            
        # 2. 按 Product_Name 进行排序
        # key=lambda x: x['Product_Name'] 告诉 sorted() 按照字典中的 Product_Name 键的值来排序
        sorted_data = sorted(structured_data, key=lambda x: x['Product_Name'])
        
        # 3. 排序后再进行字符串拼接
        date = []
        for item in sorted_data:
            d = [f"{item['name']}\n\n{self.i18n.get('product_name')}:{item['Product_Name']}\n\n{self.i18n.get('part_number')}:{item['Part_number']}   {self.i18n.get('serial_number')}:{item['Serial_number']}   {self.i18n.get('mu_ma')}:{item['MuMa']}  {self.i18n.get('lnkstat')}:{item['LnkSta']}  {self.i18n.get('pcie_gen')}:{item['pci']}"]
            date.append(d)
            
        # 4. 渲染表格
        return tabulate(tabular_data=date, tablefmt="rounded_grid", stralign="left", numalign="left")
                
    def _get_lspci(self):
        """获取lspci数据"""
        # with open("bash/lspci.log", "r", encoding="utf-8") as f:
        #     date = f.read()
        date = run_command("lspci -vvv")
        return create_pci_info_dict(date)
        
    def _get_net_pci(self):
        """获取网络设备的pci id信息
        """
        # self._get_lspci()
        net = ['ethernet','infiniband','network']
        pattern = re.compile(r'\b(' + '|'.join(net) + r')\b', re.IGNORECASE)
        matched_bus_ids = []
    
        for bus_id, info_text in self.lspci.items():
            if not info_text:
                continue
                
            # 获取第一行文本
            first_line = info_text.split('\n', 1)[0]
            
            # 检查是否匹配
            if pattern.search(first_line):
                matched_bus_ids.append(bus_id)
        
        primary_bus_ids = [bid for bid in matched_bus_ids if bid.endswith('.0')]   
        return primary_bus_ids
    
    
    def _get_disk_dict(self):
        """获取磁盘信息"""
        a = run_command("lsblk -d -o NAME,TYPE,TRAN,PATH,SIZE,SERIAL,MODEL -J")
        date = json.loads(a)
        if not isinstance(date, dict):
            return {}
        return date