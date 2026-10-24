"""Review submission and retrieval endpoints.

The signature endpoint POST /review streams an SSE response in three phases:
  1. analysis — findings from the static engine (fast, <100ms)
  2. text — personality commentary streaming from Claude (2-5s)
  3. complete — review ID + share URL, then the saved AI review
"""

import json
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewListItem, ReviewRequest
from app.services.review_service import (
    build_review_response,
    build_shared_review_response,
    create_review,
    stream_ai_review,
)

reviews_router = APIRouter()


def _sse(data: dict[str, Any]) -> str:
    """Wrap a JSON object as an SSE data event."""
    return "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"


@reviews_router.post("/review", tags=["Reviews"], status_code=status.HTTP_200_OK)
async def submit_review(
    request: ReviewRequest,
    response: Response,
    req: Request,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Submit code for review. Streams findings + personality commentary as SSE.

    SSE event stream:
      {"type": "analysis", "review_id": "...", ...}
      {"type": "text", "content": "..."}
      {"type": "complete", "review_id": "...", "share_token": "..."}
    """
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"

    async def event_stream() -> AsyncGenerator[str, None]:
        # Phase 1: run the static analysis immediately.
        try:
            review_id, analysis = await create_review(request, db)
        except Exception as exc:
            yield _sse({"type": "error", "content": f"Analysis failed: {exc}"})
            return

        # Send findings to the frontend so they render instantly.
        yield _sse({
            "type": "analysis",
            "review_id": review_id,
            "personality_id": request.personality_id,
            "input_mode": request.input_mode,
            "language": request.language,
            "findings": [f.model_dump() for f in analysis.findings],
        })

        # Phase 2: stream the personality commentary.
        try:
            async for chunk in stream_ai_review(review_id, analysis, request):
                if await req.is_disconnected():
                    return
                yield _sse({"type": "text", "content": chunk})
        except Exception as exc:
            if await req.is_disconnected():
                return
            yield _sse({"type": "error", "content": f"Review generation failed: {exc}"})
            return

        # Phase 3: finalize with the saved review details.
        saved = build_review_response(db, review_id)
        if saved is None:
            yield _sse({"type": "error", "content": "Review not saved"})
            return

        yield _sse({
            "type": "complete",
            "review_id": review_id,
            "share_token": saved.share_token,
            "share_url": f"/review/share/{saved.share_token}",
            "findings_count": len(saved.findings),
            "stats": saved.summary_stats,
        })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


def _review_to_dict(review: Review) -> dict[str, Any]:
    """Serialize a Review ORM object to a JSON-friendly dict."""
    ai_parsed = {}
    if review.ai_review:
        try:
            ai_parsed = json.loads(review.ai_review)
        except json.JSONDecodeError:
            pass

    findings_data = review.findings
    if isinstance(findings_data, str):
        try:
            findings_data = json.loads(findings_data)
        except json.JSONDecodeError:
            findings_data = []

    # findings_data might be the full AnalysisResult dict with a "findings" key.
    if isinstance(findings_data, dict) and "findings" in findings_data:
        findings_list = findings_data["findings"]
    elif isinstance(findings_data, list):
        findings_list = findings_data
    else:
        findings_list = []

    return {
        "id": review.id,
        "personality_id": review.personality_id,
        "input_mode": review.input_mode,
        "language": review.language,
        "findings": [
            {
                "id": f.get("id", ""),
                "category": f.get("category", ""),
                "rule": f.get("rule", ""),
                "severity": f.get("severity", "info"),
                "message": f.get("message", ""),
                "line_start": f.get("line_start"),
                "line_end": f.get("line_end"),
                "code_snippet": f.get("code_snippet"),
                "suggestion": f.get("suggestion"),
            }
            for f in findings_list
        ],
        "ai_review": review.ai_review or "",
        "opening": ai_parsed.get("opening", ""),
        "closing": ai_parsed.get("closing", ""),
        "overall_grade": ai_parsed.get("overall_grade", ""),
        "summary_stats": review.summary_stats or {},
        "share_url": f"/review/share/{review.share_token}",
        "created_at": review.created_at.isoformat(),
        "code_input": review.code_input,
    }


@reviews_router.get("/review/{review_id}", tags=["Reviews"])
async def get_review_endpoint(review_id: str, db: Session = Depends(get_db)):
    """Fetch a saved review by ID."""
    review = build_review_response(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return _review_to_dict(review)


@reviews_router.get("/review/share/{share_token}", tags=["Reviews"])
async def get_shared_review(share_token: str, db: Session = Depends(get_db)):
    """Fetch a review via its shareable link token."""
    review = build_shared_review_response(db, share_token)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return _review_to_dict(review)


@reviews_router.get("/reviews", tags=["Reviews"])
async def list_reviews(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List recent reviews (compact view)."""
    reviews = (
        db.query(Review)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        ReviewListItem(
            id=r.id,
            personality_id=r.personality_id,
            language=r.language,
            summary_stats=r.summary_stats or {},
            created_at=r.created_at,
            code_preview=(r.code_input[:80] + "...") if r.code_input else "",
        )
        for r in reviews
    ]
