from __future__ import annotations


from antlr4 import Token
from lexer.XbtLexer import XbtLexer
from parser.exprs import *

class Parser:
    index: int
    lexer: XbtLexer
    peek: Token
    prev : Token

    def __init__(self, lexer: XbtLexer):
        self.lexer = lexer
        self.peek = None
        self.prev = None

global parser
def parse(lexer: XbtLexer) -> list:
    global parser
    parser = Parser(lexer)

    exprs: list[Expr] = []
    # Load the initial token
    advance()

    while True:
        if peek() and peek().type == Token.EOF:
            break

        expr: Expr = parse_rule()
        if expr:
            exprs.append(expr)

    # from pprint import pprint
    # [ pprint(x.as_dict(), sort_dicts=False) for x in exprs]
    # exit(1)
    return exprs


def parse_rule() -> Expr:
    if matches(parser.lexer.RULE) is False:
        return parse_expression()

    name: Variable = parse_primary()

    consume(parser.lexer.LBRACE,
            f"missing '{{' in rule declaration for '{prev().text}'.")

    exprs: list[Expr] = []
    while at_end() is False:
        if check(parser.lexer.RBRACE):
            break
        expr: Expr = parse_expression()
        exprs.append(expr)

    consume(parser.lexer.RBRACE,
            f"missing '}} after rule declaration for '{prev().text}'.")
    return Rule(name, exprs)

def parse_expression() -> Expr:
    if matches(parser.lexer.SHELL):
        return parse_shell()
    
    return parse_assignment()

def parse_shell() -> Expr:
    # '$' .* '\n' ;
    return Shell(prev())

def parse_assignment() -> Expr:

    l: int = line()
    c: int = column()
    expr: Expr = parse_primary()

    if matches(parser.lexer.EQUAL) is False:
        return expr

    if isinstance(expr, Variable) is False:
        error(l,c,
              "You are attempting to assign a expression to "
              "something that clearly isn't a storage type.")

    var: Variable = expr
    values: list[Expr] = []
    
    while check(parser.lexer.STRING):
        values.append(parse_expression())

    consume(parser.lexer.DOT,
            "Missing '.' in variable assignment.")
    return Assign(var, values)

def parse_primary() -> Expr:

    if matches(parser.lexer.VARIABLE):
        token: Token = prev()
        token.text = token.text[1:]
        return Variable(token)
    if matches(parser.lexer.IDENT):
        return Variable(prev())
    if matches(parser.lexer.ML_COMMENT):
        return Comment(prev())
    if matches(parser.lexer.STRING, parser.lexer.PATH):
        return Literal(prev())
    # if matches(parser.lexer.NEW_LINE):
    #     advance()
    else:
        error(peek().line, peek().column, 
              f"Unimplementd type: {peek().text}, type: {peek().type}")











def position() -> tuple[int, int]:
    return (line(), column())

def line() -> int:
    global parser
    return parser.peek.line

def column() -> int:
    global parser
    return parser.peek.column


def at_end() -> bool:
    return peek() and peek().type == Token.EOF

def consume(kind: int, err_message: str) -> Token:
    if matches(kind):
        return prev()

    l: int = peek().line
    c: int = peek().column
    error(l, c, err_message)

def error(line: int, col: int, message: str) -> None:
    print(f"[parser-error][{line}:{col}] {message}")
    exit(1)

def matches(*kinds: int) -> bool:
    to_match = peek().type

    for kind in kinds:
        if kind == to_match:
            advance()
            return True
    return False

def check(kind: int) -> bool:
    return peek().type == kind

def peek() -> Token:
    global parser
    return parser.peek

def prev() -> Token:
    global parser
    return parser.prev

def advance() -> Token:
    global parser
    parser.prev = parser.peek
    parser.peek = parser.lexer.nextToken()


if __name__ == "__main__":
    from lexer.XbtLexer import lex
    from xbt_utils import read_file



