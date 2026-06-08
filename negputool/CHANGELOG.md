# Changelog

All notable changes to `negpu` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1 - Project skeleton (current)

#### Added
- `pyproject.toml` (PEP 621) with pinned runtime + dev dependency groups.
- `requirements.txt` and `requirements-dev.txt` for non-pip-frontends.
- `setup.cfg` for tools that don't yet read `pyproject.toml`.
- `.gitignore` (negputool-local; complements the root one).
- `Makefile` with `help / venv / install / dev / lint / format / typecheck / test / all / build / onefile / clean` targets.
- `negpu/_version.py` carrying `__version__ = "0.1.0.dev0"`.
- `negpu/__init__.py` re-exporting `__version__` and `__all__`.
- `negpu/__main__.py` (`python -m negpu`).
- `negpu/cli.py` Typer app exposing `negpu` / `gpu-tool` console scripts and
  three placeholder sub-commands (`doctor`, `config-show`, `menu`).
- `negpu/py.typed` (PEP 561 marker).
- Empty sub-package `__init__.py` for `config / log / i18n / runner / cases /
  plugins / report / menu / tools / install / wsclient / autotest`.
- Two default i18n locales (`en.json`, `zh_CN.json`) under
  `negpu/i18n/locales/`.
- Smoke tests under `tests/`:
  - `tests/conftest.py` (adds project root to `sys.path`).
  - `tests/test_version.py` (version, py.typed, locales, sub-packages).
  - `tests/test_cli.py` (Typer `--version`, `--help`, placeholders,
    `python -m negpu`).

#### Not yet implemented
- Real `config` / `log` / `runner` / `cases` / `menu` / `tools` / `wsclient`
  modules — placeholders only, scheduled for Phases 2-7.
- `LICENSE` file (MIT, to be added in Phase 9).
- `MIGRATION.md` (full content in Phase 10; placeholder sections now).

[Unreleased]: https://github.com/Xiao-yux/gpu_tool/compare/HEAD