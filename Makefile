.PHONY: run clean

all:
	python xbt.py

xbt:
	make -C lexer/
clean:
	make -C lexer/ clean