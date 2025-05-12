from __future__ import annotations

from antlr4 import Token
from dataclasses import dataclass


class Expr:
    def as_dict(self) -> dict[str, object]:
        pass

@dataclass
class Shell(Expr):
    commands: Token

    def as_dict(self) -> dict[str, object]:
        return {"shell": self.commands.text}

@dataclass
class Comment(Expr):
    token: Token

    def as_dict(self) -> dict[str, object]:
        return { "comment": self.token.text }
    
@dataclass
class Rule(Expr):
    name: Variable
    exprs: list[Expr]
    environment: dict[str, object]

    def __init__(self, name: Variable, exprs: list[Expr]):
        self.name = name
        self.exprs = exprs
        self.environment = {}

    def as_dict(self) -> dict[str, object]:
        exprs: list[Expr] = []
        for expr in self.exprs:
            if expr:
                exprs.append(expr)
        return { 
            "rule": {
                "name": self.name.token.text if self.name else None,
                "exprs": [e.as_dict() for e in exprs]
            }
        }

@dataclass
class Variable(Expr):
    token: Token

    def as_dict(self) -> dict[str, object]:
        return { "variable": self.token.text }

@dataclass
class Assign(Expr):
    variable: Variable
    values: list[Expr]
    is_global: bool

    def __init__(self, variable: Variable, values: list[Expr], is_global: bool = False):
        self.variable = variable
        self.values = values
        self.is_global = is_global

    def as_dict(self) -> dict[str, object]:
        values: list[object] = []
        for val in self.values:
            values.append(val.as_dict())

        return { 
            "assign": {
                "variable": self.variable.token.text,
                "value"   : values
            }
        }


@dataclass
class Literal(Expr):
    token: Token

    def as_dict(self) -> dict[str, object]:
        return { "literal": {self.token.text } }


@dataclass
class BuildFiles(Expr):
    token: Token
    files: list[Expr]

    def as_dict(self) -> dict[str, object]:
        return { 
            "build-files": {
                    "files": [x.as_dict() for x in self.files]
                }
        }

@dataclass
class OutFiles(Expr):
    token: Token
    files: list[Expr]

    def as_dict(self) -> dict[str, object]:
        return { 
            "out-files": {
                    "files": [x.as_dict() for x in self.files]
                }
        }


@dataclass
class HelperFiles(Expr):
    token: Token
    files: list[Literal | Variable | MemberAccess]

    def as_dict(self) -> dict[str, object]:
        return { 
            "helper-files": {
                    "files": [x.as_dict() for x in self.files]
                }
        }

@dataclass
class HelperFile(Expr):
    file: str | Literal | Variable | MemberAccess

    def as_dict(self) -> dict[str, object]:
        assert isinstance(self.file, Literal | Variable | MemberAccess)
        return { 
            "helper-file": self.file.as_dict() 
        }

@dataclass
class MemberAccess(Expr):
    # Rule::member ;
    rule_name: Token
    member   : Token

    def as_dict(self) -> dict[str, object]:
        return { 
            "member-access": {
                    "rule-name"  : self.rule_name.text,
                    "member-name": self.member.text
                }
        }