from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./whatnext.db",
        alias="DATABASE_URL",
    )
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="content_embeddings", alias="QDRANT_COLLECTION")
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    cors_origins_raw: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")
    explanation_model: str = Field(default="llama-3.3-70b-versatile", alias="EXPLANATION_MODEL")
    # online_discovery_model: str = Field(default="groq/compound-mini", alias="ONLINE_DISCOVERY_MODEL")
    online_discovery_model: str = Field(default="llama-3.3-70b-versatile", alias="ONLINE_DISCOVERY_MODEL")
    embedding_dimensions: int = Field(default=384, alias="EMBEDDING_DIMENSIONS")
    ai_timeout_seconds: int = 20

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
