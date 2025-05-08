.PHONY: run clean

all:
	python xbt.py

clean:
	make -C lexer/ clean