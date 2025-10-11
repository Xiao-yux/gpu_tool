arg = {
    "帮助": "--help",
    "运行系统集成测试": "--sit",
    "不运行任何BMC相关任务": "--no_bmc",
    "跳过运行测试前的操作系统检查": "--skip_os_check",
    "遇到第一个错误时失败": "--fail_on_first_error",
    "使用系统中预装的驱动": "--skip_driver_load",
    "通知diag内核处于锁定状态": "--lockdown",
    "将日志文件输出到指定文件夹": "--log",
    "将--log文件夹打包为tgz": "--tar_custom_log_dir",
    "仅在指定的NVSwitch设备上运行测试": "--only_nvswitch_devs",
    "仅在指定的GPU设备上运行测试": "--only_gpu_devs",
    "运行IST测试": "--ist",
    "运行GPU现场诊断测试": "--gpufielddiag",
    "GPU现场诊断参数": "--gpu_fd_args",
    "禁用Pex检查": "--disable_pex_checks",
    "启用DRA分析": "--enable_dra",
    "skucheck JSON文件的绝对路径": "--sku_json",
    "运行1级测试": "--level1",
    "运行2级测试": "--level2",
    "运行指定虚拟ID的测试": "--test",
    "跳过指定虚拟ID的测试": "--skip_tests"
}
for k,v in arg.items():
    print(f"{k} : {v}")