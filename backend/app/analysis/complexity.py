"""Complexity-based checks using Python's AST.

Checks:
- Cyclomatic complexity (McCabe) — too many branches per function.
- Nesting depth — code buried in if/for/while is hard to follow.
- Function length — giant functions that do too much.
"""

import ast
from typing import Any

from app.schemas.findings import Finding, Severity


def check_complexity(tree: ast.Module) -> list[Finding]:
    """Run all complexity checks on a parsed Python AST.

    Cyclomatic complexity counts decision points (if, for, while, except,
    boolean operators, asserts). A function with complexity > 10 is a warning,
    > 20 is critical — the code is getting hard to reason about.
    """
    findings: list[Finding] = []
    complexity_check(tree, findings)
    nesting_check(tree, findings)
    length_check(tree, findings)
    return findings


def _add(finding: Finding, findings: list[Finding]) -> None:
    """Append a finding and bump the severity tracker."""
    findings.append(finding)


# ───────── Cyclomatic complexity ─────────


def complexity_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Report functions whose cyclomatic complexity exceeds thresholds.

    McCabe complexity = 1 + (number of decision points). We count If, For,
    While, ExceptHandler, and each element of BoolOp (and/or), plus Assert.
    (match/case on Python 3.10+ is also a decision point, but it's rare in
    typical codebases; we keep the formula simple and honest.)
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        complexity = _compute_complexity(node)
        if complexity > 20:
            sev: Severity = "critical"
            threshold_desc = "> 20"
        elif complexity > 10:
            sev = "warning"
            threshold_desc = "> 10"
        else:
            continue  # normal function, no finding

        _add(
            Finding(
                id=f"cc-{node.lineno}",
                category="complexity",
                rule="high_cyclomatic_complexity",
                severity=sev,
                message=(
                    f"Function '{node.name}' has cyclomatic complexity of {complexity} "
                    f"(over {threshold_desc}). Too many branches make it hard to test and follow."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}...",
                suggestion=(
                    "Split it into smaller functions. A good target is complexity <= 10 per function."
                ),
            )
        )


def _compute_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Count decision points inside a function body.

    Base complexity is 1 (the function itself). Every branch adds to it.
    """
    count = 1

    for child in ast.walk(node):
        # Each `if`, `for`, `while`, and `except` handler is one decision point.
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            count += 1
        # `and`/`or` each add a decision point — but guard for the right type.
        elif isinstance(child, ast.BoolOp):
            count += len(child.values) - 1
        # Asserts are explicit decisions about program state.
        elif isinstance(child, ast.Assert):
            count += 1

    return count


# ───────── Nesting depth ─────────


def nesting_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Report functions with excessive nesting depth.

    Nesting deeper than 4 levels is hard to read; deeper than 6 is a smell
    that usually means the code needs restructuring. We look at the max
    depth of if/for/while/with/try blocks inside each function.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        max_depth = _max_nesting_depth(node)
        if max_depth <= 4:
            continue

        sev = "critical" if max_depth > 6 else "warning"
        _add(
            Finding(
                id=f"nd-{node.lineno}",
                category="complexity",
                rule="deep_nesting",
                severity=sev,
                message=(
                    f"Function '{node.name}' nests {max_depth} levels deep "
                    f"(over 4). Pyramid code is hard to read."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}...",
                suggestion=(
                    "Use early returns or extract nested blocks into helper functions."
                ),
            )
        )


def _max_nesting_depth(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Return the deepest chain of decision/control blocks in the function."""
    # Walk the body, but treat each block statement as a nesting layer.
    stack = [0]
    max_depth = 0

    def _visit(n: ast.AST, depth: int) -> None:
        nonlocal max_depth
        if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            new_depth = depth + 1
            max_depth = max(max_depth, new_depth)
            for child in ast.iter_child_nodes(n):
                _visit(child, new_depth)
        elif isinstance(n, ast.stmt):
            # Statements don't add nesting but contain bodies we must inspect.
            for child in ast.iter_child_nodes(n):
                _visit(child, depth)
        else:
            for child in ast.iter_child_nodes(n):
                _visit(child, depth)

    # Start one level below the function definition itself.
    for child in node.body:
        _visit(child, 0)

    return max_depth


# ───────── Function length ─────────


def length_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Report functions that are suspiciously long.

    > 50 lines is a warning, > 100 is critical. This is a crude but useful
    heuristic — very long functions usually do too much and deserve a split.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        length = node.end_lineno - node.lineno + 1
        if length <= 50:
            continue

        sev = "critical" if length > 100 else "warning"
        _add(
            Finding(
                id=f"fl-{node.lineno}",
                category="complexity",
                rule="long_function",
                severity=sev,
                message=(
                    f"Function '{node.name}' is {length} lines long "
                    f"(over 50). Consider breaking it into smaller functions."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}(...){' ' * max(0, 40 - len(node.name))}# {length} lines",
                suggestion=(
                    "Split into focused helper functions, each doing one thing."
                ),
            )
        )
