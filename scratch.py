import re


env = {
    "name": "John",
    "punc": "!"
}

# Pretty terrible, but I'll fix later.
def interpolate(string: str, local_env: dict[str, object]) -> str:
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
        new_val: str = local_env.get(var_name, var_name)


        string_copy = string_copy.replace(key, new_val)
    return string_copy



print(interpolate("hello world", env))