# Migration: gpu_tool → negpu

> ⚠️  This document is a placeholder. The full migration guide will be
> written in **Phase 10** after the rest of the package stabilises. For
> now, it captures the *known* differences you should plan around.

## TL;DR

- `gpu_tool` and `negpu` **co-exist**: install `negpu` via `pip install -e .`
  in `./negputool/`, keep using the old `dist/gpu_tool` if you need to.
- Old log directory `/home/houmao/log/<sn>/<时间>/...` is **not modified**
  and remains readable.
- New log directory is `/home/<user>/log/<sn>/<时间>/{system,run,script,report}/`.

## Path-level changes

| Topic | gpu_tool (old) | negpu (new) |
|---|---|---|
| User in log path | hard-coded `houmao` | `getpass.getuser()` (dynamic) |
| Log dir layout | flat | `system / run / script / report` |
| Menu key | string `"1"/"2"/"exit"` | `MenuKey` enum |
| Resume file | `resume.json` (kept) | `resume.json` (kept) |
| i18n files | `core/i18n/{en,zh_cn}.py` | `negpu/i18n/locales/{en,zh_CN}.json` |
| Console entry | `python main.py` | `negpu` / `gpu-tool` / `python -m negpu` |
| WebSocket | default on, no auth | **default off**, async |
| SSH bridge | n/a | `asyncssh` (Phase 7) |
| PDF report | none | auto-generated per test item |

## Command-level differences (planned)

| Old command | New command | Status |
|---|---|---|
| `python main.py` (menu) | `negpu menu` | Phase 5 |
| 查看 CPU 内存信息 | `negpu system info` | Phase 6 |
| FD 压测 level1 | `negpu case run fd --level 1` | Phase 4 |
| 一键测试 1 | `negpu auto test1` | Phase 8 |
| Resume 中断续跑 | `negpu auto resume` | Phase 8 |
| 查看 fd 报表 | (auto generated in `report/`) | Phase 8 |

## What stays the same

- The `bash/` directory and its scripts / binaries.
- The `fieldiag.sh --no_bmc --level1 --log ...` invocation pattern.
- The screen-based execution (negative only) — `negpu runner screen` will
  reproduce `dist/gpu_tool` behaviour.
- The serial-number-based per-machine log bucket.

## Coming in Phase 10

- Step-by-step "old → new" switch guide.
- A `scripts/compare_logs.py` tool that diffs the old and new layouts
  for the same physical machine.
- Recommended deprecation timeline for `gpu_tool`.