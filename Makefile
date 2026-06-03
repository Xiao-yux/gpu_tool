OUTPUT = dist/gpu_tool
SOURCE = main.py
CC     = clang
PIP_DEPS = noneprompt toml Nuitka text2art art tqdm aiofiles websockets asyncio Nuitka[onefile] openpyxl
# 		--clang 

build:
	source ./.venv/bin/activate && \
	export CCACHE_LINK=ccache && \
	python -m nuitka \
		--onefile \
		--onefile-no-compression \
		--onefile-tempdir-spec="{CACHE_DIR}/gpu_tool" \
		--onefile-cache-mode=cached \
		--lto=yes \
		--static-libpython=yes \
		--assume-yes-for-downloads \
		--enable-plugins=upx \
		--upx-binary=/usr/bin/upx \
		--product-name="gpu_tool" \
		--noinclude-default-mode=allow \
		--include-data-dir=bash=bash \
		--include-data-file=config.toml=config.toml \
		--output-dir=dist \
		--output-filename=gpu_tool \
		--remove-output \
		--show-progress \
		$(SOURCE)
#  --include-package=websockets

clean:
	rm -rf dist main.build main.dist

install:
	apt update && apt install -y gcc g++ clang lld make patchelf python3-dev ccache python3 python3-pip
	pip install --upgrade pip
	pip install $(PIP_DEPS)

run :
	$(OUTPUT)

.PHONY: build clean install



