"""App package init — trigger personality registration on import."""

from app.personality.registry import register_all

register_all()
