from antlr4 import *


from lexer.XbtLexer import XbtLexer
from parser.xbt_parser import parse
from xbt_utils import read_file
from parser.exprs import *

from sys import stdout


global global_env
global_env = {}
global rules_ran
rules_ran = 0

def notify(message: str) -> None:
    print(message)
    stdout.flush()



def main():
    global global_env
    global rules_ran

    source: str = read_file("test.xbt")
    lexer: XbtLexer = XbtLexer(InputStream(source))
    exprs: list[Expr] = parse(lexer)[::-1]

    for expr in exprs:
        evaluate(expr, {})
        
    if not rules_ran:
        print("No rules ran. Nothing to do.")

def evaluate(expr: Expr, local_env: dict[str, object]) -> object:
    if expr is None:
        return None

    if isinstance(expr, Rule)    : return eval_rule(expr)
    if isinstance(expr, Shell)   : return eval_shell(expr)
    if isinstance(expr,Comment)  : return eval_comment(expr)
    if isinstance(expr, Assign)  : return eval_assign(expr, local_env)
    if isinstance(expr, Literal) : return eval_literal(expr)
    if isinstance(expr, Variable): return eval_variable(expr, local_env)
    else: error(f"[interpreter-error] unimplemented expression: {expr}")


def eval_rule(rule: Rule) ->  None:
    # Nested rules are not allowed as of, so 
    global global_env
    global rules_ran
    # If rule name already exists, throw an error.
    rule_name = rule.name.token.text
    l: int = rule.name.token.line
    c: int = rule.name.token.column
    if rule_name in global_env.keys():
        error(l, c, f"rule name already declared: '{rule_name}'.")
    
    # Define rule
    global_env[rule_name] = rule

    for e in rule.exprs:
        if isinstance(e, Assign):
            # TODO(tyler): Should I check to make sure
            # there are no redefinitions?
            rule.environment[e.variable.token.text] = evaluate(e.value, global_env)

    if "build_files" not in rule.environment.keys():
        error(l, c, f"'build_files' was not assigned in rule '{rule_name}'.")
    if "output_files" not in rule.environment.keys():
        error(l, c, f"'output_files' was not assigned in rule '{rule_name}'.")

    build_file : str = rule.environment["build_files"][1:-1]
    output_file: str = rule.environment["output_files"][1:-1]

    import os
    if os.path.isfile(build_file) is False:
        error(l, c, f"file path '{build_file}' in rule '{rule_name}' does not exist.")

    output_exists = os.path.isfile(output_file)

    # NOTE: The key to the whole show
    build_time  = os.path.getctime(build_file)
    output_time = os.path.getctime(output_file) if output_exists else 0
    if build_time < output_time:
        return (False, rule_name)

    [ evaluate(expr, rule.environment) for expr in rule.exprs ]
    rules_ran+=1

    return (True, rule_name)

def eval_shell(shell: Shell) ->  None:
    command: str = str(shell.commands.text)[1:].strip()
    print(f"$ {command}")

    import os
    res = os.popen(command)
    [ notify(x) for x in res.readlines() ]
    res.close()
    return None

def eval_comment(comment: Comment) -> None:
    #print(f"COMMENT: ", comment.token.text)
    return None

def eval_variable(variable: Variable, local_env: dict[str, object]) -> None:
    variable_name = variable.token.text
    if variable_name in local_env.keys():
        return local_env[variable_name]

    if variable_name in global_env.keys():
        return global_env[variable_name]
    
    error(variable.token.line, variable.token.column,
          f"undefined variable: {variable_name}")

def eval_assign(assign: Assign, local_env: dict[str, object]) -> None:
    value: object = evaluate(assign.value, local_env)
    local_env[assign.variable.token.text] = value
    return None

def eval_literal(literal: Literal) -> None:
    return literal.token.text

def error(line: int, col: int, message: str) -> None:
    print(f"[interpreter-error][{line}:{col}] {message}")
    exit(1)

if __name__ == "__main__":
    main()