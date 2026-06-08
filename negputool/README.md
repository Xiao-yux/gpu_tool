# negpu

> **Async-first GPU/Server testing toolkit, reborn from
> [gpu_tool](https://github.com/Xiao-yux/gpu_tool).**

`negpu` is a clean-room rewrite of the original `gpu_tool` project. It
keeps the operational semantics (menu-driven fieldiag / gpu-burn / DCGMI /
NCCL / nvbandwidth / p2p / stress-ng / memtester / fio orchestration) but
fixes the P0 security issues, removes the global singletons, adds proper
typing / tests / CI, and is fully **async** from the menu loop down to the
process runners and the WebSocket / SSH bridges.

This package lives at `./negputool/` next to the original `gpu_tool/`
source tree. The original tree is **not modified** — both projects can
co-exist; users can migrate at their own pace.

---

## Status

| Phase | Topic | Status |
|---|---|---|
| 1 | Project skeleton (this PR) | ✅ done |
| 2 | Core infra (config / log / i18n / system collector) | ⏳ planned |
| 3 | Runner abstraction (local / screen) | ⏳ planned |
| 4 | `BaseTestCase` + concrete cases + plugin loader | ⏳ planned |
| 5 | Async menu (MenuKey enum, loop) | ⏳ planned |
| 6 | tools split (system / nvidia / ipmi / fd / disk / storage) | ⏳ planned |
| 7 | WS client (controlled-side) + `asyncssh` bridge | ⏳ planned |
| 8 | Report (md / html / pdf, PDF auto) + autotest | ⏳ planned |
| 9 | CI / Nuitka onefile / packaging | ⏳ planned |
| 10 | E2E + docs + log-comparison tool | ⏳ planned |

See `REFACTORING_TASK.txt` for the full task list and rationale.

---

## Quick start (WSL / Linux)

```bash
# 1. install (editable, with dev deps)
cd negputool
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# or:   pip install -r requirements-dev.txt

# 2. check version
negpu --version
gpu-tool --version
python -m negpu --version

# 3. try the (placeholder) commands
negpu doctor       # planned for Phase 2
negpu config-show  # planned for Phase 2
negpu menu         # planned for Phase 5
```

> **WSL note**: the original project is Linux-only (it expects `screen`,
> `nvidia-smi`, `ipmitool`, `dmidecode`, `stress-ng`, `fio`, `memtester`,
> etc.). WSL works for development. WSL2 is recommended.

---

## Layout

```
negputool/
├── REFACTORING_TASK.txt        # the refactoring plan
├── README.md                   # this file
├── CHANGELOG.md                # migration log
├── MIGRATION.md                # how to switch from gpu_tool
├── pyproject.toml              # PEP 621 metadata + tool config
├── requirements.txt            # runtime deps
├── requirements-dev.txt        # + dev deps
├── setup.cfg                   # legacy config
├── Makefile                    # install / lint / test / onefile
├── .gitignore
│
├── negpu/                      # the package
│   ├── cli.py                  # Typer entry point (`negpu` / `gpu-tool`)
│   ├── _version.py
│   ├── config/  log/  i18n/  runner/  cases/
│   ├── plugins/  report/  menu/  tools/  install/
│   └── wsclient/  autotest/
│
├── tests/                      # pytest (asyncio_mode=auto)
├── scripts/                    # dev_run.sh, compare_logs.py
├── docker/                     # dev container
└── .github/workflows/          # ci.yml, build.yml
```

---

## Development

```bash
make help           # list targets
make dev            # editable install + dev deps
make lint           # ruff check
make format         # black + ruff --fix
make typecheck      # mypy --strict
make test           # pytest with coverage
make all            # lint + typecheck + test
make build          # sdist + wheel
make onefile        # Nuitka single-file binary
make clean
```

Pre-commit hooks (optional but recommended) will be added in Phase 9.

---

## Differences from the original `gpu_tool`

| | gpu_tool (old) | negpu (new) |
|---|---|---|
| Python | 3.6+ | **3.10+** |
| Sync / async | mixed (threading) | **fully async** |
| Config | hand-rolled TOML | **pydantic v2** |
| CLI | `prompt_toolkit`/`noneprompt` | **Typer** (with `noneprompt` for menus) |
| Menu keys | `"1" / "2" / "exit"` strings | **`MenuKey` enum** |
| Log dir | `/home/houmao/log/<sn>/<时间>/...` (hard-coded) | `/home/<user>/log/<sn>/<时间>/{system,run,script,report}/` |
| i18n | Python dicts in `core/i18n/*.py` | **JSON** in `negpu/i18n/locales/*.json` |
| Report | per-test, mostly text logs | **MD / HTML / PDF**, PDF auto |
| Plugin | hard-coded `exclude` set | **directory scan** `negpu/plugins/` |
| WS | 1 server, 1 client, no auth | **async WS client** + **`asyncssh` bridge**, default off |
| Build | Nuitka onefile | **Nuitka onefile** (PyPI not used) |
| Tests | none | **pytest** + `pytest-asyncio` + `pytest-cov` |
| CI | none | **GitHub Actions**: ruff + mypy + pytest |
| Types | partial | **PEP 561** (`py.typed`) + `mypy --strict` |

The original `gpu_tool` source tree is untouched. See `MIGRATION.md`
(written in Phase 10) for step-by-step migration notes.

---

## License

MIT — see `LICENSE` (to be added).