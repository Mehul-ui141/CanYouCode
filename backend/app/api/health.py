"""Health check endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.config import settings

health_router = APIRouter()


@health_router.get("/health", tags=["Health"])
async def health_check():
    """Confirm the API is alive and knows its config name."""
    return {"status": "ok", "app": settings.APP_NAME}
