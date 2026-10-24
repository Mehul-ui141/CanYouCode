"""Multi-language static analysis orchestrator.

Supports Python, Java, C, C++, JavaScript, and TypeScript using a combination
of AST parsing (for Python) and robust language-aware regex pattern matching
for compiled and dynamic languages where full compilation isn't available.
"""

import ast
import time
from typing import Any

from app.schemas.findings import AnalysisResult, Finding

from .bugs import check_bugs
from .complexity import check_complexity
from .patterns import run_pattern_checks
from .smells import check_smells
from .style import check_style


def analyze(code: str, language: str = "python", input_mode: str = "raw") -> AnalysisResult:
    """Analyze a code snippet in any supported language and return findings.

    Args:
        code: Source code or diff.
        language: "python", "java", "c", "cpp", "javascript", or "typescript".
        input_mode: "raw" or "diff".

    Returns:
        AnalysisResult with findings sorted by line number.
    """
    start = time.perf_counter()

    if input_mode == "diff":
        normalized = _normalize_diff(code)
        input_stats = {"total_lines": len(normalized.splitlines()), "language": language}
    else:
        normalized = code
        input_stats = {"total_lines": len(code.splitlines()), "language": language}

    findings: list[Finding] = []

    # 1. Python AST-based checks
    if language == "python":
        try:
            tree = ast.parse(normalized)
            findings.extend(check_complexity(tree))
            findings.extend(check_smells(tree, normalized))
            findings.extend(check_bugs(tree, normalized))
            findings.extend(check_style(tree, normalized))
        except SyntaxError as e:
            findings.append(Finding(
                id="f-synerr",
                category="bug",
                rule="syntax_error",
                severity="critical",
                message=f"Python Syntax Error: {e.msg}",
                line_start=e.lineno,
                code_snippet=e.text.rstrip() if e.text else None,
                suggestion="Fix the syntax error before running deeper analysis.",
            ))

    # 2. Universal & language-specific pattern checks (covers C, C++, Java, JS, TS, Python)
    findings.extend(run_pattern_checks(normalized, language))

    findings = _deduplicate(findings)
    findings = _sort_by_line(findings)
    findings = _assign_ids(findings)
    stats = _compute_stats(findings)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return AnalysisResult(
        findings=findings,
        stats=stats,
        analysis_time_ms=round(elapsed_ms, 2),
        input_stats=input_stats,
    )


def _normalize_diff(diff_text: str) -> str:
    lines = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
    return "\n".join(lines)


def _deduplicate(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple] = set()
    deduped = []
    for f in findings:
        key = (f.rule, f.line_start, f.code_snippet)
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    return deduped


def _sort_by_line(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (f.line_start or 0, f.line_end or 0, f.rule))


def _assign_ids(findings: list[Finding]) -> list[Finding]:
    for i, f in enumerate(findings, start=1):
        f.id = f"f-{i:03d}"
    return findings


def _compute_stats(findings: list[Finding]) -> dict[str, int]:
    stats = {"critical": 0, "warning": 0, "info": 0, "nitpick": 0}
    for f in findings:
        stats[f.severity] = stats.get(f.severity, 0) + 1
    return stats
