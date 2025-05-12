.PHONY: clean compile

XbtLexer.py: XbtLexer.g4
	antlr4 $^ -Dlanguage=Python3

compile:
	make XbtLexer.py

clean:
	rm Xbt*.interp Xbt*.py Xbt*.tokens