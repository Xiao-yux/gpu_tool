OUTPUT = dist/gpu_tool
SOURCE = main.py
CC     = clang
PIP_DEPS = noneprompt toml Nuitka text2art art tqdm

build:
	python -m nuitka --onefile --standalone --lto=yes --assume-yes-for-downloads\
	    --clang --include-package=core --include-package=menu --include-package=utils \
		--include-data-dir=bash=bash --show-progress --enable-plugins=upx \
	    --include-data-file=config.toml=config.toml \
	    --output-dir=dist --output-filename=gpu_tool --remove-output $(SOURCE)

clean:
	rm -rf dist main.build main.dist

install:
	apt update && apt install -y gcc g++ clang lld make patchelf python3-dev ccache python3 python3-pip
	pip install --upgrade pip
	pip install $(PIP_DEPS)

run :
	$(OUTPUT)
.PHONY: build clean install



