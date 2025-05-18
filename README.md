# XBT (X Build Tool)
## XBT Lang At A Glance
The program is a set of rules (`rule`) where each rule contains a set of input files 
(`build_files`), a set of output files (`output_files`), and a set of shell commands
to execute. The program loops through the set of rules in the opposite order in which
they were declared. For each rule, if any of the input files are newer than the output 
files, then that rule's set of shell commands will be
executed. 
> In short, if a rule's input files are newer than its output files,
> then the rule will execute it's shell commands.

In order for a rule to be conditionally executable, you must declare two of the following:
1. `build_files` : Aliased to `$^`
2. `output_files`: Aliased to `$@`
3. `helper_files`: Aliased to `'!' (STRING | MEMBER)`. Can only be used when declaring 
   `build_files` as of right now.

However, if you want to have a rule run everytime, then don't declare `build_files` 
and/or `output_files`.

> For a more in depth look into the language, see 
> [XBT Lang Introduction](./docs/xbt_lang/language_intro.md)

Below is the build script currently being used for XBT itself.
```
/* Commands that can be called from the
 * command line: `xbt clean compile run`
 */
cmd run     { $ echo "RUNNING!"      }
cmd clean   { $ rm Xbt::$clean       }
cmd compile { $ python xbt.py -r Xbt }

/* The first rule defined is the last to
 * execute.
 */
rule Xbt {
	/* If the three input files below are
	 * newer than the output files ($@)
	 * below, then run this rule. The two
	 * following members below are called
	 * "Designated Members".
	 */
	$^ : "xbt.py" "parser/xbt_parser.py"  
				  !Lexer::$@              .
	$@: "dist/xbt"                        .

	/* User defined members */
	clean    : $@ .
	exit_msg : "Done!" .

	/* Shell commands to run if this rule
	 * triggers.
	 */
	$ pyinstaller $^ -F
	$ echo Lexer::$@
}

/* If "lexer/XbtLexer.g4" is newer than "XbtLexer.py" OR 
 * XbtLexer.py doesn't exist, then run the antlr4 command. 
 * Else, don't execute the shell commands.
 */
rule Lexer {
	build_files : "lexer/XbtLexer.g4"           .
	output_files: "lexer/XbtLexer.py"           .

	clean : $@ .

	$ antlr4 $build_files -Dlanguage=Python3
}
```

## Build
Below are the prerequisite programs required to be on your
machine if you would like to build Xbt from source.
1. `make`       : >= 4.4.1
2. `antlr4`     : >= 4.13.2
3. `python`     : >= 3.12.6
4. `pyinstaller`: >= 6.11.0

To build this project, simply run `make`. This will compile
the lexer (Antlr) and create a binary stored in `dist/xbt`.

If you would like an example build file to test, you can look for 
`build.xbt` in the [examples directory](./examples) or rebuild Xbt 
itself using the `build.xbt` file in the project's root directory 
(AKA where this README is located).