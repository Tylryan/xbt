from __future__ import annotations
import sys

class Args:
    build_file: str
    entry_rule: str
    commands: list[str]

    def __init__(self):
        self.build_file = None
        self.entry_rule = None
        self.commands = []

def cli():
    args = Args()
    if len(sys.argv) == 1:
        args.build_file = "build.xbt"

    # NOTE(tyler): Assuming the user passes args correctly.
    elif sys.argv[1] == "-f":
        args.build_file = sys.argv[2]

    elif sys.argv[1] == "-r":
        args.build_file = "build.xbt"
        args.entry_rule = sys.argv[2]
    else:
        args.build_file = "build.xbt"
        args.commands = sys.argv[1:]
    return args