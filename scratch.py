
def flat_join(delim: str, xs) -> str:
    new_string: str = ""

    for i, x in enumerate(xs):
        if i == 0:
            new_string+= f"{x}{delim}"
        elif isinstance(x, list):
            new_string += flat_join(delim, x)
        else:
            new_string += f"{delim}{x}"
    return new_string


print(flat_join(" ", ["file1.txt", ["dist/xbt"]]))