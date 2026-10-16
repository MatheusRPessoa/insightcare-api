from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    aws_profile: str = "insightcare"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-micro-v1:0"


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
