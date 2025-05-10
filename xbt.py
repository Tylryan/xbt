from antlr4 import *


from lexer.XbtLexer import XbtLexer
from parser.xbt_parser import parse
from xbt_utils import read_file, interpolate
from parser.exprs import *

import sys
from sys import stdout

def trim_quote(string: str) -> str:
    assert isinstance(string, str)
    return string[1:-1]
# TODO(tyler): Put this somewhere else
def trim_quotes(strings: list[str]) -> list[str]:
    assert isinstance(strings, list)
    return [trim_quote(s) for s in strings]

global global_env
global_env = {}
global rules_ran
rules_ran = 0

def notify(message: str) -> None:
    print(message)
    stdout.flush()


BUILD_FILES  =  "build_files"
OUTPUT_FILES =  "output_files"
WATCH_FILES  =  "watch_files"

def main():
    global global_env
    global rules_ran

    # TODO(tyler): Make command line more robust.
    # currently real easy to crash.

    # source: str = read_file(sys.argv[1])
    source: str = read_file("build.xbt")
    lexer: XbtLexer = XbtLexer(InputStream(source))
    exprs: list[Expr] = parse(lexer)[::-1]

    # from pprint import pprint
    # [pprint(x.as_dict()) for x in exprs ]
    # exit(1)

    for expr in exprs:
        evaluate(expr, {})
        
    if not rules_ran:
        print("No rules ran. Nothing to do.")

def evaluate(expr: Expr, local_env: dict[str, object]) -> object:
    if expr is None:
        return None

    if isinstance(expr, Rule)    : return eval_rule(expr)
    if isinstance(expr, Shell)   : return eval_shell(expr, local_env)
    if isinstance(expr, MemberAccess): return eval_member_access(expr, local_env)
    if isinstance(expr,Comment)  : return eval_comment(expr)
    if isinstance(expr, Assign)  : return eval_assign(expr, local_env)
    if isinstance(expr, Literal) : return eval_literal(expr)
    if isinstance(expr, Variable): return eval_variable(expr, local_env)
    if isinstance(expr, BuildFiles): return eval_file_dec(expr, local_env)
    if isinstance(expr, OutFiles)  : return eval_file_dec(expr, local_env)
    if isinstance(expr, WatchFiles): return eval_file_dec(expr, local_env)
    else: error(f"[interpreter-error] unimplemented expression: {expr}")

def eval_list(exprs: list[Expr], local_env: dict[str, object]) -> list[object]:
    values: list[object] = []
    for expr in exprs:
        values.append(evaluate(expr, local_env))
    return values

def eval_member_access(expr: MemberAccess, local_env: dict[str, object]) -> str:
    assert isinstance(expr, MemberAccess)
    global  global_env
    # NOTE(tyler): Expects the '$' at the front,
    # but this is not how variables are stored.
    # The are stored without this sign.
    member_name: str = expr.member.text[1:]
    if member_name in local_env.keys():
        return local_env[member_name]

    rule_name: Token =expr.rule_name
    err_msg = f"Undefined Rule: {rule_name.text}"
    if rule_name.text not in global_env.keys():
        error(rule_name.line, rule_name.column,
              err_msg)

    rule: Rule = global_env[expr.rule_name.text]
    if member_name not in rule.environment.keys():
        err_msg = f"Undefined Member: {expr.member.text}."
        error(expr.member.line, expr.member.column,
              err_msg)

    # Note, this returns uninterpolated strings
    res: list[str] = rule.environment[member_name]
    return res


def eval_file_dec(expr: BuildFiles | OutFiles | WatchFiles, 
                  local_env: dict[str, object]) ->  list[str]:

    assert isinstance(expr, BuildFiles | OutFiles  | WatchFiles)

    files: list[str] = []
    for file in expr.files:
        if isinstance(file, Literal):
            res: str = eval_literal(file)
            files.append(res)
        elif isinstance(file, MemberAccess):
            res: list[str] = eval_member_access(file, local_env)
            files = files + res
        else:
            err_msg = f"Invalid expression in '{expr.token.text}' declaration."
            error(expr.token.line, expr.token.col,
                  err_msg)
    return files


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

    # Basically the main entry point as this is the
    # highest level expression allowed.
    for e in rule.exprs:
        # If found an assign, assign the values to the variable.
        if isinstance(e, Assign):
            # TODO(tyler): Should I check to make sure
            # there are no redefinitions?
            values: list[str] = eval_list(e.values, rule.environment)
            rule.environment[e.variable.token.text] = values
        # If found a these specific keywords,
        # then assign their values to the keyword.
        if isinstance(e, BuildFiles | OutFiles | WatchFiles):
            key: str = e.token.text
            # At this point, the user has declared a keyword like
            # 'build_files'. If this evaluation returns an empty
            # list, then the user has forgotten to assign values.
            # This is a syntax error that should be caught by the
            # parser. But just in case, I'll assert it here.
            values: list[str] = eval_file_dec(e, rule.environment)
            assert values, f"The parser should not allow '{key}' to be none"
            rule.environment[key] = values if values else None


    # Immediately pull out the values for the keywords 
    # "build_files" and "output_files".
    build_files: list[str] | None = rule.environment.get(BUILD_FILES, [])
    output_files: list[str]| None = rule.environment.get(OUTPUT_FILES, [])

    # String Interpolation:
    # Replace  potential variables in their values with
    # the expanded values those variables contain.
    if build_files and output_files:
        build_files = [interpolate(f, rule.environment) for f in build_files]
        output_files = [interpolate(f, rule.environment) for f in output_files]

    import os
    from os.path import getctime

    # If the user did not assign a value to one of these 
    # keyword variables then the rule should not do a time 
    # comparison and should simply run the shell scripts
    # every time.
    if build_files == [] or output_files == []:
        eval_list(rule.exprs, rule.environment)
        rules_ran+=1
        return (True, rule_name)

    # At this point, the user has declared the files they wish to
    # watch. If those files don't exist, we should let them know
    # about it.
    def files_exist_check(files: list[str], skip_error: bool = False) -> bool:
        for file in files:
            path_not_exists = os.path.isfile(file) is False
            if path_not_exists and skip_error == False:
                error(l, c, f"file path '{file}' in rule '{rule_name}' does not exist.")
            if path_not_exists:
                return False
        return True

    def get_newest_file_timestamp(files: list[str]) -> int:
        # If there are no files...
        newest_timestamp: int = getctime(files[0])

        for file in files[1:]:
            newest_timestamp = max(newest_timestamp, getctime(file))
        return newest_timestamp

    
    assert build_files, "The parser should not allow 'build_files' to be None."
    assert output_files, "The parser should not allow 'output_files' to be None."

    # We don't check to see if watch_files or output_files exist
    # though as they are not required in the final shell command.
    files_exist_check(build_files)
    newest_build_time: int = get_newest_file_timestamp(build_files)

    # The user has declared at least `build_files` and `output_files`.
    # Therefor at this point, we do need to check whether the output
    # files exist.
    newest_output_time: int = 0 
    if files_exist_check(output_files, skip_error=True):
        newest_output_time = get_newest_file_timestamp(output_files)


    # If the user is watching a set of build files and any of them
    # is newer than the set of output files they are watching,
    # then we should trigger this rule.
    # This checks the opposite case. If the latest modified build
    # file is older than the latest modified output file, then do
    # not trigger this rule.
    if newest_build_time < newest_output_time:
        return (False, rule_name)

    eval_list(rule.exprs, rule.environment)
    rules_ran+=1
    return (True, rule_name)

def eval_shell(shell: Shell, local_env: dict[str, object]) ->  None:
    og_commands = shell.commands.text
    commands: list[str] = str(shell.commands.text)[1:].strip().split()

    # Check if the variable exists in the rule's scope.
    # if it doesn't, then return the string as is.
    # I'm guessing some people will want to run a command
    # like: `$ echo $?`.
    def resolve_variable(variable: str) -> str:
        if variable[0] != "$": return variable
        vars: list[str] = local_env.get(variable[1:], [])
        if vars == []: return variable

        # vars = trim_quotes(vars)
        return interpolate(' '.join(vars), local_env)


    commands = [ resolve_variable(var) for var in commands]
    print(f"$ {' '.join(commands)}")

    import os

    line: int = shell.commands.line
    return_code: int = os.system(' '.join(commands))
    if return_code != 0:
        print(f"\n[build-error: {line}] Exit Code {return_code}.") 
        exit(return_code)

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
    values: list[object] = eval_list(assign.values, local_env)
    local_env[assign.variable.token.text] = values
    return None

def eval_literal(literal: Literal) -> str:
    # NOTE(tyler): For right now, pretty much
    # everything is a string. Once more types
    # are supported, I will have to check the
    # type before trimming.
    return trim_quote(literal.token.text)

def error(line: int, col: int, message: str) -> None:
    print(f"[interpreter-error][{line}:{col}] {message}")
    exit(1)

if __name__ == "__main__":
    main()