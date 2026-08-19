from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Tender Response System"
    app_env: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ao_response"
    postgres_user: str = "ao_user"
    postgres_password: str = "aziz1234"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "tender_documents"

    redis_host: str = "localhost"
    redis_port: int = 6379

    llm_provider: str = "openai"
    llm_model: str = ""

    upload_dir: str = "documents"
    generated_dir: str = "generated"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
