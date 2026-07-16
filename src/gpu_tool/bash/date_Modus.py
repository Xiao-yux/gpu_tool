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
    