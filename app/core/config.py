"""
Central place for all configuration values.

Instead of reading os.environ everywhere in the code, we read it once here
and import the `settings` object anywhere we need a config value.
This also means secrets (DB password, JWT secret, LLM API key) only ever
live in the .env file, never inside the source code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database
    database_url: str

    # jwt auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # llm
    gemini_api_key: str

    # rate limiting
    daily_request_limit: int = 20

    # tells pydantic-settings to load values from a .env file.
    # extra="ignore" because .env also has POSTGRES_USER/PASSWORD/DB, which
    # only docker-compose needs (to create the container), not this app.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Created once at import time, reused everywhere (no need to re-read .env each time)
settings = Settings()
