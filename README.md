# GPU Tool

一套用于服务器 GPU 测试与诊断的工具集合和菜单化管理脚本，提供常用显卡检测、压力测试、NCCL 性能测试、日志收集与 Web 界面展示等功能。

## 主要功能
- 菜单化运行多个 GPU/系统测试脚本（fieldiag、gpu-burn、NCCL 等）
- 日志和结果收集，支持统一的输出目录结构
- 简易 Web 界面用于远程查看/控制（位于 `webserver/`）
- 常用诊断脚本集中在 `bash/` 中，方便复用

## 系统要求
- Linux（推荐 Ubuntu/CentOS，部分脚本依赖 `lshw`、`pciutils` 等）
- Python 3.10+   (项目使用 3.10)


## 快速开始
克隆仓库并编译（示例）：

```bash
git clone https://github.com/Xiao-yux/gpu_tool.git
cd gpu_tool
make install   #可选 创建虚拟环境 python -m venv venv
make build  #编译
```

构建后可执行文件会放在 `dist/` 目录（取决于 Makefile 配置）。

项目也可以直接通过 Python 运行（用于开发或调试）：

```bash
python src/gpu_tool/main.py
# 或者运行 web 界面
python src/webserver/main.py
```

## 配置
程序会读取一个 TOML 格式的配置文件，默认路径建议为 `/etc/gpu_tool/config.toml`。你可以在运行前或首次运行后编辑该文件来配置工具路径和日志目录。(如果没有会自己生成一个默认的)

示例 `config.toml`：

```toml  
#需要手动配置的项目
[PATH]
config_file = "/etc/gpu_tool/config.toml"  #默认配置文件路径
fd_path = "/home/path/fd"  #fieldiag 路径    #配置的路径会成为该程序的运行路径
gpu_burn_path = "/home/path/gpu-burn"  #gpu_burn 路径
nccl_path = "/home/path/nccl-tests/build"  #nccl 路径
fd_exe = "fieldiag.sh"  #fieldiag 脚本名
gpu_burn_exe = "gpu_burn" #gpu_burn 程序名称
nccl_exe = "all_reduce_perf" #nccl 程序名称

[LOG]
log_path = "/home/path/log"  #保存的日志路径
log_file = "gpu_tool_debug.log"
```

注意：本项目以 Linux 环境为主。

## gpu_tool目录概览
- `core/`：核心加载逻辑
- `menu/`：菜单交互与命令行参数解析
- `config/`：配置文件解析与路径管理
- `bash/`：系统信息显示脚本
- `i18n/`：国际化支持
- `log/`：日志模块
- `runner/`：screen会话管理与程序执行模块
- `testmanager/`：自动测试模块 (未完成)
- `utils/`：工具函数与辅助模块


具体实现与入口：
- [main.py](src/gpu_tool/main.py) — 程序主入口
- [menu/menu.py](src/gpu_tool/menu/menu.py) — 菜单逻辑

edac-util -v

## 日志与结果
日志与测试结果按配置保存到 'log_path' 中, 命名格式 `log_path/<SN>/time/*`
- `system` : 收集的系统原始命令信息，如 lspci -vvv,dmicode等,具体收集命令在 [check_and_save_system.py](src/gpu_tool/utils/check_and_save_system.py) 中
- `script` : 经过脚本整理后的信息,脚本结果样例可以查看 [doc/gpu_tool1.png](doc/gpu_tool1.png) 
- `run` : 测试程序运行中输出的信息.
- `report`: 测试结果汇总信息.(待实现)

## 部分测试软件地址
- [gpu-burn](https://github.com/wilicc/gpu-burn)
- [nccl-tests](https://github.com/NVIDIA/nccl-tests)
- [cuda-samples](https://github.com/nvidia/cuda-samples)
- [nvbandwidth](https://github.com/NVIDIA/nvbandwidth)

## 贡献与反馈
欢迎提交 Issue 或 PR 来建议功能、修复 bug 或补充新测试脚本。请在贡献前先打开 Issue 讨论。

## 许可证
当前仓库包含 `LICENSE` 文件，请参阅该文件了解许可信息。
