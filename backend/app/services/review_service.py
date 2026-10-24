"""Orchestration services for the review pipeline."""

import asyncio
import json
import string
import uuid
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from app.analysis import analyze
from app.models.review import Review
from app.personality import registry
from app.personality.rewriter import parse_claude_output, rewrite_findings_stream
from app.schemas.findings import AnalysisResult
from app.schemas.review import ReviewRequest


def generate_share_token() -> str:
    """Create an 8-char, URL-safe, guessable share token."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(__import__("random").choices(alphabet, k=8))


async def analyze_code(request: ReviewRequest) -> AnalysisResult:
    """Run the static analysis engine on the submitted code."""
    return analyze(request.code, request.language, request.input_mode)


async def create_review(request: ReviewRequest, db: Session) -> tuple[str, AnalysisResult]:
    """Create a review: analyze, save, return the review ID and analysis."""
    if request.personality_id not in registry.PERSONALITIES:
        raise ValueError(f"Unknown personality: {request.personality_id}")

    from app.analysis.detector import detect_language

    detected_lang = detect_language(request.code)
    request.language = detected_lang  # auto-detect language

    analysis: AnalysisResult = await asyncio.to_thread(
        analyze, request.code, request.language, request.input_mode
    )

    review_id = str(uuid.uuid4())
    share_token = generate_share_token()

    review = Review(
        id=review_id,
        code_input=request.code,
        input_mode=request.input_mode,
        language=request.language,
        personality_id=request.personality_id,
        share_token=share_token,
    )
    review.set_findings(analysis.model_dump())

    db.add(review)
    db.commit()
    db.refresh(review)

    return review_id, analysis


async def stream_ai_review(review_id: str, analysis: AnalysisResult, request: ReviewRequest) -> AsyncGenerator[str, None]:
    """Stream the personality review from Gemini, parse it, and persist it."""
    if analysis is None:
        db_session = None
        try:
            from app.database import SessionLocal
            db_session = SessionLocal()
            review = db_session.query(Review).filter(Review.id == review_id).one_or_none()
            if review:
                raw = review.findings  # property that parses JSON
                if isinstance(raw, dict) and "findings" in raw:
                    analysis = AnalysisResult(**raw)
                elif isinstance(raw, list):
                    analysis = AnalysisResult(findings=raw, stats=review.summary_stats or {})
                else:
                    analysis = AnalysisResult(findings=[], stats=review.summary_stats or {})
        finally:
            if db_session:
                db_session.close()

    parts: list[str] = []

    stream_gen = rewrite_findings_stream(analysis, request.personality_id, request.code)
    async for chunk in stream_gen:
        parts.append(chunk)
        yield chunk

    raw_text = "".join(parts)
    parsed = parse_claude_output(raw_text)

    db_session = None
    try:
        from app.database import SessionLocal
        db_session = SessionLocal()

        review = db_session.query(Review).filter(Review.id == review_id).one_or_none()
        if review is not None:
            review.set_ai_review(parsed)
            db_session.commit()
    finally:
        if db_session:
            db_session.close()


def build_review_response(db: Session, review_id: str) -> Review | None:
    """Fetch a review by ID (used for GET /review/{id})."""
    return db.query(Review).filter(Review.id == review_id).first()


def build_shared_review_response(db: Session, share_token: str) -> Review | None:
    """Fetch a review by its share token (used for GET /review/share/{token})."""
    return db.query(Review).filter(Review.share_token == share_token).first()
