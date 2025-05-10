# XBT (X Build Tool)

# XBT Lang
## Motivation
I wanted a build tool that followed an incremental compile approach similar to Make, but with different features and in a language that is more intuitive to me. So instead of looking around, I figured I'd try to make my own.

## At A Glance
> For a more in depth look into the language, see 
> [XBT Lang Introduction](./docs/xbt_lang/language_intro.md)
```
/* Rules are executed in the reverse order they
 * are defined (LIFO), where the top-most rule 
 * (in this case 'SomeRule') is executed last.
 */

/* Global Variables */
$PROJECT_DIR = "examples/c_project" .

rule Entry {
    /* Local Members */
    build_files: "${PROJECT_DIR}/main.c"
                 Helper::$output_files    .
    output_files: "a.out"                 .

    /* User Defined Members */
    $my_var = "DONE!".

    /* Access to local members */
    $ gcc -o $build_files ; echo $my_var

    /* Access to other Rule members. */
    $ echo Helper outputs Helper::$output_files
}

rule Helper {
    build_files: "${PROJECT_DIR}/helper.c"  .
    output_files: "${PROJECT_DIR}/helper.o" .

    $ gcc -o $output_files -c $build_files
}
```


## Build