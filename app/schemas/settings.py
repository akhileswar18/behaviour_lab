from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./data/behavior_lab.db"
    log_level: str = "INFO"
    deterministic_mode: bool = True
    simulation_seed: int = 42
    message_default_intent: str = "observe"
    message_default_tone: str = "neutral"
    relationship_positive_delta: float = 0.08
    relationship_negative_delta: float = 0.06
    recent_event_window: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
