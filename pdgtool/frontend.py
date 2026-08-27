"""Front end: read a source file, parse it, and reject anything outside the
accepted language subset from the Phase 1 specification.

Rejecting out-of-scope constructs early (with the line number) keeps the
analysis honest and gives a clean error instead of a confusing crash later.
"""

from __future__ import annotations

import ast


class SubsetError(Exception):
    """Raised when the source uses a construct outside the accepted subset."""


# AST node types that are explicitly out of scope, mapped to a human name.
_DISALLOWED: dict[type, str] = {
    ast.FunctionDef: "function definitions",
    ast.AsyncFunctionDef: "async function definitions",
    ast.ClassDef: "class definitions",
    ast.For: "for loops",
    ast.AsyncFor: "async for loops",
    ast.Break: "break",
    ast.Continue: "continue",
    ast.Return: "return",
    ast.Import: "imports",
    ast.ImportFrom: "imports",
    ast.Try: "try/except",
    ast.With: "with blocks",
    ast.AsyncWith: "async with blocks",
    ast.Lambda: "lambda expressions",
    ast.Global: "global declarations",
    ast.Nonlocal: "nonlocal declarations",
    ast.List: "list literals",
    ast.Dict: "dict literals",
    ast.Set: "set literals",
    ast.Tuple: "tuples",
    ast.ListComp: "comprehensions",
    ast.DictComp: "comprehensions",
    ast.SetComp: "comprehensions",
    ast.GeneratorExp: "generator expressions",
    ast.Subscript: "indexing / subscripting",
}


def parse_file(path: str) -> ast.Module:
    """Read and parse ``path`` into a Python AST module."""
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    try:
        return ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise SubsetError(f"{path}: could not parse: {exc}") from exc


def validate(tree: ast.Module, path: str = "<input>") -> None:
    """Walk the tree and raise SubsetError if any disallowed construct appears."""
    problems: list[str] = []
    for node in ast.walk(tree):
        for typ, name in _DISALLOWED.items():
            if isinstance(node, typ):
                line = getattr(node, "lineno", "?")
                problems.append(f"  line {line}: {name} are not in the accepted subset")
                break
    if problems:
        raise SubsetError(
            f"{path}: input uses constructs outside the accepted language subset:\n"
            + "\n".join(problems)
        )