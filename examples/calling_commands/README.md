# Calling Rules Directly
The user can directly call rules from the command line. When calling
rules directly, all rules below the specified rule will also be ran.
However, no rule above the specified rule will be ran.

## Example

build.xbt
```
rule Main {
    $ echo "Running Main"
}

rule World {
    $ echo "World!"
}

rule Hello {
    $ echo "Hello"
}
```

In this example, we are wanting to run the rule "Hello", then the
"World". The output should be:

```
Hello
World!
```

To run this build, run `xbt World` from the command line.
