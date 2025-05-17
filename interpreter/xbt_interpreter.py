from __future__ import annotations

from xbt_globals import *
from xbt_utils import *
from cli.xbt_cli import Args

from antlr4 import *
from xbt_utils import read_file, interpolate, flat_join, trim_quote, trim_quotes
from parser.exprs import *
from xbt_globals import *

from pprint import pprint
import sys
from sys import stdout

global global_env
global_env = {}
global rules_ran
rules_ran = 0
global dry_run
dry_run = False

def interpret(args: Args, exprs: list[Expr]) -> None:
    from pprint import pprint
    [pprint(x.as_dict()) for x in exprs ]

    global_exprs, rest = global_var_decs(exprs)

    for global_expr in global_exprs:
        evaluate(global_expr)


    commands, rest = cmd_decs(rest)

    # TODO(tyler): If command passed in command line in
    # commands, then execute command and skip below.
    # Eventually, the user will be able to pass multiple
    # commands. Do this for each.

    [print(x) for x in commands]


    if args.entry_rule:
        rest = keep_starting_at(args.entry_rule)


    if len(args.commands) > 0:
        global dry_run
        dry_run = True
        for expr in rest[::-1]:
            evaluate(expr, {})
        dry_run = False

        for cmd in args.commands:
            if run_cmd(cmd, commands) is False:
                error(0, 0, f"Unknown command passed in the command line: '{cmd}'")
    else:
        for expr in rest[::-1]:
            evaluate(expr, {})

    if not rules_ran:
        print("No rules ran. Nothing to do.")

def evaluate(expr: Expr, local_env: dict[str, object] = {}) -> object:
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
    if isinstance(expr, HelperFile): return eval_helper_file(expr, local_env)
    if isinstance(expr, HelperFiles): return eval_file_dec(expr, local_env)
    else: error(f"[interpreter-error] unimplemented expression: {expr}")

def eval_list(exprs: list[Expr], local_env: dict[str, object]) -> list[object]:
    values: list[object] = []
    for expr in exprs:
        values.append(evaluate(expr, local_env))
    return values

def eval_helper_file(expr: HelperFile, 
                      local_env: dict[str, object], 
                      keep=False) -> list[str]:
    err_msg = f"Unimplemented type in HelperFile: {expr.file}."
    assert isinstance(expr.file,  Literal | Variable | MemberAccess), err_msg

    # Only the shell would not want to keep the original
    # HelperFile.
    if not keep:
        return expr

    if isinstance(expr.file, Literal):
        return [HelperFile(eval_literal(expr.file))]
    if isinstance(expr.file, Variable):
        return [HelperFile(eval_variable(expr.file, local_env))]
    if isinstance(expr.file, MemberAccess):
        evaled_files = eval_member_access(expr.file, local_env)
        return [HelperFile(f) for f in evaled_files]

def eval_member_access(expr: MemberAccess, local_env: dict[str, object]) -> list[str]:
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


def eval_file_dec(expr: BuildFiles | OutFiles, 
                  local_env: dict[str, object]) ->  list[str | HelperFile]:
    # assert isinstance(expr, BuildFiles | OutFiles  | HelperFiles)

    files: list[str] = []
    for file in expr.files:
        if isinstance(file, Literal):
            res: str = eval_literal(file)
            files.append(res)
        elif isinstance(file, MemberAccess):
            res: list[str] = eval_member_access(file, local_env)
            files = files + res
        elif isinstance(file, Variable):
            res: list[str] = eval_variable(file, local_env)
            files = files + res
        elif isinstance(file, HelperFile):
            res: list[HelperFile] = eval_helper_file(file, 
                                                           local_env, True)
            files = files + res
        else:
            err_msg = f"Invalid expression in '{expr.token.text}' declaration.'"
            error(expr.token.line, expr.token.column,
                  err_msg)
    return files


def eval_rule(rule: Rule) ->  None:
    # Nested rules are not allowed as of, so 
    global global_env
    global rules_ran
    global dry_run
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
        if isinstance(e, BuildFiles | OutFiles | HelperFiles):
            key: str = e.token.text
            if key == "$^": key = BUILD_FILES
            if key == "$@": key = OUTPUT_FILES
            # At this point, the user has declared a keyword like
            # 'build_files'. If this evaluation returns an empty
            # list, then the user has forgotten to assign values.
            # This is a syntax error that should be caught by the
            # parser. But just in case, I'll assert it here.
            values: list[str | HelperFile] = eval_file_dec(e, 
                                                           rule.environment)
            assert values, f"The parser should not allow '{key}' to be none"
            rule.environment[key] = values if values else None





    # Immediately pull out the values for the keywords 
    # "build_files" and "output_files".
    build_files: list[str | HelperFile] | None = rule.environment.get(BUILD_FILES, [])
    output_files: list[str]| None = rule.environment.get(OUTPUT_FILES, [])

    shell_commands: list[Shell] = []
    for expr in rule.exprs:
        if isinstance(expr, Shell):
            shell_commands.append(expr)


    # String Interpolation:
    # Replace  potential variables in their values with
    # the expanded values those variables contain.
    if build_files:
        build_files = [interpolate(f, global_env, rule.environment) for f in build_files]
    if output_files:
        output_files = [interpolate(f, global_env, rule.environment) for f in output_files]

    import os
    from os.path import getctime

    # If dry run, then don't evaluate
    if dry_run:
        return (False, "idk")

    # If the user did not assign a value to one of these 
    # keyword variables then the rule should not do a time 
    # comparison and should simply run the shell scripts
    # every time.
    if build_files == [] or output_files == []:
        # NOTE: This is the point in the program where Shell/BuildFiles/etc
        # are evaluated.
        # TODO(tyler): This should ony evaluate Shell Commands right?
        if rule.is_command:
            [ evaluate(expr, global_env) for expr  in shell_commands]
        else:
            [ evaluate(expr, rule.environment) for expr  in shell_commands]
        # eval_list(rule.exprs, rule.environment)
        rules_ran+=1
        return (True, rule_name)

    # At this point, the user has declared the files they wish to
    # watch. If those files don't exist, we should let them know
    # about it.
    def files_exist_check(files: list[str | HelperFile], skip_error: bool = False) -> bool:
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

    [ evaluate(expr, rule.environment) for expr  in shell_commands]
    # eval_list(rule.exprs, rule.environment)
    rules_ran+=1
    return (True, rule_name)


def var_lookup(var_name: str, local_env: dict[str, object]) -> str | None:
    # Check the local environment first
    if var_name in local_env.keys():
        return local_env.get(var_name)

    # Then check the global. Return None
    # if no variable was found.
    return global_env.get(var_name, None)

def var_exists(var_name: str, local_env: dict[str,object]) -> Rule | None:
    global global_env
    return var_name in local_env.keys() or \
           var_name in global_env.keys()

def eval_shell(shell: Shell, local_env: dict[str, object]) ->  None:
    global global_env

    og_commands = shell.commands.text
    commands: list[str] = str(shell.commands.text)[1:].strip().split()


    # Check if the variable exists in the rule's scope.
    # if it doesn't, then return the string as is.
    # I'm guessing some people will want to run a command
    # like: `$ echo $?`.
    def resolve_variable(variable: str, lenv) -> str | None:
        og_var: str = variable
        # If key is in local, set that
        # Elif key is in global, set that
        # Else, return original string

        if not variable:
            return None

        var_name: str = variable
        # TODO: Make this more solid
        if var_name == "$^":
            var_name = BUILD_FILES
        elif var_name == "$@": 
            var_name = OUTPUT_FILES
        elif var_name[0] == "$": var_name = variable[1:]

        to_unpack: list[str] = var_name.split("::")

        potential_rule: str = ""
        p_member      : str = ""

        if len(to_unpack) == 2:
            potential_rule = to_unpack[0]
            p_member = to_unpack[1]

        thing: object = None
        if var_exists(potential_rule, lenv):
            thing = var_lookup(potential_rule, lenv)
        elif var_exists(var_name, lenv):
            thing = var_lookup(var_name, lenv)
        else:
            return None

        # If the thing in question is a rule,
        # then look up the p_member in that scope.
        if isinstance(thing, Rule):
            rule: Rule = thing
            without_dollar: str = p_member[1:]
            new_var = p_member if is_keyword(p_member) \
                else without_dollar
            return resolve_variable(new_var, 
                                    rule.environment)


        if isinstance(thing, list):
            no_helpers: list[str]  = []
            for file_path in thing:
                if isinstance(file_path, HelperFile):
                    pass
                else:
                    no_helpers.append(file_path)
            if no_helpers == []:
                return ""
            
            res = flat_join(" ", no_helpers)
            return interpolate(res,
                               global_env,
                               local_env)
        return None



    resolved_commands: list[str] = []
    for cmd in commands:
        resolved: str | None = resolve_variable(cmd, local_env)

        if isinstance(resolved, str):
            resolved_commands.append(resolved)
            continue

        resolved_commands.append(cmd)
        
        
    # commands = [ resolve_variable(var,local_env) for var in commands]
    # print(f"$ {' '.join(commands)}")
    print(f"$ {' '.join(resolved_commands)}")

    import os

    line: int = shell.commands.line
    return_code: int = os.system(' '.join(resolved_commands))
    if return_code != 0:
        print(f"\n[build-error: {line}] Exit Code {return_code}.") 
        sys.exit(return_code)

    return None

def eval_comment(comment: Comment) -> None:
    #print(f"COMMENT: ", comment.token.text)
    return None

def eval_variable(variable: Variable, local_env: dict[str, object]) -> object:
    variable_name = variable.token.text

    if is_alias(variable.token.text):
        variable_name = get_alias(variable_name)

    if variable_name in local_env.keys():
        return local_env[variable_name]

    if variable_name in global_env.keys():
        res = global_env[variable_name]
        return res
    
    error(variable.token.line, variable.token.column,
          f"undefined variable: {variable_name}")

def eval_assign(assign: Assign, local_env: dict[str, object]) -> None:
    global global_env


    variable: Token = assign.variable.token
    values: list[object] = eval_list(assign.values, local_env)

    if assign.is_global:
        global_env[variable.text] = values
    else:
        local_env[variable.text] = values
    return None

def eval_literal(literal: Literal) -> str:
    # NOTE(tyler): For right now, pretty much
    # everything is a string. Once more types
    # are supported, I will have to check the
    # type before trimming.
    return trim_quote(literal.token.text)

def error(line: int, col: int, message: str) -> None:
    print(f"[interpreter-error][{line}:{col}] {message}")
    sys.exit(1)


###     HELPERS 

def global_var_decs(exprs: list[Expr]) -> list[Assign]:
    global_decs: list[Assign] = []
    all_other: list[Expr] = []
    for expr in exprs:
        if isinstance(expr, Assign):
            if expr.is_global:
                global_decs.append(expr)
                continue
        all_other.append(expr)
            
    return (global_decs, all_other)

# TODO(tyler): extract commands
def cmd_decs(exprs: list[Expr]) -> tuple[list[Rule], list[Expr]]:
    commands: list[Rule] = []
    all_other: list[Expr] = []
    for expr in exprs:
        if isinstance(expr, Rule):
            if expr.is_command:
                commands.append(expr)
                continue
        all_other.append(expr)
            
    return (commands, all_other)

def run_cmd(cmd_name: str, commands: list[Rule]) -> bool:
    global global_env
    for command in commands:
        command_name = command.name.token.text
        if command_name == cmd_name:
            evaluate(command, global_env)
            return True
    return False

# If a user passes in a rule by name via the command
# line.
def keep_starting_at(rule_name: str) -> list[Expr]:
    to_eval: list[Expr] = []
    keep: bool = False
    # Remove rules
    for expr in rest:
        # If it's not even a rule, then append it
        if isinstance(expr, Rule) is False:
            to_eval.append(expr)
            continue
        # If it is a rule, check to see if it's
        # the rule we're looking for.
        crule_name: str = expr.name.token.text

        # If it is...
        if rule_name == crule_name:
            # Then start keeping subsequent rules.
            keep = True

        if keep:
            to_eval.append(expr)

    if keep == False:
        err_msg = f"Unknown rule passed from command line: '{rule_name}'"
        error(0,0, err_msg)

    return to_eval