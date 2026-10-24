"""Request/response schemas for the review flow.

The review flow is deliberately two-phase:
1. POST /review — submits code and returns an SSE stream (findings immediately,
   then AI commentary streaming, then a final review id/share url).
2. GET /review/{id} — fetches a saved review in one tidy JSON object.
"""

import datetime
from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["python", "java", "c", "cpp", "javascript", "typescript"]


class ReviewRequest(BaseModel):
    """What the frontend sends when you paste code and pick a personality.

    Attributes:
        code: The pasted code or git-style diff.
        input_mode: "raw" for plain code, "diff" for a patch to analyze.
        language: Language hint.
        personality_id: One of the 12 personality keys.
    """

    code: str = Field(..., description="The pasted code or diff")
    input_mode: Literal["raw", "diff"] = Field("raw", description="Whether input is raw code or a diff")
    language: Language = Field("python", description="Language of the input")
    personality_id: str = Field(..., description="Which personality should review this")


class FindingOut(BaseModel):
    """Finding as returned in review responses (lighter version)."""

    id: str
    category: str
    rule: str
    severity: str
    message: str
    line_start: int | None
    line_end: int | None
    code_snippet: str | None
    suggestion: str | None


class ReviewResponse(BaseModel):
    """Full review payload for GET endpoints and the final SSE event.

    This is what the ReviewPage renders from a saved review, and what gets
    shared when someone clicks Share.
    """

    id: str
    personality_id: str
    input_mode: str
    language: str
    findings: list[FindingOut]
    ai_review: str  # Full text review written by the personality
    opening: str
    closing: str
    overall_grade: str
    summary_stats: dict[str, int]
    share_url: str
    created_at: datetime.datetime


class ReviewListItem(BaseModel):
    """Compact review for the history list (avoids shipping the whole code)."""

    id: str
    personality_id: str
    language: str
    summary_stats: dict[str, int]
    created_at: datetime.datetime
    code_preview: str  # First ~80 chars, to show what you reviewed

    class Config:
        from_attributes = True
