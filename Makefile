.PHONY: run clean

all:
	python xbt.py build.xbt

xbt:
	make -C lexer/
clean:
	make -C lexer/ clean