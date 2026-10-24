"""List all available review personalities."""

from fastapi import APIRouter

from app.personality import PERSONALITIES
from app.schemas.personality import PersonalityInfo

personalities_router = APIRouter()


@personalities_router.get("/personalities", tags=["Personalities"])
async def list_personalities():
    """Return all 12 available personality options."""
    return [PersonalityInfo(**p.to_dict()) for p in PERSONALITIES.values()]
