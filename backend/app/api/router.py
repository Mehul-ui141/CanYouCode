"""Aggregates all API route modules into a single router."""

from fastapi import APIRouter

from app.api.health import health_router
from app.api.personalities import personalities_router
from app.api.reviews import reviews_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(personalities_router)
api_router.include_router(reviews_router)
