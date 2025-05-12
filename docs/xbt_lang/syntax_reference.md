**Grammar**
```ebnf
Program := Rule*
        | GlobalAssignment*;

Rule    := 'rule' IDENT '{' Expr* '}' ;

Expr    := MemberDeclaration
        | ShellCommand ;

MemberDeclaration := '$'IDENT '=' ( STRING | MEMBER ) '.'
                  | DESIGNATED_MEMBER ':' '!'? ( STRING | MEMBER ) '.' ;

ShellCommand := '$ ' (STRING | MEMBER )+ '\n';

DESIGNATED_MEMBER := 'build_files'
                  | 'output_files' ;
```

**Rules**

```
rule MyRule {
    /* Members Go here*/

    /* Shell commands go here */
}
```

**Members**
```
$user_defined_member_1 = "string"        .
$user_defined_member_2 = $other_variable .

build_files : "main.c" .
output_files: "a.out"  .
```

**`$`: Shell Commands**
```
$ gcc -o $output_files -c $build_files
```

**`!`: Helper Files**  
As of 0.2.0, the `!` operator is only valid
when declaring `build_files` (a.k.a `$^`).
```
build_files: "other.c" !"other.h" .
```

**String Interpolation**
```bash
$HOME = "/home/name" ;
$DOCS="${HOME}/documents";
```
**Assigning a Set of values**
```bash
build_files: "a.c" "b.c" "e.c"  "d.c";
```

**Variable Referencing Within Shell**
```bash
build_files: "one.c"  "two.c";
... code
$ gcc $build_files ;
```

**Forward Referencing Rule Members**  
The user can forward reference Rules and their members. This makes declaring 
'build_files' a little easier since they can reference a variable instead of 
retyping every file path . In the example below, the Entry rule declares it's 
'build_files' to be:
1) ..."main.c"
2) `Helper::$output_files`

> `Helper::$output_files` would be expanded to "helper.o".

```
rule Entry {
    /* Below, 'Helper::$output_files' would 
     * return "helper.o" 
     */
    build_files  : "main.c" 
                    Helper::$output_files .
    output_files : "a.out"                .

    $ gcc -o $output_files $build_files
}

/* This rule would always run as it doesn't 
 * declare 'build_files'. It's also a useless
 * rule :)
 */
rule Helper {
    output_files : "helper.o" .

    $ echo "Running Helper"
}
```