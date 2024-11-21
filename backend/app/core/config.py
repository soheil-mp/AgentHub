from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os
from functools import lru_cache
import re
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "AgentHub"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4-turbo-preview", description="OpenAI model to use")

    # Redis Configuration
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_DB: int = Field(0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    REDIS_TTL: int = Field(3600, description="Redis TTL in seconds")
    REDIS_URL: str = Field("redis://localhost:6379", description="Redis URL")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, description="Rate limit per minute")
    RATE_LIMIT_REQUESTS: int = Field(100, description="Maximum requests per window")
    RATE_LIMIT_WINDOW: int = Field(60, description="Rate limit window in seconds")

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://frontend:3000",
            "http://localhost:8001",  # Add backend URL
            "http://127.0.0.1:8001"   # Add backend IP
        ],
        description="Allowed CORS origins"
    )

    # Agent Configuration
    DEFAULT_MODEL: str = Field("gpt-3.5-turbo", description="Default LLM model")
    DEFAULT_TEMPERATURE: float = Field(0.7, description="Default temperature for LLM")
    MAX_RETRIES: int = Field(3, description="Maximum retries for failed operations")
    CACHE_TTL: int = Field(3600, description="Cache TTL in seconds")

    # MongoDB Configuration
    MONGODB_HOST: str = Field("localhost", description="MongoDB host")
    MONGODB_PORT: int = Field(27017, description="MongoDB port")
    MONGODB_USER: str = Field("agenthub_user", description="MongoDB username")
    MONGODB_PASSWORD: str = Field("password123", description="MongoDB password")
    MONGODB_DB_NAME: str = Field("agenthub", description="MongoDB database name")
    MONGODB_URL: Optional[str] = None

    # Security
    ENCRYPTION_KEY: str = Field(..., description="32-byte encryption key for sensitive data")
    JWT_SECRET: str = Field(..., description="JWT secret key")

    # Service Configuration
    ENVIRONMENT: str = Field("development", description="Environment (development/production)")
    DEBUG: bool = Field(True, description="Debug mode")

    @validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: str) -> str:
        if not v or v == "your-api-key-here":
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("OpenAI API key must be set in production")
            return "sk-dummy-key-for-development"
        return v

    @validator("ENCRYPTION_KEY")
    def validate_encryption_key(cls, v: str) -> str:
        if not v or v == "your-32-byte-encryption-key-here":
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("Encryption key must be set in production")
            return "dummy-encryption-key-32-bytes-dev"
        return v

    @validator("JWT_SECRET")
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or v == "your-jwt-secret-here":
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("JWT secret must be set in production")
            return "dummy-jwt-secret-for-development"
        return v

    @validator("MONGODB_URL")
    def construct_mongodb_url(cls, v: Optional[str], values: dict) -> str:
        """Construct MongoDB URL if not provided."""
        if v:
            return v
        
        user = quote_plus(values.get("MONGODB_USER", "agenthub_user"))
        password = quote_plus(values.get("MONGODB_PASSWORD", "password123"))
        host = values.get("MONGODB_HOST", "localhost")
        port = values.get("MONGODB_PORT", 27017)
        db_name = values.get("MONGODB_DB_NAME", "agenthub")
        
        return (
            f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
            "?authSource=admin"
        )

    @validator("REDIS_URL")
    def construct_redis_url(cls, v: str, values: dict) -> str:
        """Construct Redis URL with password if provided."""
        if values.get("REDIS_PASSWORD"):
            password = quote_plus(values["REDIS_PASSWORD"])
            host = values.get("REDIS_HOST", "localhost")
            port = values.get("REDIS_PORT", 6379)
            db = values.get("REDIS_DB", 0)
            return f"redis://:{password}@{host}:{port}/{db}"
        return v

    def get_redis_url(self) -> str:
        """Get Redis URL with proper authentication."""
        if not self.REDIS_ENABLED:
            return ""
        return self.REDIS_URL

    def get_mongodb_url(self) -> str:
        """Get MongoDB URL with proper authentication."""
        return self.MONGODB_URL

    def is_valid_openai_key(self) -> bool:
        """Check if the OpenAI API key is valid."""
        if self.ENVIRONMENT == "development" and self.OPENAI_API_KEY == "sk-dummy-key-for-development":
            return True
        
        # Check if key matches OpenAI key pattern
        key_pattern = r'^sk-[A-Za-z0-9]{32,}$'
        return bool(re.match(key_pattern, self.OPENAI_API_KEY))

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create settings instance
settings = get_settings() 