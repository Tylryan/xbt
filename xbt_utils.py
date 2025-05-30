from __future__ import annotations
from parser.exprs import HelperFile

def trim_quote(string: str) -> str:
    assert isinstance(string, str)
    return string[1:-1]
# TODO(tyler): Put this somewhere else
def trim_quotes(strings: list[str]) -> list[str]:
    assert isinstance(strings, list)
    return [trim_quote(s) for s in strings]

def read_file(path: str) -> str:
    f = open(path)
    c = f.read()
    f.close()
    return c

# Pretty terrible, but I'll fix later.
# The purpose of this function is to replace ${var} with the
# actual string it represents.
def interpolate(string: str | HelperFile,
                global_env: dict[str, object],
                local_env: dict[str, object]) -> str | None:

    if isinstance(string, HelperFile):
        # At this piont, contents should only 
        # be a string.
        # TODO(tyler): [1:-1] is a hot fix.
        string = string.file

    if not string:
        return None
    string_copy: str = str(string)

    i = 0

    matches: list[str] = []
    while i < len(string) -1:
        if string[i] == "$":
            i+=2
            if i >= len(string) -1:
                break

            text = ""
            while i < len(string) - 1:
                if string[i] == "}":
                    break
                text += string[i]
                i+=1
            matches.append(text)
        i+=1
    key_vals: list[tuple[str, str]] = [(f"${{{x}}}", x) for x in matches]

    for key_val in key_vals:
        key: str = key_val[0]
        var_name: str = key_val[1]

        new_vals: list[str] = []
        if var_name in local_env.keys():
            new_vals = local_env.get(var_name, var_name)
        elif var_name in global_env.keys():
            new_vals = global_env.get(var_name, var_name)
        for v in new_vals:
            string_copy = string_copy.replace(key, v)
    return string_copy