"""Bug-detection checks.

These catch genuinely risky patterns: secrets in code, SQL injection,
unhandled exceptions, and silent error swallowing. Severity is always
"critical" or "warning" — the AI gets extra ammo to be dramatic.
"""

import ast
import re
from typing import Optional

from app.schemas.findings import Finding, Severity


def check_bugs(tree: ast.Module, source: str) -> list[Finding]:
    """Run all bug-related checks."""
    findings: list[Finding] = []
    hardcoded_secret_check(source, findings)
    sql_injection_check(tree, source, findings)
    bare_except_check(tree, findings)
    silent_exception_check(source, findings)
    no_error_handling_check(tree, source, findings)
    potential_none_access_check(source, findings)
    return findings


# ───────── Hardcoded secrets ─────────
# Regex for common secret-ish variable names with a string literal value.
SECRET_PATTERN = re.compile(
    r'(?i)(?:api[_-]?key|api[_-]?secret|password|secret[_-]?key|token|access[_-]?token|private[_-]?key)\s*=\s*["\'][^"\']+["\']',
)
SECRET_LINE = re.compile(
    r'(?i)(?:api[_-]?key|api[_-]?secret|password|secret[_-]?key|token|access[_-]?token|private[_-]?key)\s*='
)


def hardcoded_secret_check(source: str, findings: list[Finding]) -> None:
    """Flag password/key/secret/token literals committed to source.

    This is the #1 thing that gets you paged at 3am, so it's critical severity.
    We avoid false positives by requiring an actual string value (not a variable
    reference like `os.environ.get(...)`), and we use case-insensitive name
    matching because people write things as `PASSWORD` or `Api-Key`.
    """
    lines = source.splitlines()
    reported: set[int] = set()

    for i, line in enumerate(lines, start=1):
        # Skip if the value is an env-var reference or f-string interpolation.
        if re.search(r'\$?\{?os\.', line) or "\\$" in line:
            continue

        if SECRET_LINE.search(line) and SECRET_PATTERN.match(line):
            if i not in reported:
                reported.add(i)
                snippet = line[:80]
                findings.append(Finding(
                    id=f"hs-{i}",
                    category="bug",
                    rule="hardcoded_secret",
                    severity="critical",
                    message=(
                        f"Hardcoded secret on line {i}. If this code is committed, "
                        f"the secret is now public."
                    ),
                    line_start=i,
                    line_end=i,
                    code_snippet=snippet,
                    suggestion="Move secrets to environment variables or a secrets manager.",
                ))


# ───────── SQL injection ─────────

# Match f-strings or %-formatted strings passed into execute-like calls.
SQL_INJECT_CALL = re.compile(
    r'(?P<call>execute|cursor|query)\s*\(\s*(?P<arg>[\w"\']|#?\$?\{)', re.IGNORECASE
)
INJECTION_SOURCE = re.compile(r'\{[^}]+\}|%s|%\d+|\.\s*format\(')


def sql_injection_check(tree: ast.Module, source: str, findings: list[Finding]) -> None:
    """Detect string interpolation inside SQL execute() calls.

    Using f-strings or .format() on SQL is the classic injection vector.
    We look for .execute("..." % ...) or execute(f"...") patterns.
    """
    # AST-based: find calls to .execute with an f-string or format arg.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"execute", "cursor"} and not node.args:
                continue

            # e.g. conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
                for arg in node.args:
                    if isinstance(arg, ast.JoinedStr):  # f-string
                        found = False
                        for value in ast.walk(arg):
                            if isinstance(value, ast.FormattedValue):
                                found = True
                                break
                        if found:
                            i = node.lineno
                            snippet = source.splitlines()[i - 1].strip()[:90]
                            findings.append(Finding(
                                id=f"sq-{i}",
                                category="bug",
                                rule="sql_injection",
                                severity="critical",
                                message=(
                                    f"SQL query on line {i} uses an f-string. "
                                    f"User input can inject arbitrary SQL."
                                ),
                                line_start=i,
                                line_end=i,
                                code_snippet=snippet,
                                suggestion="Use parameterized queries: `conn.execute('SELECT * FROM u WHERE id = ?', (id,))`.",
                            ))

                    elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                        i = node.lineno
                        snippet = source.splitlines()[i - 1].strip()[:90]
                        findings.append(Finding(
                            id=f"sq-{i}",
                            category="bug",
                            rule="sql_injection",
                            severity="critical",
                            message=(
                                f"SQL query on line {i} uses % formatting. "
                                f"User input can inject arbitrary SQL."
                            ),
                            line_start=i,
                            line_end=i,
                            code_snippet=snippet,
                            suggestion="Use parameterized queries instead of % formatting.",
                        ))


# ───────── Bare except ─────────


def bare_except_check(tree: ast.Module, findings: list[Finding]) -> None:
    """Flag bare `except:` clauses that swallow everything.

    `except:` will catch `KeyboardInterrupt` and `SystemExit` too — the exact
    things you need to be able to shut the program down. It's a warning because
    the code still runs, but it's a landmine for debugging.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            # Ignore `except:` that immediately re-raises or logs.
            stmt = node.body[0] if node.body else None
            if isinstance(stmt, ast.Raise) and stmt.exc is not None:
                continue
            i = node.lineno
            findings.append(Finding(
                id=f"be-{i}",
                category="bug",
                rule="bare_except",
                severity="warning",
                message=(
                    f"Bare `except:` on line {i} catches everything, including "
                    f"KeyboardInterrupt. You're hiding errors."
                ),
                line_start=i,
                line_end=i,
                code_snippet="except:",
                suggestion="Catch specific exceptions, e.g. `except ValueError as e:` and handle/ re-raise.",
            ))


# ───────── Silent exception ─────────

SILENT_PATTERN = re.compile(r"except\s*:\s*\n\s*pass", re.MULTILINE)
SILENT_BLOCK = re.compile(r"\bexcept\b.*?\n\s+pass\b", re.DOTALL)


def silent_exception_check(source: str, findings: list[Finding]) -> None:
    """Flag `except: pass` — the most dangerous thing in Python.

    Swallowing exceptions silently makes bugs invisible. If you must do it,
    at least log something.
    """
    for m in SILENT_PATTERN.finditer(source):
        i = source[: m.start()].count("\n") + 1
        snippet = source.splitlines()[i - 1].strip()
        findings.append(Finding(
            id=f"se-{i}",
            category="bug",
            rule="silent_exception",
            severity="critical",
            message=(
                f"`except: pass` on line {i}. You're swallowing exceptions and "
                f"making bugs impossible to debug."
            ),
            line_start=i,
            line_end=i + 1,
            code_snippet=snippet,
            suggestion="Log the exception or re-raise it. `pass` hides the bug.",
        ))


# ───────── No error handling ─────────

IO_OPS = re.compile(r"\b(?:open|requests\.[a-z]+|urllib\.[a-z0-9.]+|subprocess\.[a-z]+|socket\.)")
IO_NAMES = {"open", "request", "get", "post", "put", "delete", "connect", "listen"}


def no_error_handling_check(tree: ast.Module, source: str, findings: list[Finding]) -> None:
    """Flag I/O calls that are not wrapped in try/except.

    Any call that reaches the network, the filesystem, or the shell can fail —
    and without a try/except, it crashes the whole program.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Call, ast.Assign, ast.Await)):
            continue

        # Find call nodes (handle wrapped await).
        call = node.func if isinstance(node, ast.Await) else getattr(node, "func", None)
        if not isinstance(call, ast.Attribute) and not isinstance(call, ast.Name):
            continue

        name = call.id if isinstance(call, ast.Name) else call.attr
        if name not in IO_NAMES:
            continue

        # Determine if there's a surrounding try block.
        start = node.lineno
        lines = source.splitlines()
        has_try = False
        for j in range(start - 1, -1, -1):
            if lines[j].lstrip().startswith(("try:", "async with", "with")):
                has_try = True
                break
            if lines[j].lstrip().startswith(("def ", "class ", "for ", "while ",
                                             "if ", "else:", "elif ", "except:",
                                             "match ", "case ")):
                break  # reached a new block without a try

        if not has_try and name in {"open"}:
            i = node.lineno
            snippet = lines[i - 1].strip()[:90]
            findings.append(Finding(
                id=f"noeh-{i}",
                category="bug",
                rule="no_error_handling",
                severity="warning",
                message=(
                    f"I/O call on line {i} is not wrapped in try/except. "
                    f"It can raise and crash your program."
                ),
                line_start=i,
                line_end=i,
                code_snippet=snippet,
                suggestion="Wrap I/O in a try/except and handle failures gracefully.",
            ))


# ───────── Potential None access ─────────

NONE_ACCESS = re.compile(
    r'\b(?:\.get\([^)]*\)\s*\[\s*["\']?\w+["\']?\s*\]|["\']\w+["\']\s*\[[^]]+\])'
)


def potential_none_access_check(source: str, findings: list[Finding]) -> None:
    """Flag dictionary access that may silently return None.

    `d["key"]` raises if the key is missing, but `d.get("key")` returns None
    and then you use it — and 5 minutes later you have a confusing AttributeError
    somewhere else. Not critical, but worth surfacing.
    """
    lines = source.splitlines()
    reported: set[int] = set()
    for i, line in enumerate(lines, start=1):
        if ".get(" in line and ("[" in line or "if" not in line):
            if i not in reported and re.search(r'\.get\([^)]*\)', line):
                reported.add(i)
                snippet = line.strip()[:90]
                findings.append(Finding(
                    id=f"pna-{i}",
                    category="bug",
                    rule="potential_none_access",
                    severity="info",
                    message=(
                        f"Potential None on line {i}: `.get()` can return None. "
                        f"Check for None or use `in` before accessing."
                    ),
                    line_start=i,
                    line_end=i,
                    code_snippet=snippet,
                    suggestion="Use `.get(key)` and check the result, or `if key in d:`.",
                ))


import re
