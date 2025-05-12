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
```
/* Declare global variables */
$PREFIX = "" .


/* This rule can be given any name */
rule Run {
    watch_files: "${PREFIX}/some-file.txt" .

    $ Main::output_files $watch_files
}

/* 'Main' will be the last rule to execute */
rule Main {
    /* Designated Members */
    build_files : "${PREFIX}/main.c" 
                   Helper::$output_files .

    output_files: "${PREFIX}/a.out"      .

    /* User Defined Members */
    $exit_message = "Done compiling!"    .

    /* Shell Commands */
    $ gcc -o $@ $^ $#
    $ gcc -o $output_files $build_files
    $ echo $exit_message
}

/* If "helper.h" is changed, it should
    * trigger the shell commands. They
    * just aren't used in the shell commands
    */
rule Helper {
    /* The '!' indicates a helper file. If
     * the helper file is updated, the rule
     * will run, but it won't be included
     * when referencing $^ or $build_files.
     */
    build_files : "${PREFIX}/helper.c" 
                  !"${PREFIX}/helper.h .
    output_files: "${PREFIX}/helper.o" .

    $ gcc -o $output_files -c $build_files

    OUTPUT
    gcc -o ..helper.o -c ..helper.c
}

/* This would be the first thing executed if
 * "hello.txt" is updated.
 */
rule Email {
    $^: "hello.txt" .
    $ python email_self.py $^
}
```


## Build
Below are the prerequisite programs required to be on your
machine if you would like to build Xbt from source.
1. `make`       : > 4.4.1
2. `antlr4`     : > 4.13.2
3. `python`     : > 3.12.6
4. `pyinstaller`: > 6.11.0

To build this project, simply run `make`. This will compile
the lexer (Antlr) and create a binary stored in `dist/xbt`.

Currently, `xbt` requires the path a build file. If you would like 
an example build file to test, you can look for `build.xbt` in the 
[examples directory](./examples) or rebuild Xbt itself using the 
`build.xbt` file in the project's root directory (AKA where this 
README is located).