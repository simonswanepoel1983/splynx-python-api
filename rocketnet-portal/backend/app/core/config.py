"""
Configuration settings for RocketNet Portal
Includes Splynx API configuration and other environment variables
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    APP_NAME: str = "RocketNet Portal"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_EXPIRE_SECONDS: int = 3600
    
    # Splynx Configuration
    SPLYNX_URL: str = Field(..., description="Splynx instance URL")
    SPLYNX_API_KEY: str = Field(..., description="Splynx API key")
    SPLYNX_API_SECRET: str = Field(..., description="Splynx API secret")
    SPLYNX_TIMEOUT: int = 30
    
    # Features
    ENABLE_SPEED_TEST: bool = True
    RETENTION_FEE_AMOUNT: float = 25.00
    MAX_SPEED_TESTS_PER_DAY: int = 5
    
    # External Services
    SPEED_TEST_PROVIDER: str = "ookla"  # ookla, fast, custom
    SPEED_TEST_API_KEY: Optional[str] = None
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True) 
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("SPLYNX_URL")
    def validate_splynx_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("Splynx URL must start with http:// or https://")
        return v.rstrip("/")
    
    @validator("RETENTION_FEE_AMOUNT")
    def validate_retention_fee(cls, v):
        if v < 0:
            raise ValueError("Retention fee amount must be non-negative")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()