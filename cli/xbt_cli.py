from __future__ import annotations

class Args:
    build_file: str
    entry_rule: str
    commands: list[str]

    def __init__(self):
        self.build_file = None
        self.entry_rule = None
        self.commands = []