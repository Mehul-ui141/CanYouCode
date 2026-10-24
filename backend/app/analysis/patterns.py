"""Multi-language pattern checks for Python, Java, C, C++, JavaScript, and TypeScript.

Catches cross-cutting concerns, security risks, and language anti-patterns
via robust regular expressions tailored to each language syntax.
"""

import re
from dataclasses import dataclass
from app.schemas.findings import Finding


@dataclass
class _Pattern:
    compiled: re.Pattern
    rule: str
    severity: str
    message: str
    suggestion: str = ""
    languages: list[str] = None  # None = applies to all


UNIVERSAL_PATTERNS: list[_Pattern] = [
    _Pattern(
        compiled=re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG):\s", re.IGNORECASE),
        rule="todo_comment",
        severity="info",
        message="Unresolved TODO/FIXME comment.",
        suggestion="Resolve or update the comment before shipping.",
    ),
    _Pattern(
        compiled=re.compile(
            r'(?i)(?:api[_-]?key|api[_-]?secret|password|secret[_-]?key|token|access[_-]?token|private[_-]?key)\s*=\s*["\'][^"\']+["\']'
        ),
        rule="hardcoded_secret",
        severity="critical",
        message="Hardcoded secret detected in code.",
        suggestion="Move secrets to environment variables or a secure vault.",
    ),
]

PYTHON_PATTERNS: list[_Pattern] = [
    _Pattern(
        compiled=re.compile(r"\bprint\("),
        rule="debug_print",
        severity="info",
        message="Debug print() statement left in code.",
        suggestion="Remove print statements before committing.",
    ),
    _Pattern(
        compiled=re.compile(r"^import\s+\*$", re.MULTILINE),
        rule="wildcard_import",
        severity="warning",
        message="Wildcard import (`import *`) pollutes the module namespace.",
        suggestion="Import specific names instead.",
    ),
    _Pattern(
        compiled=re.compile(r"==\s*(True|False|None)\b|\b(True|False|None)\s*=="),
        rule="identity_comparison",
        severity="info",
        message="Use `is` for identity comparison with True/False/None.",
        suggestion="Replace `x == True` with `x is True`.",
    ),
    _Pattern(
        compiled=re.compile(r"\b(eval|exec)\s*\("),
        rule="eval_usage",
        severity="critical",
        message="eval()/exec() is used. Extremely dangerous with untrusted input.",
        suggestion="Avoid dynamic code execution entirely.",
    ),
]

C_CPP_PATTERNS: list[_Pattern] = [
    _Pattern(
        compiled=re.compile(r"\bstrcpy\s*\("),
        rule="unsafe_strcpy",
        severity="critical",
        message="`strcpy` is unsafe and leads to buffer overflows.",
        suggestion="Use `strncpy` or `snprintf` instead.",
    ),
    _Pattern(
        compiled=re.compile(r"\bsprintf\s*\("),
        rule="unsafe_sprintf",
        severity="critical",
        message="`sprintf` can cause buffer overflows if output exceeds buffer size.",
        suggestion="Use `snprintf` with explicit size limits.",
    ),
    _Pattern(
        compiled=re.compile(r"\bgets\s*\("),
        rule="unsafe_gets",
        severity="critical",
        message="`gets` is catastrophically insecure and deprecated.",
        suggestion="Use `fgets` with size checks.",
    ),
    _Pattern(
        compiled=re.compile(r"\bmalloc\s*\([^)]*\)\s*;\s*\n\s*(?!.*if\s*\([^)]+==\s*NULL\))"),
        rule="unchecked_malloc",
        severity="warning",
        message="Memory allocation (`malloc`) without checking for NULL return.",
        suggestion="Always check if returned pointer is NULL before using it.",
    ),
    _Pattern(
        compiled=re.compile(r"\bfree\s*\(\s*([a-zA-Z_]\w*)\s*\);\s*\n.*?\1\s*->"),
        rule="use_after_free",
        severity="critical",
        message="Potential use-after-free vulnerability.",
        suggestion="Set pointer to NULL immediately after calling free().",
    ),
]

JAVA_PATTERNS: list[_Pattern] = [
    _Pattern(
        compiled=re.compile(r"\bcatch\s*\(\s*Exception\s+[a-zA-Z_]\w*\s*\)"),
        rule="broad_exception_java",
        severity="warning",
        message="Catching broad `Exception` instead of specific exceptions.",
        suggestion="Catch precise exception types (e.g. `IOException`, `NullPointerException`).",
    ),
    _Pattern(
        compiled=re.compile(r"==\s*\"[^\"]*\"|\"[^\"]*\"\s*=="),
        rule="string_equality_java",
        severity="critical",
        message="Comparing Java strings with `==` checks reference equality, not content.",
        suggestion="Use `.equals()` to compare string values.",
    ),
    _Pattern(
        compiled=re.compile(r"\bSystem\.out\.print(ln)?\s*\("),
        rule="system_out_print",
        severity="info",
        message="Using `System.out.println` for logging in production code.",
        suggestion="Use a logging framework (SLF4J, Log4j) instead.",
    ),
]

JS_TS_PATTERNS: list[_Pattern] = [
    _Pattern(
        compiled=re.compile(r"\bvar\s+[a-zA-Z_]"),
        rule="var_keyword",
        severity="warning",
        message="Using `var` leads to function-scoping bugs and hoisting issues.",
        suggestion="Use `let` or `const` instead.",
    ),
    _Pattern(
        compiled=re.compile(r"\b==\s*(?!null|undefined)|(?!null|undefined)\s*==\b"),
        rule="loose_equality",
        severity="warning",
        message="Using loose equality (`==` or `!=`) instead of strict (`===` or `!==`).",
        suggestion="Use strict equality (`===` / `!==`) to avoid unexpected type coercion.",
    ),
    _Pattern(
        compiled=re.compile(r"\bconsole\.log\s*\("),
        rule="console_log",
        severity="info",
        message="`console.log` left in production code.",
        suggestion="Remove debug console logs before committing.",
    ),
    _Pattern(
        compiled=re.compile(r":\s*any\b"),
        rule="typescript_any",
        severity="info",
        message="Explicit use of `any` type defeats TypeScript type safety.",
        suggestion="Provide a specific interface or `unknown`.",
    ),
]


def run_pattern_checks(source: str, language: str) -> list[Finding]:
    """Run all applicable pattern checks for the given language."""
    findings: list[Finding] = []
    seen: set[tuple[str, int]] = set()

    # Collect relevant pattern sets
    patterns = list(UNIVERSAL_PATTERNS)
    if language == "python":
        patterns.extend(PYTHON_PATTERNS)
    elif language in ("c", "cpp"):
        patterns.extend(C_CPP_PATTERNS)
    elif language == "java":
        patterns.extend(JAVA_PATTERNS)
    elif language in ("javascript", "typescript"):
        patterns.extend(JS_TS_PATTERNS)
        if language == "typescript":
            pass  # TS patterns already included

    for pat in patterns:
        for m in pat.compiled.finditer(source):
            line = source[: m.start()].count("\n") + 1
            key = (pat.rule, line)
            if key in seen:
                continue
            seen.add(key)

            snippet = source.splitlines()[line - 1].strip()[:90] if line <= len(source.splitlines()) else ""
            findings.append(Finding(
                id=f"pat-{key[0]}-{line}",
                category="bug" if pat.severity == "critical" else "style",
                rule=pat.rule,
                severity=pat.severity,
                message=pat.message,
                line_start=line,
                line_end=line,
                code_snippet=snippet,
                suggestion=pat.suggestion or "Review and fix the issue.",
            ))

    return findings
