# =============================================================================
#  gpu_tool Makefile
#  Project: gpu_tool — async-first GPU / Server testing toolkit
#  Layout: src/  (src/gpu_tool/..., src/webserver/...)
# =============================================================================

# -----------------------------------------------------------------------------
# Basic configuration
# -----------------------------------------------------------------------------
PY      ?= python3
PIP     ?= $(PY) -m pip
PYTHON  ?= $(PY)

# Detect platform (used for Nuitka/UPX paths)
ifeq ($(OS),Windows_NT)
    PLATFORM      := windows
    PY            := python
    VENV_DIR      := .venv-windows
    VENV_ACTIVATE := $(VENV_DIR)/Scripts/activate
    RM            := rmdir /S /Q
    MKDIR         := mkdir
    UPX_BIN       :=
    NULL_DEV      := nul
else
    PLATFORM      := $(shell uname -s | tr '[:upper:]' '[:lower:]')
    VENV_DIR      := .venv-$(PLATFORM)
    VENV_ACTIVATE := $(VENV_DIR)/bin/activate
    RM            := rm -rf
    MKDIR         := mkdir -p
    UPX_BIN       := $(shell command -v upx 2>/dev/null || echo /usr/bin/upx)
    NULL_DEV      := /dev/null
endif

# -----------------------------------------------------------------------------
# Project metadata (keep in sync with pyproject.toml)
# -----------------------------------------------------------------------------
PACKAGE       := gpu_tool
APP_ENTRY     := $(PACKAGE).main:app
# 从 src/gpu_tool/_version.py 中获取版本号
VERSION_FULL := $(shell $(PY) -c "import ast; print(next(n.value.s if isinstance(n.value, ast.Constant) else n.value for n in ast.parse(open('src/gpu_tool/_version.py').read()).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__version__' for t in n.targets)))" 2>/dev/null || echo 0.0.0)

# Nuitka-compatible strict X.Y.Z version (PEP 440 pre-release / local segments are stripped)
VERSION := $(shell $(PY) -c "v='$(VERSION_FULL)';print(v.split('-')[0].split('+')[0])" \
              2>/dev/null \
              || echo "$(VERSION_FULL)")
PRODUCT_NAME  := gpu_tool
SRC_DIR       := src
TESTS_DIR     := tests
DOC_DIR       := doc
DIST_DIR      := dist
BUILD_DIR     := build

# Nuitka output binary
ifeq ($(PLATFORM),windows)
    OUTPUT_BIN := $(DIST_DIR)/$(PRODUCT_NAME).exe
else
    OUTPUT_BIN := $(DIST_DIR)/$(PRODUCT_NAME)
endif

# -----------------------------------------------------------------------------
# Dependency groups
# -----------------------------------------------------------------------------
# Runtime dependencies (mirror pyproject.toml -> project.dependencies)
RUNTIME_DEPS := \
    pydantic \
    noneprompt \
    toml \
    websockets \
    aiofiles \
    openpyxl \
    tqdm \
    text2art \
    rich \
    jinja2 \
    weasyprint

# Dev / tooling dependencies (mirror pyproject.toml -> [project.optional-dependencies] dev)
DEV_DEPS := \
    pytest \
    pytest-asyncio \
    pytest-mock \
    pytest-cov \
    ruff \
    mypy \
    black \
    typing

# Build-only dependencies (Nuitka + plugins)
BUILD_DEPS := \
    Nuitka \
    ordered-set \
    Nuitka[onefile]

# Optional Linux apt packages needed for the Nuitka build chain
APT_BUILD_DEPS := gcc g++ clang lld make patchelf python3-dev ccache

# -----------------------------------------------------------------------------
# Default target
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help
.PHONY: help
help: ## Show this help message
	@$(PY) -c "import re,sys;\
print('gpu_tool — Makefile targets\n' + '='*40);\
print('\nUsage: make <target>\n');\
print('Targets:');\
[print(f'  {t:<14} {h}') for t,h in re.findall(r'^([a-zA-Z0-9_-]+):.*?##\s*(.+)$$', open('Makefile').read(), re.M)]"

# =============================================================================
# Setup / Install
# =============================================================================
.PHONY: venv
venv: ## Create a local virtualenv at $(VENV_DIR)
	@test -d $(VENV_DIR) || $(PY) -m venv $(VENV_DIR)
	@echo "Virtualenv ready at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_ACTIVATE)"

.PHONY: install
install: ## Install runtime dependencies into the active environment
	$(PIP) install --upgrade pip
	$(PIP) install -e .

.PHONY: install-deps
install-deps: ## Install runtime dependencies only (no package install)
	$(PIP) install --upgrade pip
	$(PIP) install $(RUNTIME_DEPS)

.PHONY: install-dev
install-dev: install ## Install dev dependencies (pytest, ruff, mypy, black, ...)
	$(PIP) install $(DEV_DEPS)
	@echo "Pre-commit hooks: run 'pre-commit install' if you use them."

.PHONY: install-build
install-build: install ## Install Nuitka + build dependencies
	$(PIP) install $(BUILD_DEPS)

.PHONY: install-system
install-system: ## Install OS-level build dependencies (Linux only — requires sudo)
	@echo "Installing system packages: $(APT_BUILD_DEPS)"
	apt-get update
	apt-get install -y $(APT_BUILD_DEPS)

.PHONY: install-all
install-all: install-dev install-build ## Install everything (runtime + dev + build)

# =============================================================================
# Run (development)
# =============================================================================
.PHONY: run
run: ## Run the gpu_tool CLI from source
	$(PY) -m $(PACKAGE)

.PHONY: run-web
run-web: ## Run the Flask webserver from source (src/webserver/main.py)
	$(PY) $(SRC_DIR)/webserver/main.py

.PHONY: run-web-flask
run-web-flask: ## Run webserver via Flask CLI (FLASK_APP-style)
	FLASK_APP=$(SRC_DIR)/webserver/main.py $(PY) -m flask run --host=0.0.0.0 --port=88

# =============================================================================
# Test / Lint / Typecheck / Format
# =============================================================================
.PHONY: test
test: ## Run pytest with coverage (as configured in pyproject.toml)
	$(PY) -m pytest $(TESTS_DIR)

.PHONY: test-fast
test-fast: ## Run pytest without coverage (faster local loop)
	$(PY) -m pytest $(TESTS_DIR) --no-cov -q

.PHONY: test-cov
test-cov: ## Run pytest with HTML coverage report under build/htmlcov
	$(PY) -m pytest $(TESTS_DIR) --cov-report=html:$(BUILD_DIR)/htmlcov --cov-report=xml:$(BUILD_DIR)/coverage.xml

.PHONY: lint
lint: ## Run ruff (lint)
	$(PY) -m ruff check src $(TESTS_DIR)

.PHONY: lint-fix
lint-fix: ## Run ruff with autofixes
	$(PY) -m ruff check --fix src $(TESTS_DIR)

.PHONY: format
format: ## Run ruff format + black
	$(PY) -m ruff format src $(TESTS_DIR)
	$(PY) -m black src $(TESTS_DIR)

.PHONY: format-check
format-check: ## Verify formatting without writing changes
	$(PY) -m ruff format --check src $(TESTS_DIR)
	$(PY) -m black --check src $(TESTS_DIR)

.PHONY: typecheck
typecheck: ## Run mypy in strict mode
	$(PY) -m mypy src

.PHONY: check
check: lint typecheck test ## Run lint + typecheck + tests

# =============================================================================
# Build (Nuitka onefile)
# =============================================================================
.PHONY: build
build: ## Build a onefile binary with Nuitka into ./dist
	@command -v $(PY) >/dev/null || (echo "Python not found: $(PY)" && exit 1)
	@mkdir -p $(DIST_DIR)
	$(PY) -m nuitka \
		--onefile \
		--onefile-no-compression \
		--onefile-tempdir-spec="{CACHE_DIR}/$(PRODUCT_NAME)" \
		--onefile-cache-mode=cached \
		--lto=yes \
		--static-libpython=yes \
		--assume-yes-for-downloads \
		--enable-plugins=upx \
		--upx-binary=$(UPX_BIN) \
		--product-name="$(PRODUCT_NAME)" \
		--product-version="$(VERSION)" \
		--noinclude-default-mode=allow \
		--include-data-dir=$(SRC_DIR)/$(PACKAGE)/bash=bash \
		--include-package=websockets \
		--output-dir=$(DIST_DIR) \
		--output-filename=$(PRODUCT_NAME) \
		--remove-output \
		--show-progress \
		$(SRC_DIR)/$(PACKAGE)/main.py

.PHONY: build-dev
build-dev: ## Fast dev build (no LTO, no UPX) — useful for quick local verification
	@mkdir -p $(DIST_DIR)
	$(PY) -m nuitka \
		--onefile \
		--noinclude-default-mode=allow \
		--include-data-dir=$(SRC_DIR)/$(PACKAGE)/bash=bash \
		--include-package=websockets \
		--output-dir=$(DIST_DIR) \
		--output-filename=$(PRODUCT_NAME) \
		--remove-output \
		$(SRC_DIR)/$(PACKAGE)/main.py

.PHONY: build-module
build-module: ## Build a Python module (not onefile) — faster, for testing
	@mkdir -p $(DIST_DIR)
	$(PY) -m nuitka \
		--module \
		--output-dir=$(DIST_DIR) \
		--remove-output \
		$(SRC_DIR)/$(PACKAGE)/__main__.py

# =============================================================================
# Distribution helpers
# =============================================================================
.PHONY: sdist
sdist: ## Build a source distribution (sdist + wheel) into ./dist
	$(PY) -m pip install --upgrade build
	$(PY) -m build --outdir $(DIST_DIR)

.PHONY: publish-test
publish-test: sdist ## Upload to TestPyPI
	$(PY) -m pip install --upgrade twine
	$(PY) -m twine upload --repository testpypi $(DIST_DIR)/*

.PHONY: publish
publish: sdist ## Upload to PyPI
	$(PY) -m pip install --upgrade twine
	$(PY) -m twine upload $(DIST_DIR)/*

# =============================================================================
# Run built artifacts
# =============================================================================
.PHONY: run-built
run-built: ## Run the binary produced by `make build`
	@if [ ! -x "$(OUTPUT_BIN)" ]; then \
		echo "Binary not found: $(OUTPUT_BIN) — run 'make build' first."; \
		exit 1; \
	fi
	$(OUTPUT_BIN)

# =============================================================================
# Cleaning
# =============================================================================
.PHONY: clean
clean: ## Remove build artifacts (dist/, build/, *.build, *.dist, caches)
	$(RM) $(DIST_DIR) $(BUILD_DIR)
	$(RM) $(PACKAGE).build $(PACKAGE).dist $(PACKAGE).onefile-build
	$(RM) $(PACKAGE)_main.build $(PACKAGE)_main.dist
	$(RM) *.onefile-build
	$(RM) .mypy_cache .ruff_cache .pytest_cache .coverage htmlcov
	find . -type d -name '__pycache__' -prune -exec $(RM) {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -prune -exec $(RM) {} + 2>/dev/null || true

.PHONY: distclean
distclean: clean ## Also remove virtualenvs and the local config cache
	$(RM) $(VENV_DIR)
	$(RM) .venv .venv-windows .venv-linux
	$(RM) src/webserver/cache.db
	$(RM) src/webserver/tmp.txt
	$(RM) src/webserver/log src/webserver/utils/log
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name 'nuitka-crash-report.xml' -delete 2>/dev/null || true

.PHONY: clean-logs
clean-logs: ## Remove runtime log directories
	$(RM) log fdlog src/webserver/log src/webserver/utils/log
	$(RM) src/gpu_tool/log/*.log 2>/dev/null || true

# =============================================================================
# Documentation
# =============================================================================
.PHONY: docs
docs: ## Build documentation into $(DOC_DIR)/build (placeholder — configure sphinx/mkdocs to enable)
	@echo "Documentation build is not configured yet."
	@echo "Add sphinx/mkdocs configuration to enable this target."
	@mkdir -p $(DOC_DIR)

.PHONY: tree
tree: ## Print a high-level directory tree (skipping caches/build artifacts)
	@find . -maxdepth 4 \
		-not -path '*/\.*' \
		-not -path '*/__pycache__*' \
		-not -path '*/dist*' \
		-not -path '*/build*' \
		-not -path '*/.venv*' \
		-not -path '*/node_modules*' \
		| sort

# =============================================================================
# Meta
# =============================================================================
.PHONY: info
info: ## Print resolved Make variables (useful for debugging)
	@echo "PLATFORM     = $(PLATFORM)"
	@echo "PY           = $(PY)"
	@echo "PACKAGE      = $(PACKAGE)"
	@echo "VERSION      = $(VERSION)"
	@echo "SRC_DIR      = $(SRC_DIR)"
	@echo "TESTS_DIR    = $(TESTS_DIR)"
	@echo "DIST_DIR     = $(DIST_DIR)"
	@echo "OUTPUT_BIN   = $(OUTPUT_BIN)"
	@echo "VENV_DIR     = $(VENV_DIR)"

.PHONY: version
version: ## Print the project version (from pyproject.toml)
	@echo "$(VERSION)"

.PHONY: deps-print
deps-print: ## Print the dependency lists
	@echo "Runtime:"; echo ' $(RUNTIME_DEPS)' | tr ' ' '\n' | sed 's/^/  /'
	@echo "Dev:    "; echo ' $(DEV_DEPS)'     | tr ' ' '\n' | sed 's/^/  /'
	@echo "Build:  "; echo ' $(BUILD_DEPS)'   | tr ' ' '\n' | sed 's/^/  /'