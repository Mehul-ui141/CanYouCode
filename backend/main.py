"""Can You Code — API entry point.

FastAPI app that wires together:
- Static analysis engine (finds real issues)
- Personality system (rewrites findings in character)
- SSE streaming (findings now, personality later)
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reviews import reviews_router
from app.api.personalities import personalities_router
from app.api.health import health_router
from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME + " API",
        description=(
            "Can You Code: paste code, pick a personality, get roasted (or cheered on) "
            "by AI-powered code review."
        ),
        version="0.1.0",
    )

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Simple in-memory rate limiter for /api/review
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import time

    request_counts = {}

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if request.url.path.startswith("/api/review") and request.method == "POST":
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            window = 60  # 1 minute window
            limit = 10   # max 10 reviews per minute per IP

            if client_ip not in request_counts:
                request_counts[client_ip] = []

            # Filter timestamps within window
            request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < window]

            if len(request_counts[client_ip]) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please wait a minute before submitting more code reviews."}
                )

            request_counts[client_ip].append(now)

        return await call_next(request)

    # Create DB tables on startup.
    init_db()
    logger.info("Database initialized")

    # Mount all API routes.
    app.include_router(reviews_router, prefix="/api")
    app.include_router(personalities_router, prefix="/api")
    app.include_router(health_router, prefix="/api")
    logger.info("API routes mounted")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Ensure UTF-8 encoding for all terminal output and streaming responses
    import sys
    import codecs
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
