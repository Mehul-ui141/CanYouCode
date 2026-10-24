"""Schemas for the personality listing endpoint."""

from pydantic import BaseModel


class PersonalityInfo(BaseModel):
    """A personality card shown in the picker grid.

    Attributes:
        id: Unique key used when submitting a review.
        name: Human-readable display name.
        description: One-line explanation of what the personality is like.
        emoji: Emoji avatar to display on the card.
        color: Hex accent color for theming that personality.
        tone_preview: A one-line sample of how this personality sounds.
    """

    id: str
    name: str
    description: str
    emoji: str
    color: str  # Hex color, e.g. #B91C1C
    tone_preview: str
