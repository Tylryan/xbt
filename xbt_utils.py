

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
def interpolate(string: str, local_env: dict[str, object]) -> str:
    string_copy: str = trim_quote(string)

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
        new_vals: list[str] = local_env.get(var_name, var_name)
        for v in new_vals:
            string_copy = string_copy.replace(key, v)
    return string_copy