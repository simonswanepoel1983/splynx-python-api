from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "RocketNet Client Portal"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./rocketnet_portal.db"
    
    # Security settings
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Splynx API settings
    splynx_url: str = "https://splynx.rocketnet.com"
    splynx_api_key: Optional[str] = None
    splynx_api_secret: Optional[str] = None
    
    # Redis settings (for caching and sessions)
    redis_url: str = "redis://localhost:6379"
    
    # Frontend settings
    frontend_url: str = "http://localhost:3000"
    
    # Email settings (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()