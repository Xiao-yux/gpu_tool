from __future__ import annotations
import json
import re

from pydantic import BaseModel, Field
from pydantic.types import Json


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
    GPU_Current_Temp: str = Field(default="", description="GPU当前温度")
    GPU_Power:list = Field(default=[], description="GPU功率(最大功率/使用功率)")
    
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
    