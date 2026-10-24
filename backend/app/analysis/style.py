"""Style checks.

Checks:
- Naming conventions — snake_case for functions/variables, PascalCase for classes.
- Missing type hints — functions that give no type information.
- Unused imports — dead code that clutters your namespace.
- Dead code — statements after return/raise that never execute.
"""

import ast
import re
from typing import Iterable

from app.schemas.findings import Finding


def check_style(tree: ast.Module, source: str) -> list[Finding]:
    """Run all style-related checks."""
    findings: list[Finding] = []
    naming_check(tree, findings)
    missing_type_hints(tree, findings)
    unused_imports_check(tree, source, findings)
    dead_code_check(tree, findings)
    return findings


# ───────── Naming conventions ─────────

import re as _re

SNAKE_CASE = _re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL_CASE = _re.compile(r"^[A-Z][a-zA-Z0-9]*$")

# Magic names that don't follow the rules and never should.
MAGIC_NAMES = {
    "__init__", "__str__", "__repr__", "__eq__", "__hash__", "__lt__", "__le__",
    "__gt__", "__ge__", "__del__", "__new__", "__call__", "__len__", "__getitem__",
    "__setitem__", "__iter__", "__next__", "__enter__", "__exit__", "__await__",
    "__aenter__", "__aexit__", "__aiter__", "__anext__", "__main__",
}


def naming_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Verify PEP 8 naming conventions.

    - Functions and variables must be snake_case.
    - Classes must be PascalCase.
    """
    for node in ast.walk(tree):
        # ─── Function / method names ───
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if name not in MAGIC_NAMES and not SNAKE_CASE.match(name):
                findings.append(Finding(
                    id=f"nc-{node.lineno}-func",
                    category="style",
                    rule="naming_violation",
                    severity="info",
                    message=(
                        f"Function '{name}' is not snake_case. PEP 8 says "
                        f"functions should be lowercase_with_underscores."
                    ),
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    code_snippet=f"def {name}...",
                    suggestion="Rename to snake_case, e.g. `process_user_data`.",
                ))

        # ─── Class names ───
        if isinstance(node, ast.ClassDef):
            name = node.name
            if name not in MAGIC_NAMES and not PASCAL_CASE.match(name):
                findings.append(Finding(
                    id=f"nc-{node.lineno}-class",
                    category="style",
                    rule="naming_violation",
                    severity="info",
                    message=(
                        f"Class '{name}' is not PascalCase. PEP 8 says classes "
                        f"should use CapWords."
                    ),
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    code_snippet=f"class {name}:",
                    suggestion="Rename to PascalCase, e.g. `UserData`.",
                ))

        # ─── Variable / argument names ───
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if not SNAKE_CASE.match(name) and not MAGIC_NAMES.get(name):
                        findings.append(Finding(
                            id=f"nc-{node.lineno}-var",
                            category="style",
                            rule="naming_violation",
                            severity="info",
                            message=(
                                f"Variable '{name}' is not snake_case. PEP 8 says "
                                f"variables should be lowercase_with_underscores."
                            ),
                            line_start=node.lineno,
                            line_end=node.end_lineno,
                            code_snippet=source.splitlines()[node.lineno - 1].strip()[:70],
                            suggestion="Rename to snake_case, e.g. `user_count`.",
                        ))

        # ─── Lambda names are fine, skip. ───


# ───────── Missing type hints ─────────


def missing_type_hints(tree: ast.Module, findings: list[Finding]) -> None:
    """Flag functions with no type annotations at all.

    Type hints make code self-documenting and enable better tooling. We flag
    functions that have *no* annotations whatsoever — args without return, or
    return without args, is fine and counts as hinting.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        has_arg_hints = any(a.annotation is not None for a in node.args.args)
        has_return_hint = node.returns is not None

        if not has_arg_hints and not has_return_hint:
            findings.append(Finding(
                id=f"th-{node.lineno}",
                category="style",
                rule="missing_type_hints",
                severity="info",
                message=(
                    f"Function '{node.name}' has no type hints. Add annotations "
                    f"for your args and return value."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}...",
                suggestion="Add type hints: `def foo(x: int) -> str: ...`.",
            ))


# ───────── Unused imports ─────────


def unused_imports_check(tree: ast.Module, source: str, findings: list[Finding]) -> None:
    """Detect imported names that are never referenced in the file.

    Unused imports make the module harder to reason about and can slow imports.
    We collect all import targets and check they appear as identifier names
    elsewhere in the source.
    """
    imports: dict[str, int] = {}  # name -> lineno of import

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imports[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imports[name] = node.lineno

    # Build a set of all identifier names used in the body (excluding imports).
    used_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Name, ast.Attribute)):
            used_names.add(node.id)

    for name, lineno in sorted(imports.items(), key=lambda x: x[1]):
        if name not in used_names and not name.startswith("_"):
            line = source.splitlines()[lineno - 1].strip()[:80]
            findings.append(Finding(
                id=f"ui-{lineno}",
                category="style",
                rule="unused_import",
                severity="warning",
                message=(
                    f"Import '{line}' on line {lineno} is never used. Remove it."
                ),
                line_start=lineno,
                line_end=lineno,
                code_snippet=line,
                suggestion="Delete the unused import or use it.",
            ))


# ───────── Dead code ─────────


def dead_code_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Find statements that can never execute.

    A statement (or block) that comes after a `return`, `raise`, `break`, or
    `continue` within the same block will never run. This catches stale code.
    """
    for node in ast.walk(tree):
        # Only look at function/module-level blocks for simplicity.
        block = node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            block = node
            for i, stmt in enumerate(node.body):
                if _is_dead_statement(stmt):
                    snippet = source_code_from_line(stmt, block)
                    findings.append(Finding(
                        id=f"dc-{stmt.lineno}",
                        category="style",
                        rule="dead_code",
                        severity="warning",
                        message=(
                            f"Dead code on line {stmt.lineno}: this statement "
                            f"comes after a return/raise/break/continue."
                        ),
                        line_start=stmt.lineno,
                        line_end=stmt.end_lineno or stmt.lineno,
                        code_snippet=snippet,
                        suggestion="Remove the unreachable statement or move it before the return.",
                    ))


def _is_dead_statement(stmt: ast.stmt) -> bool:
    """Check if a statement is unreachable (after return/raise/break/continue)."""
    return isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue,
                             ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))


def source_code_from_line(node: ast.AST, block: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Get the source line for a node. Fallback to a generic snippet."""
    try:
        lines = block.body  # not source
        return f"    ...  # line {node.lineno}"
    except Exception:
        return f"    ...  # line {node.lineno}"
