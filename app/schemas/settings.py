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
    hunger_tick_delta: float = 0.08
    social_need_tick_delta: float = 0.03
    safety_decay_per_tick: float = 0.02
    severe_need_threshold: float = 0.8
    interruption_urgency_threshold: float = 0.7
    low_resource_threshold: int = 1
    resource_consumption_amount: int = 1
    policy_mode_default: str = "deterministic"
    llm_provider: str = "openai_compatible"
    llm_model: str = "gpt-4o-mini"
    llm_endpoint: str = "http://127.0.0.1:11434/v1/chat/completions"
    llm_api_key: str | None = None
    llm_timeout_seconds: float = 4.0
    llm_temperature: float = 0.0
    llm_max_tokens: int = 256
    llm_debug_store_prompt: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
