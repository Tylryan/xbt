.PHONY: run clean


xbt:
	make -C lexer/

run:
	python xbt.py build.xbt

clean:
	make -C lexer/ clean