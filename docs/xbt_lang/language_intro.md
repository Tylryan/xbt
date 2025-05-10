# XBT Language
## The Basics
> See the [XBT Syntax Reference](./syntax_reference.md) page for more information about 
> XBT's syntax.

**Execution Order**  
TODO: Describe this  


**Rules**  
The `rule` keyword declares a new set of commands to be executed in the reverse order they are declared. A rule is split up
into two sections: 1) Declarations, 2) Shell commands.

```
rule Entry {
    /* Declarations */
    build_files : "main.c" "other.o" .
    output_files: "a.out"            .
    $user_defined_var = "hello world".
    $other_var        = $output_files.

    /* Shell Scripts */
    $ gcc -o $output_files $build_files
    $ echo "DONE!"
}
```
**Members**  
The declaration section is where rule members are defined. Members come in two flavors:
1. **Designated Member**: E.g. `build_files`
2. **User Defined Member**: E.g. `$user_defined_var`

The user can declare their own members by using the `$member = EXPR` syntax.

In any given rule, there may or may not be `members` declared. However, if a rule does not declare any members, it will always be executed. So if you want a rule to be ran every
every time you compile, then don't declare the Designated Rules. Below is a list and
description of these Designated Members:
1. **build_files**: Files required for toolchain command. For example, `.o` and `.c` files.  
2. **output_files**: Also known as Target Files. These are the files a rule will produce. For example, `a.out` files.  
3. **watch_files**: Any file you would like to compare change timestamps with your output_files. For example, `.h` files.  
> A build will only execute a rule conditionally if both the `build_files` 
> and `output_files` members are declared. In other words, if either is 
> not declared, then the rule will *always* run.

From the programmer's perspective, a designated member behaves like a user defined member and is just syntactically different.