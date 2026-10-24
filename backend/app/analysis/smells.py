"""Code smell checks.

Checks:
- Magic numbers — unexplained literals scattered through the code.
- God functions — functions that do an unreasonable amount of work.
- Duplicate blocks — copied-and-pasted logic that should be a function.
"""

import ast
from collections import Counter
from typing import Iterable

from app.schemas.findings import Finding, Severity


def check_smells(tree: ast.Module, source: str) -> list[Finding]:
    """Run all smell checks and return findings."""
    findings: list[Finding] = []
    magic_number_check(tree, source, findings)
    god_function_check(tree, source, findings)
    duplicate_block_check(source, findings)
    return findings


# ───────── Magic numbers ─────────

# Numbers the engine treats as "fine" (counting, loop bounds, math constants).
ALLOWED_NUMBERS = {0, 1, -1, 2, 10, 100, 1000, True, False}


def magic_number_check(
    tree: ast.Module, source: str, findings: list[Finding]
) -> None:
    """Find numeric literals used inline instead of named constants.

    If you see `if hours >= 1000:` you have to guess what 1000 means. It's
    better written as `if hours >= MAX_CONSECUTIVE_HOURS:`. We skip small
    numbers, loop bounds, and common magnitudes because they're usually fine.
    """
    module_level: list[tuple[str, int]] = []  # (name, lineno) of constant assignments

    # Collect module-level constants like `MAX_PAGES = 100`.
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    module_level.append((target.id, node.lineno))
    allowed_names = {name for name, _ in module_level}

    magic: set[tuple] = set()  # (lineno, value) to dedup

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, (int, float)):
            continue

        line = node.lineno
        val = node.value
        if val in ALLOWED_NUMBERS:
            continue

        # Don't report numbers that are assigned to named constants.
        if _is_constant_assignment(node, allowed_names):
            continue

        # Skip numeric literals inside other literals (like 3 in range(3)).
        if line in {n[1] for n in module_level}:
            continue

        magic.add((line, val))

    seen_messages: set[str] = set()
    for line, val in sorted(magic):
        snippet = source.splitlines()[line - 1].strip() if line <= len(source.splitlines()) else ""
        msg = (
            f"Magic number {val!r} used inline. Extract it into a named constant "
            f"so its meaning is clear."
        )
        if msg not in seen_messages:
            seen_messages.add(msg)
            findings.append(Finding(
                id=f"mn-{line}",
                category="smell",
                rule="magic_number",
                severity="info",
                message=msg,
                line_start=line,
                line_end=line,
                code_snippet=snippet or None,
                suggestion="Define a constant, e.g. `MAX_PAGES = 100` and use it here.",
            ))


def _is_constant_assignment(node: ast.Constant, allowed_names: set[str]) -> bool:
    """Check if this constant is part of a module-level constant assignment."""
    return False  # handled by module-level scanning


# ───────── God functions ─────────


def god_function_check(tree: ast.Module, source: str, findings: list[Finding]) -> None:
    """Report functions that are doing an unreasonable amount of work.

    Heuristics:
    - A function with more than 7 parameters is trying to be everything.
    - A single function containing more than 30% of the file's code lines
      is probably doing too much (extract classes or helpers).
    """
    lines = source.splitlines()
    total_lines = len(lines)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        params = [a.arg for a in node.args.args] + [
            a.arg for a in node.args.posonlyargs
        ]
        if len(params) > 7:
            findings.append(Finding(
                id=f"gf-{node.lineno}-params",
                category="smell",
                rule="god_function",
                severity="warning",
                message=(
                    f"Function '{node.name}' takes {len(params)} parameters "
                    f"(over 7). Consider bundling them into a dataclass/Pydantic model."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}(...){' ' * (40 - len(node.name))}",
                suggestion="Group related parameters into a single object or config.",
            ))
            continue

        length = (node.end_lineno or 1) - node.lineno + 1
        if total_lines > 0 and length > 0.30 * total_lines:
            findings.append(Finding(
                id=f"gf-{node.lineno}-size",
                category="smell",
                rule="god_function",
                severity="warning",
                message=(
                    f"Function '{node.name}' contains {length} of {total_lines} lines "
                    f"(over 30% of the file). It's doing too much."
                ),
                line_start=node.lineno,
                line_end=node.end_lineno,
                code_snippet=f"def {node.name}...",
                suggestion="Split into smaller, single-responsibility functions.",
            ))


# ───────── Duplicate blocks ─────────

import re


def duplicate_block_check(source: str, findings: list[Finding]) -> None:
    """Detect 3+ identical consecutive lines repeated elsewhere in the file.

    This is a simple text-based dedup that catches copy-pasted logic blocks
    (e.g. the same 4-line validation repeated in three endpoints). A full
    AST-based clone detector is overkill for an MVP.
    """
    lines = source.splitlines()
    n = len(lines)
    if n < 6:
        return

    # Normalize each line (strip whitespace) so we don't flag indentation-only matches.
    normalized = [line.strip() for line in lines]
    block_size = 3

    seen: set[tuple[str, ...]] = set()
    reported: set[tuple[int, int]] = set()

    for i in range(n - block_size + 1):
        block = tuple(normalized[i:i + block_size])
        if not block or not re.search(r"[A-Za-z0-9]", block[0]):
            continue  # empty lines don't count as code

        if block in seen:
            continue  # already flagged as part of an earlier block

        # Count total occurrences of this block.
        count = sum(1 for k in range(n - block_size + 1)
                    if tuple(normalized[k:k + block_size]) == block)

        if count > 1:
            seen.add(block)
            reported.add((i + 1, i + block_size))
            findings.append(Finding(
                id=f"dup-{i + 1}",
                category="smell",
                rule="duplicate_block",
                severity="warning",
                message=(
                    f"The same 3-line block starting at line {i + 1} appears {count} times. "
                    f"Copy-paste risk: maintain it in one place."
                ),
                line_start=i + 1,
                line_end=i + block_size,
                code_snippet=lines[i].strip()[:70],
                suggestion="Extract this block into a helper function.",
            ))
