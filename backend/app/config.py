from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Warehouse Knowledge Assistant"
    environment: str = Field(default="local")
    log_level: str = Field(default="INFO")

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str | None = None
    redis_index_name: str = Field(default="warehouse_index")
    redis_prefix: str = Field(default="doc")

    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)

    ollama_host: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="mistral")
    ollama_timeout: int = Field(default=60)
    ollama_temperature: float = Field(default=0.2)
    ollama_allowed_models: tuple[str, ...] = Field(
        default=("mistral", "llama3", "phi3", "gemma")
    )

    top_k: int = Field(default=4)
    max_context_tokens: int = Field(default=1200)
    guard_blocklist: tuple[str, ...] = Field(
        default=(
            "ignore previous",
            "disregard previous",
            "reveal system prompt",
            "shutdown",
        )
    )

    pii_mask_token: str = Field(default="[REDACTED]")
    ingestion_namespace: str = Field(default="warehouse-knowledge")
    data_path: str = Field(default="data")

    metrics_namespace: str = Field(default="rag_backend")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    @field_validator("ollama_allowed_models", mode="before")
    @classmethod
    def _parse_models(cls, value: str | tuple[str, ...]):
        if isinstance(value, str):
            return tuple(item.strip() for item in value.split(",") if item.strip())
        return tuple(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
