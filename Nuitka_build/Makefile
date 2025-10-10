OUTPUT = dist/main
SOURCE = main.py
CC     = clang

nuitka:
	python -m nuitka --onefile --standalone --lto=yes \
	    --clang --include-package=utils \
	    --include-data-file=config.toml=config.toml \
	    --output-dir=dist --output-filename=main --remove-output $(SOURCE)

upx:
	upx --best $(OUTPUT)

clean:
	rm -rf dist main.build main.dist

.PHONY: nuitka upx clean