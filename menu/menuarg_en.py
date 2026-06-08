from typing import ClassVar, Dict, List
from noneprompt import Choice


class MenuChessEn:
    _MAIN: ClassVar[List[Choice]] = [
        Choice("One-Click Test", "1"),
        Choice("System Information", "2"),
        Choice("GPU Test", "3"),
        Choice("System Other Tests", "4"),
        Choice("Settings", "5"),
        Choice("Shutdown", "6"),
        Choice("Exit", "exit"),
    ]

    _SYSTEM: ClassVar[List[Choice]] = [
        Choice("View CPU and Memory Information", "1"),
        Choice("View GPU Information", "2"),
        Choice("View Disk and Network Information", "3"),
        Choice("View NVLink Topology", "4"),
        Choice("View IMPI IP Settings", "5"),
        Choice("Back", "exit"),
    ]

    _GPU_TEST: ClassVar[List[Choice]] = [
        Choice("FD Stress Test", "1"),
        Choice("GPU Burn Stress Test", "2"),
        Choice("DCGMI Test", "3"),
        Choice("NVBandwidth Test", "4"),
        Choice("NCCL Test", "5"),
        Choice("P2P Bandwidth Latency Test", "6"),
        Choice("Back", "exit"),
    ]

    _SYS_TEST: ClassVar[List[Choice]] = [
        Choice("CPU Stress Test", "1"),
        Choice("Memory Stress Test", "2"),
        Choice("Disk Speed Test", "3"),
        Choice("Back", "exit"),
    ]
    _SYS_TOOL: ClassVar[List[Choice]] = [
        Choice("FD Log Summary", "1"),
        Choice("Back", "exit"),
    ]
    _GPU_DOWNLOAD: ClassVar[List[Choice]] = [
        Choice("Download GPU Burn", "1"),
        Choice("Download NCCL Tests", "2"),
        Choice("Download NVBandwidth", "3"),
        Choice("Download P2P Bandwidth Latency Test", "4"),
        Choice("Back", "exit"),
    ]
    _SET_SYSTEM: ClassVar[List[Choice]] = [
        Choice("Install Dependencies", "1"),
        Choice("BMC Settings", "2"),
        Choice("Download GPU Test Tools", "3"),
        Choice("Other Functions", "4"),
        Choice("Back", "exit"),
    ]
    _BMC_SET: ClassVar[List[Choice]] = [
        Choice("Set BMC to DHCP", "1"),
        Choice("Set BMC User Password", "2"),
        Choice("Back", "exit"),
    ]
    _AOTU_TEST: ClassVar[List[Choice]] = [
        Choice("Test 1 (dcgm4, nccl, p2p, nvbandwidth, fd2)", "1"),
        Choice("Test 2 (dcgm3, p2p, fd2)", "2"),
        Choice("All Bandwidth Tests (nvbandwidth, nccl, p2p)", "4"),
        Choice("Custom", "3"),
        Choice("Back", "exit"),
    ]

    _FD: ClassVar[List[Choice]] = [
        Choice("Run Level 1 Test", "1"),
        Choice("Run Level 2 Test", "2"),
        Choice("Single Item Test", "3"),
        Choice("Custom Parameter Test", "4"),
        Choice("Back", "exit"),
    ]

    _GPU_BURN: ClassVar[List[Choice]] = [
        Choice("10 Minutes", "600"),
        Choice("30 Minutes", "1800"),
        Choice("1 Hour", "3600"),
        Choice("2 Hours", "7200"),
        Choice("4 Hours", "14400"),
        Choice("8 Hours", "28800"),
        Choice("16 Hours", "57600"),
        Choice("24 Hours", "86400"),
        Choice("Custom", "1"),
        Choice("Back", "exit"),
    ]

    _DCGM: ClassVar[List[Choice]] = [
        Choice("DCGMI Level 1 Test (System verification, a few seconds)", "diag -r 1 -v"),
        Choice("DCGMI Level 2 Test (Extended system verification, about 2-8 minutes)", "diag -r 2 -v"),
        Choice("DCGMI Level 3 Test (System hardware diagnostics, about 15-30 minutes)", "diag -r 3 -v"),
        Choice("DCGMI Level 4 Test (Longer system hardware diagnostics)", "diag -r 4 -v"),
        Choice("DCGMI Discovery", "discovery -l"),
        Choice("Custom Test", "6"),
        Choice("Back", "exit"),
    ]

    # The following two menu items are too many, stored in a dictionary first, then uniformly converted to Choice
    _FD40212_ARGS_MAP: ClassVar[Dict[str, str]] = {
        "Run system integration test (--sit)": "--sit",
        "Do not run any BMC related tasks (--no_bmc)": "--no_bmc",
        "Skip OS check before running tests (--skip_os_check)": "--skip_os_check",
        "Fail on first error (--fail_on_first_error)": "--fail_on_first_error",
        "Use pre-installed driver in the system (--skip_driver_load)": "--skip_driver_load",
        "Notify diag kernel is in lockdown state (--lockdown)": "--lockdown",
        "Package --log folder as tgz (--tar_custom_log_dir)": "--tar_custom_log_dir",
        "Run tests only on specified NVSwitch devices (--only_nvswitch_devs=<b:d.f>[,<b:d.f>...])": "--only_nvswitch_devs=",
        "Run tests only on specified GPU devices (--only_gpu_devs=<b:d.f>[,<b:d.f>...])": "--only_gpu_devs=",
        "Run IST test (--ist)": "--ist",
        "Run GPU field diagnostic test (--gpufielddiag)": "--gpufielddiag",
        "GPU field diagnostic parameters (--gpu_fd_args <args>)": "--gpu_fd_args",
        "Disable Pex checks (--disable_pex_checks)": "--disable_pex_checks",
        "Enable DRA analysis (--enable_dra)": "--enable_dra",
        "Absolute path of skucheck JSON file (--sku_json <path>)": "--sku_json",
        "Run level 1 test (--level1)": "--level1",
        "Run level 2 test (--level2)": "--level2",
        "Run tests for specified virtual IDs (--test <vID>[,<vID>...])": "--test",
        "Skip tests for specified virtual IDs (--skip_tests <vID>[,<vID>...])": "--skip_tests",
        "Back": "exit",
    }

    _APT_INSTALL_MENU_MAP: ClassVar[Dict[str, str]] = {
        "Install cuda-keyring": "1",
        "Install NVIDIA-580 driver and cuda13 (If no software source, please execute 1 first)": "2",
        "Install MLNX driver (Network card driver)": "3",
        "Install DOCA": "4",
        "Install DCGMI": "5",
        "Install libnccl": "6",
        "Install system test tools (fio, stress, memtester)": "7",
        "Back": "exit"
    }

    _FD40212_TEST_ARG_MAP: ClassVar[Dict[str, str]] = {
        "checkinforom (Verify the integrity and correctness of InfoROM data.)": "checkinforom",
        "inventory   (Inventory all GPU devices in the system and their basic information.)": "inventory",
        "connectivity (Check if GPU physical connections to motherboard, power, NVLink, etc. are normal.)": "connectivity",
        "gpumem      (Test GPU memory and its interface (FBIO) functionality.)": "gpumem",
        "gpustress   (Perform high-load stress test on GPU core.)": "gpustress",
        "pcie        (Test PCIe bandwidth, rate negotiation and signal quality (including eye diagram test).)": "pcie",
        "nvlink      (Test bandwidth and signal quality of NVLink links between GPUs.)": "nvlink",
        "nvswitch    (Perform NVLink bandwidth and signal tests for NVSwitch chips.)": "nvswitch",
        "power       (Perform power stress test for GPU and NVSwitch.)": "power",
        "Back": "exit",
    }

    _NVBAND_MAP: ClassVar[Dict[str, str]] = {
        "Use cuMemcpyAsync for host-to-device CE memory copy": "0",
        "Use cuMemcpyAsync for device-to-host CE memory copy": "1",
        "Measure host-to-device copy while device-to-host copy is running (only report host-to-device copy bandwidth)": "2",
        "Measure device-to-host copy while host-to-device copy is running (only report device-to-host copy bandwidth)": "3",
        "Measure cuMemcpyAsync bandwidth between each pair of accessible peer devices (read test)": "4",
        "Measure cuMemcpyAsync bandwidth between each pair of accessible peer devices (write test)": "5",
        "Measure cuMemcpyAsync bandwidth between each pair of accessible peer devices (bidirectional read test)": "6",
        "Measure cuMemcpyAsync bandwidth between each pair of accessible peer devices (bidirectional write test)": "7",
        "Measure cuMemcpyAsync bandwidth between a single device and host (multi-device to host)": "8",
        "Measure device-to-host copy bandwidth (multi-device bidirectional)": "9",
        "Measure cuMemcpyAsync bandwidth between host and a single device (host to multi-device)": "10",
        "Measure host-to-device copy bandwidth (multi-device bidirectional)": "11",
        "Measure total copy bandwidth from all accessible peer devices to a single device (write)": "12",
        "Measure total copy bandwidth from all accessible peer devices to a single device (read)": "13",
        "Measure total copy bandwidth from a single device to all accessible peer devices (write)": "14",
        "Measure total copy bandwidth from a single device to all accessible peer devices (read)": "15",
        "Use copy kernel for host-to-device SM memory copy": "16",
        "Use copy kernel for device-to-host SM memory copy": "17",
        "Measure host-to-device copy using copy kernel (bidirectional)": "18",
        "Measure device-to-host copy using copy kernel (bidirectional)": "19",
        "Measure copy kernel bandwidth between each pair of accessible peer devices (read test)": "20",
        "Measure copy kernel bandwidth between each pair of accessible peer devices (write test)": "21",
        "Measure copy kernel bandwidth between each pair of accessible peer devices (bidirectional read test)": "22",
        "Measure copy kernel bandwidth between each pair of accessible peer devices (bidirectional write test)": "23",
        "Measure copy kernel bandwidth between a single device and host (multi-device to host)": "24",
        "Measure device-to-host bandwidth using copy kernel (multi-device bidirectional)": "25",
        "Measure copy kernel bandwidth between host and a single device (host to multi-device)": "26",
        "Measure host-to-device bandwidth using copy kernel (multi-device bidirectional)": "27",
        "Measure total copy bandwidth from all accessible peer devices to a single device (SM write)": "28",
        "Measure total copy bandwidth from all accessible peer devices to a single device (SM read)": "29",
        "Measure total copy bandwidth from a single device to all accessible peer devices (SM write)": "30",
        "Measure total copy bandwidth from a single device to all accessible peer devices (SM read)": "31",
        "Measure host-device access latency using pointer chase kernel": "32",
        "Measure pointer dereference operation latency between each pair of accessible peer devices": "33",
        "Measure cuMemcpyAsync bandwidth between GPU local device buffers": "34",
        "Back": "exit",
    }

    # ------------------------------------------------------------------
    # 2. Constructor directly assigns values
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        """Constructor, initialize menu options as Choice lists"""
        self.main_menu: List[Choice] = self._MAIN
        self.system_menu: List[Choice] = self._SYSTEM
        self.fd_menu: List[Choice] = self._FD
        self.fd_args_menu: List[Choice] = [Choice(k, v) for k, v in self._FD40212_ARGS_MAP.items()]
        self.gpu_burn_menu: List[Choice] = self._GPU_BURN
        self.dcgm_menu: List[Choice] = self._DCGM
        self.nvband_menu: List[Choice] = [Choice("All Tests", "-1")] + [
            Choice(k, v) for k, v in self._NVBAND_MAP.items()
        ]
        self.download_gpu: List[Choice] = self._GPU_DOWNLOAD
        self.setsystem_menu: List[Choice] = self._SET_SYSTEM
        self.apt_menu: List[Choice] = [Choice(k, v) for k, v in self._APT_INSTALL_MENU_MAP.items()]
        self.fd_test_arg_menu: List[Choice] = [Choice(k, v) for k, v in self._FD40212_TEST_ARG_MAP.items()]
        self.aotu_test_menu: List[Choice] = self._AOTU_TEST
        self.gpu_test_menu: List[Choice] = self._GPU_TEST
        self.sys_test_menu: List[Choice] = self._SYS_TEST
        self.bmc_set_menu: List[Choice] = self._BMC_SET
        self.sys_tool_menu: List[Choice] = self._SYS_TOOL
