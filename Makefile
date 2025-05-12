# make clean compile run
EXAMPLE_BUILD=build.xbt
XBT=xbt.py

.PHONY: clean lexer run

# EXPECTED BEHAVIOR
# 	When the user runs `make`:
# 	1. Check if "XbtLexer.g4" is newer
# 	   than "XbtLexer.py". If so, then run
#	   the antlr4 command. Else skip.
#	2. Check if "xbt.py" OR "XbtLexer.g4"
#	   are newer than "dist/xbt". If so,
#	   then run the pyinstaller command.
#	   Else, skip.
# ACTUAL BEHAVIOR
# 	In this case because all rules/targets are actually file
# 	outputs from the commands they execute, it works
# 	as expected.
dist/xbt: xbt.py lexer/XbtLexer.py
	pyinstaller xbt.py -F

# output_file: input_file
lexer/XbtLexer.py: lexer/XbtLexer.g4
	# shell commands
	antlr4 $^ -Dlanguage=Python3


# Command line arguments
clean:
	rm -rf dist*
	make -C lexer/ clean

run:
	./dist/xbt $(EXAMPLE_BUILD)

lexer:
	make lexer/XbtLexer.py