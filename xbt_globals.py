XBT_KEYWORDS = [
    "build_files",
    "output_files",
    "$^",
    "$@"
]

XBT_ALIASES = {
    "$@": "output_files",
    "$^": "build_files"
}

def is_alias(x: str) -> bool:
    return x in XBT_ALIASES

def get_alias(x: str) -> str:
    assert is_alias(x)
    return XBT_ALIASES[x]

def is_keyword(x: str) -> bool:
    return x in XBT_KEYWORDS