from typing import ClassVar, Dict, List
from noneprompt import Choice


class MenuChess:
    _MAIN: ClassVar[List[Choice]] = [
        Choice("一键测试", "1"),
        Choice("系统信息", "2"),
        Choice("GPU测试", "3"),
        Choice("系统其他测试", "4"),
        Choice("设置", "5"),
        Choice("关机", "6"),
        Choice("退出", "exit"),
    ]

    _SYSTEM: ClassVar[List[Choice]] = [
        Choice("查看CPU 内存信息", "1"),
        Choice("查看GPU信息", "2"),
        Choice("查看硬盘网卡信息", "3"),
        Choice("查看nvlink拓扑", "4"),
        Choice("查看impi ip设置信息", "5"),
        Choice("返回", "exit"),
    ]

    _GPU_TEST: ClassVar[List[Choice]] = [
        Choice("FD压测", "1"),
        Choice("GPUburn压测", "2"),
        Choice("Dcgmi测试", "3"),
        Choice("Nvband测试", "4"),
        Choice("Nccl测试", "5"),
        Choice("p2pBandwidthLatencyTest测试", "6"),
        Choice("返回", "exit"),
    ]

    _SYS_TEST: ClassVar[List[Choice]] = [
        Choice("cpu 压测", "1"),
        Choice("内存压测", "2"),
        Choice("硬盘速度测试", "3"),
        Choice("返回", "exit"),
    ]

    _SET_SYSTEM: ClassVar[List[Choice]] = [
        Choice("设置BMC为DHCP获取", "1"),
        Choice("设置BMC用户密码", "2"),
        Choice("返回", "exit"),
    ]

    _AOTU_TEST: ClassVar[List[Choice]] = [
        Choice("测试1", "1"),
        Choice("测试2", "2"),
        Choice("返回", "exit"),
    ]

    _FD: ClassVar[List[Choice]] = [
        Choice("运行Level1 测试", "1"),
        Choice("运行Level2 测试", "2"),
        Choice("单项测试", "3"),
        Choice("自定义参数测试", "4"),
        Choice("返回", "exit"),
    ]

    _GPU_BURN: ClassVar[List[Choice]] = [
        Choice("10分钟", "600"),
        Choice("30分钟", "1800"),
        Choice("1小时", "3600"),
        Choice("2小时", "7200"),
        Choice("4小时", "14400"),
        Choice("8小时", "28800"),
        Choice("16小时", "57600"),
        Choice("24小时", "86400"),
        Choice("返回", "exit"),
    ]

    _DCGM: ClassVar[List[Choice]] = [
        Choice("DCGMI 1级测试(系统验证，约几秒钟)", "diag -r 1"),
        Choice("DCGMI 2级测试(扩展系统验证，约 2 分钟)", "diag -r 2"),
        Choice("DCGMI 3级测试(系统硬件诊断，约 15 分钟)", "diag -r 3"),
        Choice("DCGMI 4级测试(更长时间的系统硬件诊断)", "diag -r 4"),
        Choice("DCGMI discovery", "discovery -l"),
        Choice("自定义测试", "6"),
        Choice("返回", "exit"),
    ]

    # 下面两个菜单项太多，用字典先存，再统一转 Choice
    _FD40212_ARGS_MAP: ClassVar[Dict[str, str]] = {
        "运行系统集成测试(--sit)": "--sit",
        "不运行任何BMC相关任务(--no_bmc)": "--no_bmc",
        "跳过运行测试前的操作系统检查(--skip_os_check)": "--skip_os_check",
        "遇到第一个错误时失败(--fail_on_first_error)": "--fail_on_first_error",
        "使用系统中预装的驱动(--skip_driver_load)": "--skip_driver_load",
        "通知diag内核处于锁定状态(--lockdown)": "--lockdown",
        "将--log文件夹打包为tgz(--tar_custom_log_dir)": "--tar_custom_log_dir",
        "仅在指定的NVSwitch设备上运行测试(--only_nvswitch_devs=<b:d.f>[,<b:d.f>...])": "--only_nvswitch_devs=",
        "仅在指定的GPU设备上运行测试(--only_gpu_devs=<b:d.f>[,<b:d.f>...])": "--only_gpu_devs=",
        "运行IST测试(--ist)": "--ist",
        "运行GPU现场诊断测试(--gpufielddiag)": "--gpufielddiag",
        "GPU现场诊断参数(--gpu_fd_args <args>)": "--gpu_fd_args",
        "禁用Pex检查(--disable_pex_checks)": "--disable_pex_checks",
        "启用DRA分析(--enable_dra)": "--enable_dra",
        "skucheck JSON文件的绝对路径(--sku_json <path>)": "--sku_json",
        "运行1级测试(--level1)": "--level1",
        "运行2级测试(--level2)": "--level2",
        "运行指定虚拟ID的测试(--test <vID>[,<vID>...])": "--test",
        "跳过指定虚拟ID的测试(--skip_tests <vID>[,<vID>...])": "--skip_tests",
        "返回": "exit",
    }

    _FD40212_TEST_ARG_MAP: ClassVar[Dict[str, str]] = {
        "checkinforom(验证 InfoROM 数据的完整性和正确性。)": "checkinforom",
        "inventory   (清点系统中所有 GPU 设备及其基本信息。)": "inventory",
        "connectivity(检查 GPU 与主板、电源、NVLink 等物理连接是否正常。)": "connectivity",
        "gpumem      (测试 GPU 显存及其接口（FBIO）功能。)": "gpumem",
        "gpustress   (对 GPU 核心进行高负载压力测试。)": "gpustress",
        "pcie        (测试 PCIe 带宽、速率协商及信号质量（含眼图测试）。)": "pcie",
        "nvlink      (测试 GPU 之间 NVLink 链路的带宽与信号质量。)": "nvlink",
        "nvswitch    (针对 NVSwitch 芯片进行 NVLink 带宽与信号测试。)": "nvswitch",
        "power       (对 GPU 及 NVSwitch 进行供电压力测试。)": "power",
        "返回": "exit",
    }

    _NVBAND_MAP: ClassVar[Dict[str, str]] = {
        "使用 cuMemcpyAsync 进行主机到设备的 CE 内存拷贝": "0",
        "使用 cuMemcpyAsync 进行设备到主机的 CE 内存拷贝": "1",
        "在设备到主机拷贝同时运行时，测量主机到设备的拷贝（仅报告主机到设备的拷贝带宽）": "2",
        "在主机到设备拷贝同时运行时，测量设备到主机的拷贝（仅报告设备到主机的拷贝带宽）": "3",
        "测量每对可访问对等设备之间 cuMemcpyAsync 的带宽（读取测试）": "4",
        "测量每对可访问对等设备之间 cuMemcpyAsync 的带宽（写入测试）": "5",
        "测量每对可访问对等设备之间 cuMemcpyAsync 的带宽（双向读取测试）": "6",
        "测量每对可访问对等设备之间 cuMemcpyAsync 的带宽（双向写入测试）": "7",
        "测量单个设备与主机之间 cuMemcpyAsync 的带宽（多设备到主机）": "8",
        "测量设备到主机的拷贝带宽（多设备双向）": "9",
        "测量主机到单个设备之间 cuMemcpyAsync 的带宽（主机到多设备）": "10",
        "测量主机到设备的拷贝带宽（多设备双向）": "11",
        "测量从所有可访问对等设备到单个设备的拷贝总带宽（写入）": "12",
        "测量从所有可访问对等设备到单个设备的拷贝总带宽（读取）": "13",
        "测量从单个设备到所有可访问对等设备的拷贝总带宽（写入）": "14",
        "测量从单个设备到所有可访问对等设备的拷贝总带宽（读取）": "15",
        "使用拷贝内核进行主机到设备的 SM 内存拷贝": "16",
        "使用拷贝内核进行设备到主机的 SM 内存拷贝": "17",
        "使用拷贝内核测量主机到设备的拷贝（双向）": "18",
        "使用拷贝内核测量设备到主机的拷贝（双向）": "19",
        "测量每对可访问对等设备之间拷贝内核的带宽（读取测试）": "20",
        "测量每对可访问对等设备之间拷贝内核的带宽（写入测试）": "21",
        "测量每对可访问对等设备之间拷贝内核的带宽（双向读取测试）": "22",
        "测量每对可访问对等设备之间拷贝内核的带宽（双向写入测试）": "23",
        "测量单个设备与主机之间拷贝内核的带宽（多设备到主机）": "24",
        "使用拷贝内核测量设备到主机的带宽（多设备双向）": "25",
        "测量主机到单个设备之间拷贝内核的带宽（主机到多设备）": "26",
        "使用拷贝内核测量主机到设备的带宽（多设备双向）": "27",
        "测量从所有可访问对等设备到单个设备的拷贝总带宽（SM写入）": "28",
        "测量从所有可访问对等设备到单个设备的拷贝总带宽（SM读取）": "29",
        "测量从单个设备到所有可访问对等设备的拷贝总带宽（SM写入）": "30",
        "测量从单个设备到所有可访问对等设备的拷贝总带宽（SM读取）": "31",
        "使用指针追踪内核测量主机-设备访问延迟": "32",
        "测量每对可访问对等设备之间指针解引用操作的延迟": "33",
        "测量 GPU 本地设备缓冲区之间 cuMemcpyAsync 的带宽": "34",
        "返回": "exit",
    }

    # ------------------------------------------------------------------
    # 2. 构造方法里直接赋值
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        """构造方法，初始化菜单选项为 Choice 列表"""
        self.main_menu: List[Choice] = self._MAIN
        self.system_menu: List[Choice] = self._SYSTEM
        self.fd_menu: List[Choice] = self._FD
        self.fd_args_menu: List[Choice] = [Choice(k, v) for k, v in self._FD40212_ARGS_MAP.items()]
        self.gpu_burn_menu: List[Choice] = self._GPU_BURN
        self.dcgm_menu: List[Choice] = self._DCGM
        self.nvband_menu: List[Choice] = [Choice("全部测试", "-1")] + [
            Choice(k, v) for k, v in self._NVBAND_MAP.items()
        ]
        self.setsystem_menu: List[Choice] = self._SET_SYSTEM
        self.fd_test_arg_menu: List[Choice] = [Choice(k, v) for k, v in self._FD40212_TEST_ARG_MAP.items()]
        self.aotu_test_menu: List[Choice] = self._AOTU_TEST
        self.gpu_test_menu: List[Choice] = self._GPU_TEST
        self.sys_test_menu: List[Choice] = self._SYS_TEST