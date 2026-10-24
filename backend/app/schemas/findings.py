"""Schemas for static-analysis findings.

These are the structured, machine-readable output of the analysis engine.
Every finding flows through here before the AI personality layer rewrites it
in a character's voice.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ───────── Severity hierarchy ─────────
# Severity drives the UI's color coding and also hints the AI at how hard to
# react. We keep the set small so the model's reactions stay consistent.
Severity = Literal["critical", "warning", "info", "nitpick"]


class Finding(BaseModel):
    """A single code issue discovered by the static analysis engine.

    Attributes:
        id: Unique identifier within the review (f-001, f-002, ...).
        category: Broad bucket — complexity, smell, bug, or style.
        rule: Machine-readable rule name for testing and metrics.
        severity: How bad it is, per the Severity enum above.
        message: Human-readable description of the issue.
        line_start/line_end: Where it occurs (1-based), if determinable.
        code_snippet: The offending line(s) so the UI can quote it.
        suggestion: A concrete fix suggestion from the engine (pre-AI).
    """

    id: str
    category: Literal["complexity", "smell", "bug", "style"] = Field(
        ..., description="Category bucket for the finding"
    )
    rule: str = Field(
        ..., description="Machine-readable rule identifier"
    )
    severity: Severity = Field(..., description="How severe this issue is")
    message: str = Field(..., description="Human-readable description of the issue")
    line_start: Optional[int] = Field(None, description="Start line (1-based)")
    line_end: Optional[int] = Field(None, description="End line (1-based)")
    code_snippet: Optional[str] = Field(
        None, description="The offending code fragment"
    )
    suggestion: Optional[str] = Field(
        None, description="Concrete fix suggestion from the engine"
    )

    class Config:
        json_schema_extra = {"example": {"id": "f-001", "category": "bug", "rule": "hardcoded_secret", "severity": "critical", "message": "Hardcoded secret detected", "line_start": 5, "code_snippet": "password = \"secret123\"", "suggestion": "Move secrets to environment variables"}}


class AnalysisResult(BaseModel):
    """The complete result of one analysis run.

    Attributes:
        findings: Sorted, deduplicated list of all findings.
        stats: Count of findings by severity for the summary tile.
        analysis_time_ms: How long the engine took (usually <100ms).
        input_stats: Total lines of code analyzed, for the "big function" check.
    """

    findings: list[Finding] = Field(default_factory=list)
    stats: dict[str, int] = Field(
        default_factory=lambda: {"critical": 0, "warning": 0, "info": 0, "nitpick": 0}
    )
    analysis_time_ms: float = Field(default=0.0, description="Analysis duration in milliseconds")
    input_stats: dict = Field(
        default_factory=dict,
        description="Stats about the input: total_lines, etc.",
    )
