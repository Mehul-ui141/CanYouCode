"""Application configuration.

All settings are loaded from environment variables using Pydantic Settings.
This keeps secrets out of source control and makes deployment trivial:
set the env vars and the app just works.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app configuration, typed and validated."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ──────────────────── Gemini / AI ────────────────────
    # Your Google Gemini API key. Required for AI-powered code reviews.
    GEMINI_API_KEY: str

    # Which Claude model does the rewriting. Sonnet 5.5 is the sweet spot:
    # creative, fast, and cheap. Upgrade to Opus only if quality suffers.
    CLAUDE_MODEL: str = "claude-sonnet-5-5"

    # ──────────────────── Database ────────────────────
    DATABASE_URL: str = "sqlite:///./canyoucode.db"

    # ──────────────────── Server ────────────────────
    # Origins allowed to call the API (the Vite dev server + any production build).
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]

    # Application name, used in API metadata.
    APP_NAME: str = "Can You Code"

    # Debug flag. When True, some endpoints emit extra verbosity.
    DEBUG: bool = True


# A single shared settings instance for the whole app.
settings = Settings()
