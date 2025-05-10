# XBT (X Build Tool)

# XBT Lang

**build_files**: Files required for toolchain command. For example, `.o` and `.c` files.  
**watch_files**: Any file you would like to compare change timestamps with your output_files. For example, `.h` files.  
**output_files**: Also known as Target Files. These are the files a rule will produce. For example, `a.out` files.  

## At A Glance
```
/* Rules are executed in the reverse order they
 * are defined (LIFO), where the top-most rule 
 * (in this case 'SomeRule') is executed last.
 */

/* TODO(tyler): Helper::output_files */
rule Entry {
    $project_dir  = "examples/c_project"   .
    build_files  : "${project_dir}/main.c" 
                    Helper::$output_files  .
    output_files : "${project_dir}/a.out"  .

    $clean = $output_files .

    $ gcc -o $output_files $build_files
}

rule Helper {
    $project_dir  = "examples/c_project"      .
    build_files  : "${project_dir}/helper.c"  .
    watch_files  : "${project_dir}/helper.h"  .
    output_files : "${project_dir}/helper.o"  .
    
    $clean = $output_files .

    $ echo "Running Helper"
}

/* Commands are like 'make [command]' 
 * and are not ran unless specified.*/

/* command clean { 
 *  $clean_files = Entry.$clean
 *  $ rm $clean_files
 * } 
 */
```
## Building
TODO

## Language Overview
TODO
- Executes rules bottom up.
- 'rule'

### Rules
Rules are names given to a set of shell commands and are declared so:
```
rule Shout {
    $ echo "LET IT ALL OUT!"
}
```

A rule 
A rule is split up into two sections:
- The Noun Section (Data)
- The Verb Section (Shell)
```
rule Animal {
    /* The Noun section */
    $build_files = "animal.c";
    $output_files = "animal.o";

    /* The Verb section */
    $ gcc -o animal.o animal.c
}
```
- '$variables'
- '$'
### String Interpolation
```bash
$HOME = "/home/name" ;
$DOCS="${HOME}/documents";
```
### Assigning a Set of values
```bash
$build_files = "a.c" "b.c" "e.c"  "d.c";
```
### Variable Referencing Within Shell
```bash
$build_files = "one.c"  "two.c";
... code
gcc $build_files ;
```

## Forward Referencing Rule Members
The user can forward reference Rules and their members. This makes declaring 'build_files' a little easier since they can reference a variable instead of retyping every file path . In the example
below, the Entry rule declares it's 'build_files' to be:
1) ..."main.c"
2) `Helper::$output_files`

> `Helper::$output_files` would be expanded to "examples/c_project/helper.o".
```
rule Entry {
    $project_dir  = "examples/c_project"      .
    /* Below, 'Helper' would return "examples/c_project/helper.o" */
    build_files  : "${project_dir}/main.c" Helper::$output_files  .
    output_files : "${project_dir}/a.out"  .

    $ gcc -o $output_files $build_files
}

/* This rule would always run as it doesn't declare 'build_files'. */
rule Helper {
    $project_dir  = "examples/c_project"      .
    output_files : "${project_dir}/helper.o"  .

    $ echo "Running Helper"
}
```