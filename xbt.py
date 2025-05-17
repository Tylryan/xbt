from __future__ import annotations

from antlr4 import *
from lexer.XbtLexer import XbtLexer

from cli.xbt_cli import cli, Args
from parser.exprs import Expr
from parser.xbt_parser import parse
from xbt_utils import read_file
from interpreter.xbt_interpreter import interpret


def main(args: Args):
    global global_env
    global rules_ran

    # TODO(tyler): Make command line more robust.
    # currently real easy to crash.

    source: str        = read_file(args.build_file)
    lexer : XbtLexer   = XbtLexer(InputStream(source))
    exprs : list[Expr] = parse(lexer)
    interpret(args, exprs)

    return 0


if __name__ == "__main__":
    from cli.xbt_cli import Args

    args: Args = cli()
    main(args)