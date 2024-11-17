from pydantic_settings import BaseSettings
from typing import List
import re
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentHub"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI settings with validation
    OPENAI_API_KEY: str
    
    @property
    def is_valid_openai_key(self) -> bool:
        """Check if OpenAI API key format is valid."""
        return bool(re.match(r'^sk-(?:proj-)?[A-Za-z0-9]{32,}$', self.OPENAI_API_KEY))
    
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Development
        "http://localhost:3000",  # Alternative development port
    ]
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_TTL: int = 3600  # Cache TTL in seconds
    REDIS_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Agent settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_RETRIES: int = 3
    CACHE_TTL: int = 3600
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if not settings.is_valid_openai_key:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "Invalid OpenAI API key format. "
            "Key should start with 'sk-' or 'sk-proj-' followed by at least 32 characters"
        )
    return settings

settings = get_settings() 