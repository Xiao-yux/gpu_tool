from __future__ import annotations

import re

from pydantic import BaseModel, Field


class sysInfo(BaseModel):
    """系统信息
    """
    manufacturer: str = Field(default="", description="制造商")
    product_name:str = Field(default="", description="产品名称")
    sn: str = Field(default="", description="SN")
    cpuinfo: list = Field(default=[], description="CPU信息")
    hight: str = Field(default="", description="服务器高度")
    type: str = Field(default="", description="服务器类型")
    bios_version: str = Field(default="", description="BIOS版本")
    bios_vendor: str = Field(default="", description="BIOS厂商")
    bios_release_date: str = Field(default="", description="BIOS发布日期")
    bios_revision: str = Field(default="", description="BIOS修订版本")
    
class MenmoryInfo(BaseModel):
    """内存信息
    """
    slot: str = Field(default="", description="槽位")
    manufacturer: str = Field(default="", description="制造商")
    product_name: str = Field(default="", description="产品名称")
    type: str = Field(default="", description="内存类型(DDR)")
    size : str = Field(default="", description="内存大小")
    maxspeed: str = Field(default="", description="最大频率")
    speed: str = Field(default="", description="当前频率")
    sn: str = Field(default="", description="SN")

class PoweInfo(BaseModel):
    """电源信息
    """
    location: str = Field(default="", description="位置")
    name: str = Field(default="", description="名称")
    manufacturer: str = Field(default="", description="制造商")
    sn: str = Field(default="", description="SN")
    rversion: str = Field(default="", description="修订版本")
    type: str = Field(default="", description="类型")
    maxpower: str = Field(default="", description="最大功率")
    status: str = Field(default="", description="状态")
    plugged: str = Field(default="", description="是否插电")
    hot_replaceable: str = Field(default="", description="是否热插拔")
    
class GPUInfo(BaseModel):
    """GPU信息
    """
    bus_id: str = Field(default="", description="总线ID")
    GPU_ID : str = Field(default="", description="GPU ID")
    Product_Name : str = Field(default="", description="产品名称")
    Product_Architecture: str = Field(default="", description="产品架构")
    Serial_Number: str = Field(default="", description="序列号")
    GPU_UUID: str = Field(default="", description="GPU UUID")
    Vbios_Version: str = Field(default="", description="Vbios版本")
    PCIe_Generation: str = Field(default="", description="PCIe 代数")
    Link_Width: str = Field(default="", description="链路宽度")
    Memory_Usage: list = Field(default=[], description="内存使用情况(总大小/使用大小)")
    ECC_Mode:bool = Field(default=False, description="ECC模式")
    ECC_Errors:dict = Field(default={}, description="ECC错误")
    ECC_rows_error_ue: str = Field(default="", description="ECC重映射单元错误")
    ECC_rows_error_ce: str = Field(default="", description="ECC重映射单元错误")
    GPU_Current_Temp: str = Field(default="", description="GPU当前温度")
    GPU_Power:list = Field(default=[], description="GPU功率(最大功率/使用功率)")
    

class DiskInfo(BaseModel):
    """磁盘信息"""
    modu_name: str = Field(default="", description="磁盘名称")
    serial_number: str = Field(default="", description="序列号")
    size: str = Field(default="", description="大小")
    firmware_version: str = Field(default="", description="固件版本")
    nvme_version: str = Field(default="", description="NVMe版本")
    temper : str = Field(default="", description="温度")
    critical_warning : str = Field(default="", description="严重警告")
    date_units_read : str = Field(default="", description="总读取大小")
    date_units_written : str = Field(default="", description="总写入大小")
    power_cycles : str = Field(default="", description="通电次数")
    power_on_hours : str = Field(default="", description="通电小时数")
    unsafe_shutdowns : str = Field(default="", description="非正常关机次数")
    smart_test: str = Field(default="", description="SMART测试")
    
    
def _coerce_scalar(value: str):
    value = value.strip()
    if not value:
        return ""
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def nvidia_to_json(nvidia: str) -> dict:
    """将 nvidia-smi 输出转换为 JSON 格式。"""
    if not nvidia:
        return {}

    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]

    for raw_line in nvidia.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("==============") and stripped.endswith("=============="):
            continue

        indent = len(line) - len(line.lstrip(" \t"))

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        current = stack[-1][1]

        if re.match(r"^.+\s:\s.+$", stripped):
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key:
                current[key] = _coerce_scalar(value)
        else:
            child: dict[str, object] = {}
            current[stripped] = child
            stack.append((indent, child))

    gpus: list[dict[str, object]] = []
    normalized: dict[str, object] = {}

    for key, value in root.items():
        if isinstance(key, str) and key.startswith("GPU ") and isinstance(value, dict):
            gpu_data = dict(value)
            gpu_data["bus_id"] = key[len("GPU "):].strip()
            gpus.append(gpu_data)
        else:
            normalized[key] = value

    if gpus:
        normalized["gpus"] = gpus

    return normalized

def dmicode_to_json(dmidecode: str) -> dict:
    """将dmidecode数据转换为json格式。"""
    if not dmidecode:
        return {}

    blocks = []
    current_block = []

    for line in dmidecode.splitlines():
        if line.startswith("Handle "):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        elif current_block:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    result: dict = {}

    for block in blocks:
        if not block:
            continue

        header = block[0]
        header_match = re.search(r"Handle\s+([^,]+),\s+DMI type\s+(\d+)", header, re.IGNORECASE)
        if not header_match:
            continue

        handle = header_match.group(1).strip()
        type_value = int(header_match.group(2))

        parsed_block = {"handle": handle, "type": type_value, "name": "", "fields": {}}
        content_lines = block[1:]

        name = ""
        fields: dict[str, str | list[str]] = {}
        pending_key: str | None = None
        pending_indent: int | None = None

        for raw_line in content_lines:
            if not raw_line.strip():
                continue

            line = raw_line.rstrip()
            stripped = line.strip()
            indent = len(line) - len(line.lstrip("\t "))

            if not name and ":" not in stripped:
                name = stripped
                continue

            if pending_key is not None and pending_indent is not None and indent > pending_indent:
                current_value = fields[pending_key]
                if isinstance(current_value, str):
                    fields[pending_key] = [current_value]
                    current_value = fields[pending_key]

                if isinstance(current_value, list):
                    current_value.append(stripped)
                continue

            if pending_key is not None:
                pending_key = None
                pending_indent = None

            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value:
                fields[key] = value
            else:
                pending_key = key
                pending_indent = indent
                fields[key] = []

        parsed_block["name"] = name
        parsed_block["fields"] = fields

        key = f"type_{type_value}"
        existing = result.get(key)
        if existing is None:
            result[key] = parsed_block
        elif isinstance(existing, list):
            existing.append(parsed_block)
        else:
            result[key] = [existing, parsed_block]

    return result

def create_pci_info_dict(pci_data: str) -> dict:
    """
    解析原始PCI信息文本，返回一个 {bus_id: pci_info} 的字典
    """
    pci_dict = {}
    # 使用换行符分割整段文本
    lines = pci_data.split('\n')
    
    current_bus_id = None
    current_info_lines = []
    
    for line in lines:
        # 检测非空且不是以空白字符（制表符或空格）开头的行，即为新的设备块起始行
        if line.strip() and not line.startswith((' ', '\t')):
            # 如果之前已经记录了设备，则将其存入字典
            if current_bus_id is not None:
                pci_dict[current_bus_id] = '\n'.join(current_info_lines).strip()
            
            # 提取 Bus ID (格式通常为 XX:XX.X)
            # 假设 Bus ID 是该行的第一个单词
            current_bus_id = line.split()[0]
            current_info_lines = [line]
        else:
            # 属于当前设备的详细信息行，追加进去
            if current_bus_id is not None:
                current_info_lines.append(line)
                
    # 处理最后一个设备块（循环结束时还没有存入字典）
    if current_bus_id is not None:
        pci_dict[current_bus_id] = '\n'.join(current_info_lines).strip()
        
    return pci_dict

def parse_smartctl_stat_output(text):
    result = {
        "disk_info": {},
        "smart_info": {}
    }
    
    # 1. 解析 disk_info
    # 匹配模式: 任意字符(键) + 冒号 + 可选的空格 + 任意字符(值)
    # 使用非贪婪模式 .*? 防止跨行匹配，并去除首尾空格
    disk_info_pattern = re.compile(r'^\s*(.*?)\s*:\s+(.*?)\s*$', re.MULTILINE)
    
    # 限定只在 === START OF INFORMATION SECTION === 区域内查找，避免误匹配其他区域的冒号行
    info_section_match = re.search(r'=== START OF INFORMATION SECTION ===\n(.*?)(?=== START OF READ SMART DATA SECTION ===|$)', text, re.DOTALL)
    
    if info_section_match:
        info_text = info_section_match.group(1)
        for match in disk_info_pattern.finditer(info_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key:  # 确保key不为空
                result["disk_info"][key] = value

    # 2. 解析 smart_info
    # 匹配模式: 空格 + 数字(ID) + 空格 + 字符(属性名) + 连续空格/字符直到最后 + 空格 + 数字/横线(RAW_VALUE)
    # RAW_VALUE 可能包含数字和横线(-)，例如某些时候是 "-" 或者 "41 (Min/Max 18/49)" 这种带括号的
    smart_section_match = re.search(r'ID#\s+ATTRIBUTE_NAME.*?\n(.*?)(?=\n\n|\nSMART Error Log Version|$)', text, re.DOTALL)
    if smart_section_match:
        smart_text = smart_section_match.group(1)
        for line in smart_text.splitlines():
            line = line.rstrip()
            if not line.strip():
                continue
                    
                # 根据 smartctl 的标准输出对齐格式:
                # ID#  ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
                # 0-3  4-28                    29-36    37-41 42-46 47-51 52-60      61-68    69-79       80-end
                
                # 确保行长度足够包含 RAW_VALUE 列 (至少大于 80)
            if len(line) > 80:
                attr_id = line[0:4].strip()
                attr_name = line[4:28].strip()
                raw_value = line[80:].strip()
                    
                if attr_id.isdigit() and attr_name and attr_name not in result["smart_info"]:
                    result["smart_info"][attr_name] = raw_value

    return result

def parse_smartctl_output(text):
    """
    解析 smartctl 输出文本，返回包含磁盘信息和 SMART 信息的字典。
    
    Args:
        text (str): smartctl 命令的完整输出文本
        
    Returns:
        dict: {"disk_info": {...}, "smart_info": {...}}
    """
    result = {
        "disk_info": {},
        "smart_info": {}
    }
    
    # 将文本按行分割
    lines = text.split('\n')
    
    # 状态标记，用于记录当前正在解析哪个部分
    # 0: 其他区域, 1: Information Section, 2: SMART Data Section
    current_section = 0 
    
    # 预编译正则，用于匹配 "Key: Value" 格式
    # 解释：
    # ^\s*       : 行首允许有空格
    # (.+?)      : 匹配 Key (非贪婪模式，直到遇到冒号)
    # \s*:\s*    : 匹配冒号及其周围可能存在的空格
    # (.+)       : 匹配 Value (冒号后的剩余内容)
    pattern = re.compile(r'^\s*(.+?)\s*:\s*(.+)')
    
    for line in lines:
        # 1. 判断当前进入哪个 Section
        if "=== START OF INFORMATION SECTION ===" in line:
            current_section = 1
            continue
        elif "=== START OF SMART DATA SECTION ===" in line:
            current_section = 2
            continue
        elif line.startswith("===") and "END" in line:
            # 如果遇到结束标记，停止解析
            current_section = 0
            continue
            
        # 2. 根据当前状态解析数据
        if current_section > 0:
            match = pattern.match(line)
            if match:
                key = match.group(1).strip()  # 去除 Key 两端空格
                value = match.group(2).strip() # 去除 Value 两端空格
                
                # 将解析出的数据存入对应的字典
                if current_section == 1:
                    result["disk_info"][key] = value
                elif current_section == 2:
                    result["smart_info"][key] = value
                    
    return result