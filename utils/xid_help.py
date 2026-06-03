from colorama import init, Fore

# XID 帮助文档字典
# 键为 XID 编号，值为该编号的说明信息
#  - title: XID 名称
#  - description: 说明文本列表（常见原因等）
#  - solution: 解决方案（没有则置为 None）
XID_HELP = {
    13: {
        "title": "GR: SW Notify Error",
        "description": [
            "常见原因：一般为用户应用程序故障。通常这是一个数组下标越界错误。也有可能是非法指令，非法寄存器等其他情况。",
            "极少数情况下 会出现硬件故障或者软件错误导致XID 13"
        ],
        "solution": None
    },
    31: {
        "title": "Fifo: MMU Error",
        "description": [
            "常见原因： 一般为应用程序级别故障。 当MMU上报故障时，当gpu芯片上的应用程序进行非法地址访问时，会触发此类故障并记录。"
        ],
        "solution": None
    },
    32: {
        "title": "PBDMA Error",
        "description": [
            "常见原因： 一般是硬件问题。当 DMA 控制器报告故障时，会记录此事件，该控制器通过 PCI-E 总线管理 NVIDIA 驱动程序和 GPU 之间的通信流。这些故障主要涉及PCI的质量问题，一般不是由用户应用程序操作引起的。"
        ],
        "solution": "联合硬件运维处理"
    },
    43: {
        "title": "RESET CHANNEL VERIF ERROR",
        "description": [
            "常见原因：基本是用户应用程序故障。不影响GPU的健康状况"
        ],
        "solution": "联合开发同事处理"
    },
    45: {
        "title": "OS: Preemptive Channel Removal",
        "description": [
            "常见原因： 通常这并代表发生故障。用户程序退出中止，control-C cpu reset sigkill 都会导致此类事件"
        ],
        "solution": None
    },
    48: {
        "title": "DBE (Double Bit Error) ECC Error",
        "description": [
            "常见原因：怀疑硬件故障。当gpu检测到不可修正的错误，会记录该事件。"
        ],
        "solution": None
    },
    63: {
        "title": "ECC Page Retirement or ROW REMAPPING",
        "description": [
            "常见原因： ECC显存故障，常见于硬件故障。 当应用程序遭遇到 GPU 显存硬件错误时，NVIDIA 自纠错机制会将错误的内存区域retire 或者 remap，retirement 和remapped 信息需要记录到 infoROM 中才能永久生效。",
            "A 系列显卡开始支持row remapping",
            "A系列之前的显卡，例如T4 V100 P100 支持dynamic page retirement"
        ],
        "solution": "联合硬件同事排查"
    },
    64: {
        "title": "ECC Page Retirement or ROW REMAPPING",
        "description": [
            "常见原因： ECC显存故障，常见于硬件故障。 当应用程序遭遇到 GPU 显存硬件错误时，NVIDIA 自纠错机制会将错误的内存区域retire 或者 remap，retirement 和remapped 信息需要记录到 infoROM 中才能永久生效。",
            "A 系列显卡开始支持row remapping",
            "A系列之前的显卡，例如T4 V100 P100 支持dynamic page retirement"
        ],
        "solution": "联合硬件同事排查"
    },
    74: {
        "title": "Nvlink ERROR",
        "description": [
            "常见原因：多半为硬件故障。多卡GPU之间使用nvlink进行通讯时出现问题，链路故障或者g卡故障都会导致。"
        ],
        "solution": "可自行通过gpu reset 或者重启节点 进行恢复。如果此时还无法恢复，需要进行维修处理。"
    },
    79: {
        "title": "GPU has fallen off the bus",
        "description": [
            "常见原因： 多半是硬件问题。具体现象为当gpu驱动尝试通过PCI-e总线访问GPU，访问失败。此事件通常由PCIe链路上的硬件故障引起，导致GPU由于链路中断而无法访问。"
        ],
        "solution": "硬件维修"
    },
    93: {
        "title": "Non-fatal violation of provisioned inforom wear limit",
        "description": [
            "常见原因: 当GPU驱动程序因违反使用nvflash-elsesessionstart导致更新infoROM失败。大多数情况下，这并不是软件驱动故障。"
        ],
        "solution": None
    },
    94: {
        "title": "CONTAINED/UNCONTAINED ECC ERRORs",
        "description": [
            "常见原因：当应用程序遭遇到 GPU 不可纠正的显存 ECC 错误时，NVIDIA 错误抑制机制会尝试将错误抑制在踩到硬件故障的应用程序，而不会让错误导致 GPU 上的所有应用程序受到影响。当抑制机制成功抑制错误时，会产生Xid 94事件，仅影响遭遇了不可纠正 ECC 错误的应用程序。 Xid95 代表抑制失败，此时表明运行在该 GPU 上的所有应用程序都已受到影响。"
        ],
        "solution": "联合硬件同事处理"
    },
    95: {
        "title": "CONTAINED/UNCONTAINED ECC ERRORs",
        "description": [
            "常见原因：当应用程序遭遇到 GPU 不可纠正的显存 ECC 错误时，NVIDIA 错误抑制机制会尝试将错误抑制在踩到硬件故障的应用程序，而不会让错误导致 GPU 上的所有应用程序受到影响。当抑制机制成功抑制错误时，会产生Xid 94事件，仅影响遭遇了不可纠正 ECC 错误的应用程序。 Xid95 代表抑制失败，此时表明运行在该 GPU 上的所有应用程序都已受到影响。"
        ],
        "solution": "联合硬件同事处理"
    },
    110: {
        "title": "SECURITY FAULT ERROR",
        "description": [
            "常见原因：硬件故障。"
        ],
        "solution": "恢复最近所有的系统硬件修改，并冷启动系统。需联系硬件处理。"
    },
    119: {
        "title": "GSP RPC Timeout / GSP Error",
        "description": [
            "常见原因： 当在 GPU 的 GSP 核心上运行的代码中发生错误/或在等待 GPU 的 GSP 核心响应 RPC 消息时发生超时时。"
        ],
        "solution": "可以尝试重启节点或者重置GPU。如果还不行联系硬件处理"
    },
    120: {
        "title": "GSP RPC Timeout / GSP Error",
        "description": [
            "常见原因： 当在 GPU 的 GSP 核心上运行的代码中发生错误/或在等待 GPU 的 GSP 核心响应 RPC 消息时发生超时时。"
        ],
        "solution": "可以尝试重启节点或者重置GPU。如果还不行联系硬件处理"
    },
}


def show_xid_help(xid):
    """
    根据传入的XID编号，打印对应的帮助说明。
    solution 字段会以绿色高亮显示。
    """
    init(autoreset=True)
    info = XID_HELP.get(xid)
    if info is None:
        print(f"{Fore.RED}未找到 XID {xid} 的帮助信息")
        return

    print(f"XID {xid}: {info['title']}:")
    for line in info['description']:
        print(line)
    if info['solution']:
        print(f"{Fore.GREEN}解决方式：{info['solution']}")
