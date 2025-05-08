

def read_file(path: str) -> str:
    f = open(path)
    c = f.read()
    f.close()
    return c