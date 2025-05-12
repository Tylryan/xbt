FUTURE STATE
```bash
$ xbt
```
- searches up your directory tree until it finds a .xbt file.
- interprets the .xbt file.

```ebnf
xbt_init := 'xbt' 'init' entry-path? direct_dependency*? ;
```

```bash
$ xbt init main.c ./people/person.c
```
> 1. List the dependencies in order.  
> 2. Running `xbt init` would have no entry and guess the order.

DONT FORGET!
You can run incrementally or just randomly. Incrementally if you
set `build_files: Dependency::$output_files`, or just using
the "if newer" approach. Think more like a batch job.

If helper.* changed, compile it again.

It would spit out a `build.xbt` file that looked like this:
Make it nice like this so that people can more easily modify it.
```
$ROOT="/home/me/projects/pong"  .

/* Command Line arguments */
$ENTRY="${ROOT}/main.c"
/* It is a direct dependency  */
$PERSON="${ROOT}/people/person" .

/* Found Files */
$HELPER="${ROOT}/helper/helper" .


```
rule Entry {
    build_files: $ENTRY Person::$output_files .

}

rule Person {
    build_files : "${PERSON}.c" .
    helper_files: "${PERSON}.h" .
    output_files: "${PERSON}.o" .

    $ gcc -o $output_files -c $build_files
}


/* Below would be treated like a boxes in a batch 
 * job.
 * E.g. If helper.h or helper.c are newer than
 * helper.o, then recompile. 
 */
rule Helper {
    build_files : "${HELPER}.c" .
    helper_files: "${HELPER}.h" .
    output_files: "${HELPER}.o" .

    $ gcc -o $output_files -c $build_files
}


USER DEFINED FUNCTIONALITY
- Transform directories into a tree of paths in memory
- This tree represents dependencies where children are
  dependencies of their parents.
  - children of the same parent would be executed from
  - left to right like a batch job.
- Go through this tree in this order and create Rules
  from them. 
    - build_files: ".c"
    - helper_files: ".h"
    - output_files: ".o"
The order of the tree will give you this:

Throw it in a hashmap and have a global counter.
When entering a node, increment the counter.
Then you could check the output easily.
{
    "values": [
        { 1: "main.c" },
        { 2: "helper.c" },
        { 3: {
            "dir": {
                "values": [ 
                    { 4: "last.c" }
                ]
            }
        }
        }
    ]
}

// Something like this would order them.
def append_node(node, xs) -> list[Node]:
    if null(xs):
        return xs
    return [head(xs)] + append_node(head(xs), tail(xs))

append_nodes = map(append_node)
ordered_list: list[Node] = map(append_nodes, xs)
no_dirs: list[Node] = map(no_dirs, ordered_list)


DEBUG OUTPUT PRECEDENCE
1: "main.c"
2: "helper.c"
4: "last.c"


```
rule Main {
    build_files: "${MAIN}.c" Dep::$build_files .
}

rule Dep {
    build_files: "${DEP}.c" .
}
```
File Structure -> XBT Lang

file_ext: str = get_file_ext("main.h")

def is_known_file_type(file_name: str) -> bool:
    for cr in custom_rules:
        if file_ext in cr["build_exts"]: return True
        if file_ext in cr["helper_exts"]: return True
        if file_ext in cr["output_exts"]: return True
    return False


**xbt.settings**
```json
{
    {
        "custom_rules": [
            /* If any of the inputs are newer than
             * any of the outputs, then run. */
            "c" : {
                /* Inputs */
                "build_exts" : [".c"],
                /* Outputs */
                "helper_exts": [".h"],
                "output_exts": [".o"]
            }
        ]
    }
}
```


INTERESTING EXPERIENCE
Coding the api for a concept to implement in
a language. 