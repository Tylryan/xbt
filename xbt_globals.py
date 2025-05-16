XBT_KEYWORDS = [
    "build_files",
    "output_files",
    "$^",
    "$@"
]

def is_keyword(x: str) -> bool:
    return x in XBT_KEYWORDS