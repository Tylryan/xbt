from __future__ import annotations

from antlr4 import *
from lexer.XbtLexer import XbtLexer

from parser.exprs import Expr
from parser.xbt_parser import parse
from xbt_utils import read_file
from interpreter.xbt_interpreter import interpret




def main(args: Args):
    path       = args.build_file
    entry_rule = args.entry_rule

    global global_env
    global rules_ran

    # TODO(tyler): Make command line more robust.
    # currently real easy to crash.

    # source: str = read_file(sys.argv[1])
    source: str = read_file(path)
    lexer: XbtLexer = XbtLexer(InputStream(source))
    exprs: list[Expr] = parse(lexer)
    interpret(args, exprs)


if __name__ == "__main__":
    import sys
    from cli.xbt_cli import Args

    args = Args()
    if len(sys.argv) == 1:
        args.build_file = "build.xbt"

    # NOTE(tyler): Assuming the user passes args correctly.
    elif sys.argv[1] == "-f":
        args.build_file = sys.argv[2]

    elif sys.argv[1] == "-r":
        args.build_file = "build.xbt"
        args.entry_rule = sys.argv[2]
    else:
        args.build_file = "build.xbt"
        args.commands = sys.argv[1:]

    main(args)