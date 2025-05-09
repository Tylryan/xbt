.PHONY: clean

XbtLexer.tokens: XbtLexer.g4
	antlr4 $^ -Dlanguage=Python3


clean:
	rm Xbt.interp Xbt*.py Xbt*.tokens