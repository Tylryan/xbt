# XBT (X Build Tool)

# XBT Lang
## Motivation
I wanted a build tool that followed an incremental compile approach similar to Make, 
but with different features and in a language that is more intuitive to me. So 
instead of looking around, I figured I'd try to make my own.

Suppose you were writing a program that takes in `some-file.txt` as a command line
argument like `./a.out some-file.txt` and that everytime `some-file.txt` got updated,
you could run `make` and it would compile some set of shell commands. The file
would looks something like this right?
> In the next section, the same example is done with xbt.
```make
# If some-file.txt changes,
# then execute the following commands.
all: a.out some-file.txt
    ./a.out $^
    
# If main.c, or helper.o or change, 
# then execute the following commands.
a.out: main.c helper.o
    gcc -o $@ $^
    $@ some-file.txt

# If helper.c, helper.o, or helper.h change,
# then execute the following commands.
helper.o: helper.c helper.o helper.h
    gcc -o $@ -c $^
```

## At A Glance
The program is a set of rules (`rule`) where each rule contains a set of input files 
(`build_files`), a set of output files (`output_files`), and a set of shell commands
to execute. The program loops through the set of rules in the opposite order in which
they were declared. For each rule, if any of the input files are newer than the output 
files, then execute that rule's set of shell commands; else skip.

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

rule Helper {
    build_files : "${PREFIX}/helper.c" .
    /* If "helper.h" is changed, it should
     * trigger the shell commands. They
     * just aren't used in the shell commands
     */
    watch_files : "${PREFIX}/helper.h" .
    output_files: "${PREFIX}/helper.o" .

    $ gcc -o $output_files -c $build_files
}

/* This would be the first thing executed if
 * "hello.txt" is updated.
 */
rule Email {
    watch_files: "hello.txt" .

    $ python email_self.py $watch_files .
}
```


## Build
There are only two dependencies:
- 1. `make`:
- 1. `antlr4`: > 4.13.2
- 2. `python`: > 3.12.6

Simply run `make`.