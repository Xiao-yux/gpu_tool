# GPU Tool

一套用于服务器 GPU 测试与诊断的工具集合和菜单化管理脚本，提供常用显卡检测、压力测试、NCCL 性能测试、日志收集与 Web 界面展示等功能。

## 主要功能
- 菜单化运行多个 GPU/系统测试脚本（fieldiag、gpu-burn、NCCL 等）
- 日志和结果收集，支持统一的输出目录结构
- 简易 Web 界面用于远程查看/控制（位于 `webserver/`）
- 常用诊断脚本集中在 `bash/` 中，方便复用

## 系统要求
- Linux（推荐 Ubuntu/CentOS，部分脚本依赖 `lshw`、`pciutils` 等）
- Python 3.6+   (项目使用 3.10)
- 已安装 GPU 驱动与 CUDA（如需要运行 NCCL/gpu-burn）

## 快速开始
克隆仓库并安装（示例）：

```bash
git clone https://github.com/Xiao-yux/gpu_tool.git
cd gpu_tool
make install
make build
```

构建后可执行文件会放在 `dist/` 目录（取决于 Makefile 配置）。

项目也可以直接通过 Python 运行（用于开发或调试）：

```bash
python main.py
# 或者运行 web 界面
python webserver/main.py
```

## 配置
程序会读取一个 TOML 格式的配置文件，默认路径建议为 `/etc/gpu_tool/config.toml`。你可以在运行前或首次运行后编辑该文件来配置工具路径和日志目录。

示例 `config.toml`：

```toml
[PATH]
config_file = "/etc/gpu_tool/config.toml"
fd_path = "/home/path/fd"
gpu_burn_path = "/home/path/gpu-burn"
nccl_path = "/home/path/nccl-tests/build"
fd_exe = "fieldiag.sh"
gpu_burn_exe = "gpu_burn"
nccl_exe = "all_reduce_perf"

[LOG]
log_path = "/home/path/log"
log_file = "gpu_tool_debug.log"
```

注意：Windows 路径格式与权限与 Linux 不同，本项目以 Linux 环境为主。

## 目录概览
- `core/`：核心逻辑、配置解析、日志模块
- `menu/`：菜单交互与命令行参数解析
- `webserver/`：提供简单的 Web 界面与静态资源
- `bash/`：收集的 Shell 脚本与测试脚本

具体实现与入口：
- [main.py](main.py) — 程序主入口
- [menu/menu.py](menu/menu.py) — 菜单逻辑
- [webserver/main.py](webserver/main.py) — Web 服务入口（若启用）

## 常见命令
- 安装依赖 / 构建（项目自带 Makefile）：

```bash
make install
make build
```

- 直接运行（开发调试）：

```bash
python main.py
python webserver/main.py
```

## 日志与结果
日志与测试结果按配置保存到 `log` 或 `fdlog/` 等目录中，`fdlog/` 下有已整理的真/假数据示例结构，便于查看输出格式。

## 贡献与反馈
欢迎提交 Issue 或 PR 来建议功能、修复 bug 或补充新测试脚本。请在贡献前先打开 Issue 讨论。

## 许可证
当前仓库包含 `LICENSE` 文件，请参阅该文件了解许可信息。
