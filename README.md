# XBT (X Build Tool)

# XBT Lang

**build_files**: Files required for toolchain command. For example, `.o` and `.c` files.
**watch_files**: Any file you would like to compare change timestamps with your output_files. For example, `.h` files.
**output_files**: Also known as Target Files. These are the files a rule will produce. For example, `a.out` files.


```
LIFO (stack)
FIFO (queue)

/* Rules are executed in the reverse order they
 * are defined (LIFO), where the top-most rule 
 * (in this case 'SomeRule') is executed last.
 */
rule SomeRule {
    build_files  = "main.c";
    output_files = "a.out";

    $ gcc main.c aux.o
    $ ./a.out
}

rule DependencyRule {
    watch_files  = "aux.h";
    build_files  = "aux.c";
    output_files = "aux.o";

    /* NOTE */
    $ gcc -o aux.o aux.c


}
```
## Building
