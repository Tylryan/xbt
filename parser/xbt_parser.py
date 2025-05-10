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

        expr: Expr = parse_globals()
        if expr:
            exprs.append(expr)

    # from pprint import pprint
    # [ pprint(x.as_dict(), sort_dicts=False) for x in exprs]
    # exit(1)
    return exprs


def parse_globals() -> Expr:
    if check(parser.lexer.VARIABLE) is False:
        return parse_rule()


    assignment: Assign = parse_assignment()
    assignment.is_global = True
    return assignment

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
    
    # Keywords
    if matches(parser.lexer.BUILD_FILES): return parse_build_files()
    if matches(parser.lexer.OUT_FILES)  : return parse_out_files()
    if matches(parser.lexer.WATCH_FILES): return parse_watch_files()
    
    return parse_assignment()

def parse_shell() -> Expr:
    # '$' .* '\n' ;
    return Shell(prev())

def parse_member_access() -> Expr:
    err_msg = "Expected parse_member_access to start with" \
              f"an identifier. Found '{peek()}'"

    assert check(parser.lexer.IDENT), err_msg
    # member_access := IDENT '::' IDENT '.' ;
    rule_name: Token = advance()

    err_msg = "Expected a '::' when accessing a Rule member."
    consume(parser.lexer.DCOLON, err_msg)

    err_msg = "Missing member in member access expression."
    member: Token = consume(parser.lexer.VARIABLE, err_msg)
    return MemberAccess(rule_name, member)

def parse_build_files() -> Expr:
    # build_files := "build_files" STRING+ "." ;
    keyword: Token = prev()

    consume(parser.lexer.COLON,
            "Missing ':' in 'build_files' declaration.")
    
    if check(parser.lexer.DOT):
        error(peek().line, peek().column,
              f"Missing values in 'build_files' declaration.")


    files: list[Expr] = []
    while not (at_end() or check(parser.lexer.DOT)):
        if checks(parser.lexer.STRING, parser.lexer.VARIABLE):
            files.append(parse_primary())

        # I only expect something like Rule::member
        # here.
        if check(parser.lexer.IDENT):
            member: MemberAccess = parse_member_access()
            files.append(member)
    

    consume(parser.lexer.DOT ,
            f"Missing '.' in 'build_files' statement.")

    return BuildFiles(keyword, files)

def parse_out_files() -> Expr:
    # build_files := "build_files" STRING+ "." ;
    keyword: Token = prev()

    consume(parser.lexer.COLON,
            "Missing ':' in 'out_files' declaration.")

    if check(parser.lexer.DOT):
        error(peek().line, peek().column,
              f"Missing values in 'build_files' declaration.")

    files: list[Expr] = []
    while at_end() is False and check(parser.lexer.STRING):
        files.append(parse_primary())
    
    consume(parser.lexer.DOT,
            f"Missing '.' in 'out_files' statement.")
    return OutFiles(keyword, files)

def parse_watch_files() -> Expr:
    # build_files := "build_files" STRING+ "." ;
    keyword: Token = prev()

    consume(parser.lexer.COLON,
            "Missing ':' in 'watch_files' declaration.")

    if check(parser.lexer.DOT):
        error(peek().line, peek().column,
              f"Missing values in 'build_files' declaration.")

    files: list[Expr] = []
    while at_end() is False and check(parser.lexer.STRING):
        files.append(parse_primary())
    
    consume(parser.lexer.DOT,
            f"Missing '.' in 'watch_files' statement.")
    return WatchFiles(keyword, files)

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
    
    if check(parser.lexer.DOT):
        error(peek().line, peek().column,
              f"Missing values in assignment expression for "
              f"variable '{var.token.text}'.")


    while check(parser.lexer.STRING) or check(parser.lexer.VARIABLE):
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

def checks(*kinds: int) -> bool:
    for kind in kinds:
        if peek().type == kind:
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
    return parser.prev


if __name__ == "__main__":
    from lexer.XbtLexer import lex
    from xbt_utils import read_file



