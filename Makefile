OUTPUT = dist/main
SOURCE = main.py
CC     = clang

nuitka:
	python -m nuitka --onefile --standalone --lto=yes --assume-yes-for-downloads\
	    --clang --include-package=core --include-package=menu --include-package=utils \
		--include-data-dir=bash=bash --show-progress\
	    --include-data-file=config.toml=config.toml \
	    --output-dir=dist --output-filename=gpu_tool --remove-output $(SOURCE)

clean:
	rm -rf dist main.build main.dist

.PHONY: nuitka clean



