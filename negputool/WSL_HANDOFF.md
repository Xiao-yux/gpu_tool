# WSL 启动交接手册

> **本文件用于在 WSL 中开始 negpu 重构项目。**
> 阅读本文件 + 跑通 4.1 节的"快速验证"，即可进入 Phase 2。

---

## 1. 任务总览

我们要做的是把 [Xiao-yux/gpu_tool](https://github.com/Xiao-yux/gpu_tool) **完全重写**为一个新的 Python 包 **`negpu`**，原仓代码**保持不动**。

### 1.1 为什么重写

原始 `gpu_tool` 的评分是 **63.6 / 100 (B 级)**，主要问题：
- 多个真实存在的 bug（`save_debug` / `system_set_menu` / `get_gpu_count`）
- 大量 `shell=True` + f-string 拼接用户输入（命令注入）
- 没有单元测试、没有 CI
- 路径硬编码 `/home/houmao/...`、强制 root
- 菜单键是字符串、模块间耦合紧

完整评分详见仓库根目录的 **`PROJECT_RATING_REPORT.md`**。

### 1.2 重写范围

| 项 | 选择 | 备注 |
|---|---|---|
| 方案 | **C 完全重写** | 保留运维语义，抛弃原结构 |
| Python | **3.10+** | dev 环境是 3.10.20 |
| 包名 | **negpu** | import 短、好念 |
| CLI 入口 | **`gpu-tool`**（+ `negpu`） | pyproject 双 console script |
| i18n | **D1 单文件平铺 JSON** | `negpu/i18n/locales/{en,zh_CN}.json` |
| 异步 | **C2 主体 asyncio** | menu / runner / log / wsclient 全部 async |
| SSH | **B2 asyncssh** | web 远端连客户端 → 客户端 → 服务器 的核心场景 |
| WS 客户端 | **A1 被控端** + **F1 默认关闭** | 仅代码完成，不自动启动 |
| 插件 | **E2 目录扫描** | 扫 `negpu/plugins/` |
| 打包 | **G1 仅 Nuitka** | 不发 PyPI |
| 报表 | **MD / HTML / PDF** | 跑完一项自动生成 PDF，其他手动 |
| 日志目录 | **`/home/<user>/log/<sn>/<时间>/{system,run,script,report}/`** | user 动态（`getpass.getuser()`） |
| 断点续跑 | **保留 `resume.json`** | 不升 SQLite |
| webserver | **暂不重构** | 后续在 `negpu/webserver/` 另起 |

---

## 2. 当前进度

### 2.1 已完成 ✅

| 阶段 | 内容 | 状态 |
|---|---|---|
| — | 项目评分报告 `PROJECT_RATING_REPORT.md` | ✅ |
| — | 重构任务书 `negputool/REFACTORING_TASK.txt` v1.1 | ✅ |
| **Phase 1** | **项目骨架（41 个文件 + 11 个子包）** | ✅ |
| Phase 2 | 核心基础设施（config / log / i18n / context / system_collector） | ⏳ |
| Phase 3 | Runner 抽象（local / screen） | ⏳ |
| Phase 4 | BaseTestCase + 各 case + 插件扫描 | ⏳ |
| Phase 5 | 异步菜单（MenuKey enum） | ⏳ |
| Phase 6 | tools 拆分 + 修 3 个真实 bug | ⏳ |
| Phase 7 | WS 客户端 + asyncssh 桥 | ⏳ |
| Phase 8 | 报表 + autotest | ⏳ |
| Phase 9 | CI / Nuitka / 打包 | ⏳ |
| Phase 10 | E2E + 文档 + 对照脚本 | ⏳ |

### 2.2 Phase 1 已交付的 41 个文件

```
negputool/
├── REFACTORING_TASK.txt        # 重构任务书 v1.1
├── WSL_HANDOFF.md              # 本文件
├── README.md                   # 项目说明
├── CHANGELOG.md                # 变更日志
├── MIGRATION.md                # 从 gpu_tool 迁移的差异表
├── pyproject.toml              # PEP 621 元数据 + ruff/mypy/pytest 配置
├── requirements.txt            # 运行时依赖
├── requirements-dev.txt        # + 开发依赖
├── setup.cfg                   # flake8/isort 兼容
├── Makefile                    # install/dev/test/lint/format/typecheck/onefile
├── .gitignore
├── docker/                     # + .gitkeep
├── scripts/                    # + .gitkeep
├── .github/workflows/          # + .gitkeep
│
├── negpu/                      # 12 个子包
│   ├── __init__.py             # 导出 __version__
│   ├── __main__.py             # python -m negpu
│   ├── _version.py             # __version__ = "0.1.0.dev0"
│   ├── cli.py                  # Typer app: --version / doctor / config-show / menu
│   ├── py.typed                # PEP 561 标记
│   ├── config/  log/  i18n/  runner/  cases/  plugins/
│   ├── report/  menu/  tools/  install/  wsclient/  autotest/
│   └── i18n/locales/{en,zh_CN}.json
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # 自动把项目根加进 sys.path
    ├── test_version.py         # 9 个版本/包结构冒烟测试
    └── test_cli.py             # 7 个 CLI 冒烟测试（含 `python -m negpu`）
```

---

## 3. WSL 启动步骤

### 3.1 前置条件

- WSL2（Ubuntu 22.04+ 推荐）
- Python 3.10+（你的环境是 3.10.20，✅）
- `git` 已安装
- 建议：`pipx`、`build`（`pip install build`）用于本地构建

### 3.2 一次性环境准备

```bash
# 1. 打开终端


# 2. 确认 Python 版本
python3 --version        # 应该是 3.10+

# 3. 进入项目目录（注意是 /mnt/d/ 不是 D:\）
cd /mnt/d/work/gpu_tool/negputool

# 4. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 5. 升级 pip，安装 negpu（可编辑模式 + dev 依赖）
pip install --upgrade pip
pip install -e ".[dev]"

# 6. 验证三个入口
negpu --version
gpu-tool --version
python -m negpu --version
```

### 3.3 跑测试

```bash
pytest -q
# 预期：tests/test_version.py (9 passed) + tests/test_cli.py (7 passed)
# 总计 16 passed
```

### 3.4 跑质量检查

```bash
make lint          # ruff check
make format        # black + ruff --fix
make typecheck     # mypy --strict
make test          # pytest + 覆盖率
make all           # lint + typecheck + test
```

### 3.5 跑自带的"无依赖"结构校验（不需装任何东西）

在 Windows PowerShell 中已验证过 38/38 全绿。WSL 中也可用：

```bash
python3 -c "
import json, tomllib, sys
from pathlib import Path
root = Path('.')
print('negpu/ exists:', (root/'negpu').is_dir())
print('pyproject OK:', tomllib.loads((root/'pyproject.toml').read_text())['project']['name'])
for n in ('en.json','zh_CN.json'):
    print(f'locale {n} OK:', '_meta' in json.loads((root/'negpu'/'i18n'/'locales'/n).read_text()))
print('py.typed OK:', (root/'negpu'/'py.typed').is_file())
"
```

---

## 4. 重要注意事项

### 4.1 不要修改原仓代码

`negputool/` 是**完全独立**的子项目。**严禁**碰 `core/`、`menu/`、`utils/`、`testclass/`、`webserver/`、`main.py`、`config.toml` 等。

> 例外：`REFACTORING_TASK.txt` 和本文件位于 `negputool/`，可改。

### 4.2 依赖与原仓有重叠

| 包 | 原仓用 | negpu 用 |
|---|---|---|
| 提示库 | `noneprompt` | `noneprompt`（保留）+ `typer`（CLI） |
| TOML | `toml` | 内置 `tomllib`（3.11+）/`tomli`（3.10） |
| WebSocket | `websockets` | `websockets`（同步 + 异步 API） |
| SSH | — | `asyncssh`（新增） |
| 配置模型 | 手写 dict | `pydantic v2` |

WSL 同时装新旧版本没问题（不同 venv）。

### 4.3 关键 bug 已经在 Phase 6 修复

3 个真实 bug：
- `save_debug` 多传 `logname=` 参数导致 TypeError
- `system_set_menu` 中 BMC 路径在 `self.main_menu()` 之前被截断
- `get_gpu_count` 条件反向（`grep -i nvidia` 命中时返回 0）

**不要在新代码里保留这些 bug。**

### 4.4 目录布局是 v1.1 决策

```text
/home/<user>/log/<sn>/<时间戳>/
├── system/      # dmesg / nvidia-smi / lspci / lsblk / ipmitool-*
├── run/         # fd_<时间戳>/, gpu_burn_<时间戳>.log, ...
├── script/      # sys_info.log / nvidia_info.log / disk_info.log / ...
├── report/      # fd.pdf (主) / fd.html / fd.md / summary.json
└── time_5_save_info.log   # 每 5 分钟 nvidia-smi 采样  #在跑Fd测试时不采样，因为跑的时候驱动会被卸载掉，不能使用nvidia-smi命令，会导致测试失败
```

`report/` 是否放根目录、PDF 触发时机在 **Phase 8** 与用户最终确认。

### 4.5 命令执行继续用 screen

```bash
screen -dmS <name> <command>     # 异步启动
screen -r <name>                  # 挂回查看
screen -ls                        # 列出会话
```

→ 由 `negpu/runner/screen.py`（Phase 3）实现异步封装。

### 4.6 WebSocket 客户端默认关闭

`config.toml`（v2.2.1）里 `wsenable = false`。
新版默认**不启动** WS 客户端，等 webserver 重构时再一起启用。
但 **代码必须写好**（Phase 7）。

### 4.7 不发 PyPI

打包策略 G1 = 仅 Nuitka 单文件。**不要**在 CI 里加 `twine upload`。
Makefile 里 `build` target 是给调试用，不会发布。

### 4.8 报表内容 "后续讨论"

PDF 报表具体字段、机头 SN / 时间 / PASS-FAIL / 度量值 / 截图等
会在 **Phase 8 实施前** 与你最终确认。**不要在 Phase 7 之前猜测。**

---

## 5. Phase 2 计划（下一步）

> **Phase 2 是真正开始"写 negpu 业务代码"的第一阶段。**

### 5.1 产出

```
negpu/
├── context.py             # 依赖注入容器（替代原 __global_config）
├── config/
│   ├── model.py           # pydantic BaseModel：Path / Language / System / Update / Log
│   ├── loader.py          # TOML 加载 + 版本合并 + 缺键回退
│   └── paths.py           # 动态用户名 / log 目录解析
├── log/
│   ├── logger.py          # 基于 logging + 文件/控制台 handler
│   ├── filter.py          # 清理控制字符 / memtester 噪声
│   ├── path.py            # /home/<user>/log/<sn>/<时间>/
│   └── system_collector.py # 一次性收集 dmesg / nvidia-smi / lspci / lsblk / ipmitool-*

tests/
├── test_config.py         # TOML 解析、版本合并、缺键、动态路径
├── test_log.py            # clean() / logger_name / 路径生成
└── test_system_collector.py # 收集器 mock 各种命令输出
```

### 5.2 关键技术决定（待 Phase 2 开工前确认）

1. **`pydantic` model 字段**：是否需要把原 `config.toml` 的所有 key 都覆盖一遍？
   - 旧：PATH / LANGUAGE / SYSTEM / UPDATE / LOG
   - 新：建议保留同样分区，但字段类型化 + 校验
2. **用户名解析顺序**：`getpass.getuser()` → 环境变量 `USER` → `whoami`？哪个优先？
3. **SN 获取失败时回退**：SN 为空字符串还是 `unknown-<uuid>` 之类？
4. **system_collector 是阻塞还是异步？** 建议异步（与 C2 一致）
5. **TOML 缺键策略**：是抛错、回退到 default、还是 warn + 用 default？建议 **warn + default**

### 5.3 我需要你确认的细节

进入 Phase 2 前，请回复：

1. **配置模型字段**：照搬原 `config.toml` 全部字段？还是只保留 negpu 用得到的？
2. **SN 失败回退**：用 `unknown` 还是 `unknown-<short_uuid>`？
3. **user 解析**：`getpass.getuser()`（推荐）还是别的？
4. **system_collector 同步/异步**：异步（推荐）还是同步？

---

## 6. 推荐阅读顺序

在 WSL 中按这个顺序读 / 改：

1. `REFACTORING_TASK.txt`（决策 + 阶段划分）
2. `PROJECT_RATING_REPORT.md`（为什么这么改）
3. `README.md`（用户视角）
4. `pyproject.toml`（依赖与配置）
5. `negpu/cli.py`（CLI 入口）
6. `negpu/i18n/locales/{en,zh_CN}.json`（文案）
7. `tests/test_cli.py`（了解 CLI 测试模式）
8. 进入 Phase 2 时再看 `core/config.py` / `core/log.py`（原版，理解要替代什么）

---

## 7. 出错时怎么排查

| 现象 | 排查 |
|---|---|
| `negpu: command not found` | 没在 venv 里 / `pip install` 没成功 |
| `ModuleNotFoundError: typer` | 没装 `pip install -e ".[dev]"` 或 dev 没装 |
| `basedpyright` 报"无法解析 typer" | 同上，IDE 没扫描到 venv |
| 测试报 `pytest` 找不到 | 同上 |
| `python -m negpu` 报 `No module` | 是不是在仓库根跑了？要在 `negputool/` 里 |
| Windows 下 `pip install` 报编码错 | 用 WSL，不要在 Windows PowerShell 装 |
| WSL 找不到 `/mnt/d/...` | `wsl --mount` 或检查 `wsl.conf` 的 automount |

---

## 8. 联系点 / 待办

- 当前 commit：`01d70ea`（在我接手前的）
- 接下来的 41 个文件**未提交**（包括 `negputool/` 和 `PROJECT_RATING_REPORT.md`）
- 提交建议时机：每个 Phase 完成后一次 `git add` + `git commit`
- 推荐 commit message：`phase(N): <一句话描述>` 格式

---

**准备好了。在 WSL 跑通 3.2 + 3.3 后，回复"OK"或贴报错，我们开始 Phase 2。**