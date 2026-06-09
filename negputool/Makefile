# negpu Makefile
# Build / install / test / format the negpu package.
#
# Usage (from project root or negputool/):
#   make help
#   make install
#   make test
#   make lint
#   make format
#   make onefile
#   make clean

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
PY     ?= python3
PIP    ?= $(PY) -m pip
RUFF   ?= $(PY) -m ruff
BLACK  ?= $(PY) -m black
MYPY   ?= $(PY) -m mypy
PYTEST ?= $(PY) -m pytest

PKG    := negpu
SRC    := src/negpu
TESTS  := tests

OUTPUT     := dist/negpu
ONEFILE    := dist/negpu-onefile
ENTRY      := src/negpu/cli.py
DATA_DIRS  := bash
DATA_FILE  := config.toml

# Ensure ``import negpu`` works when running tools without ``pip install -e .``.
export PYTHONPATH := $(CURDIR)/src:$(PYTHONPATH)

# ---------------------------------------------------------------------------
# Phony targets
# ---------------------------------------------------------------------------
.PHONY: help install dev install-dev test lint format typecheck clean build onefile \
        docs all venv

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help:
	@echo "negpu - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install        Install runtime dependencies"
	@echo "  dev            Install runtime + dev dependencies (editable)"
	@echo "  test           Run pytest with coverage"
	@echo "  lint           Run ruff check"
	@echo "  format         Run black + ruff --fix"
	@echo "  typecheck      Run mypy --strict"
	@echo "  build          Build sdist + wheel via pyproject"
	@echo "  onefile        Build a single-file binary via Nuitka"
	@echo "  clean          Remove caches and build outputs"
	@echo "  all            lint + typecheck + test"

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
venv:
	$(PY) -m venv .venv
	@echo "Run:  source .venv/bin/activate  (or  .venv\\Scripts\\activate on Windows)"

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -e ".[dev]"
	$(PIP) install -r requirements-dev.txt

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------
lint:
	$(RUFF) check $(SRC) $(TESTS)

format:
	$(BLACK) $(SRC) $(TESTS)
	$(RUFF) check --fix $(SRC) $(TESTS)

typecheck:
	$(MYPY) $(SRC)

test:
	$(PYTEST)

all: lint typecheck test

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
build:
	$(PY) -m build --outdir dist

onefile:
	$(PY) -m nuitka \
		--onefile \
		--onefile-no-compression \
		--onefile-tempdir-spec="{CACHE_DIR}/negpu" \
		--onefile-cache-mode=cached \
		--lto=yes \
		--static-libpython=yes \
		--assume-yes-for-downloads \
		--product-name="negpu" \
		--include-data-dir=$(DATA_DIRS)=$(DATA_DIRS) \
		--include-data-file=$(DATA_FILE)=$(DATA_FILE) \
		--output-dir=dist \
		--output-filename=negpu \
		--remove-output \
		--show-progress \
		$(ENTRY)

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
clean:
	rm -rf \
		build dist .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov \
		*.egg-info negpu.egg-info negpu_main.build negpu_main.dist
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +