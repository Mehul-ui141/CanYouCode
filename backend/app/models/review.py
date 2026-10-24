"""ORM model for storing reviewed code.

A single `reviews` table holds everything for the MVP: the raw input, the
structured static-analysis findings, the personality-flavored AI review, and
metadata needed for sharing.
"""

import datetime
import json
import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON

from app.database import Base


class Review(Base):
    """One submitted review — input code + analysis + personality rewrite."""

    __tablename__ = "reviews"

    # UUID primary key; readable-ish for sharing.
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # What the user pasted. Kept raw so the frontend can re-render the code.
    code_input = Column(Text, nullable=False)

    # "raw" = plain code; "diff" = a git-style diff to analyze.
    input_mode = Column(String(10), default="raw")

    # Language hint. We support Python today; extensible later.
    language = Column(String(20), default="python")

    # Which personality delivered this review.
    personality_id = Column(String(40), nullable=False)

    # The findings JSON from the static analysis engine (structured, verbatim).
    raw_findings = Column(Text, nullable=True)

    # The AI-generated personality review as full text (our serialized response).
    ai_review = Column(Text, nullable=True)

    # Precomputed counts by severity for the summary stats tile.
    summary_stats = Column(JSON, nullable=True)

    # Short, guessable token for shareable links (e.g. /review/share/xK9mP2qR).
    share_token = Column(String(8), unique=True, index=True, nullable=False)

    # When the review was created.
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # ──────────────────── Helpers ────────────────────

    def set_findings(self, analysis_result: dict):
        """Serialize the engine's AnalysisResult into JSON.

        We store raw_findings as a JSON string so the schema of the analysis
        is preserved even if the Python engine changes later.
        """
        self.raw_findings = json.dumps(analysis_result)
        # summary_stats is the same data as stats; keep them in sync.
        self.summary_stats = analysis_result.get("stats", {})

    @property
    def findings(self) -> list:
        """Parse findings as JSON on read."""
        return json.loads(self.raw_findings or "[]")

    @property
    def findings_by_id(self) -> dict:
        """Map of finding id -> finding object for O(1) lookup by frontend."""
        return {f.get("id"): f for f in self.findings}

    def set_ai_review(self, ai_review: dict):
        """Store the personality's JSON response as serialized text.

        The frontend expects a flat structure with opening/closing strings and
        an array of findings, each with its own commentary.
        """
        self.ai_review = json.dumps(ai_review)
