from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./iso22000_fsms.db"  # Default to SQLite for development
    DATABASE_TYPE: str = "sqlite"  # sqlite or postgresql
    
    # Security Configuration
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application Configuration
    APP_NAME: str = "ISO 22000 FSMS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_CREDENTIALS: bool = True
    
    # File Storage Configuration (AWS S3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: str = "iso22000-fsms-files"
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_FILE_TYPES: str = "pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif"
    
    # Notification Configuration
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_RETENTION_DAYS: int = 30
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    @validator("ALLOWED_FILE_TYPES")
    def parse_allowed_file_types(cls, v):
        return [file_type.strip() for file_type in v.split(",")]
    
    @validator("DATABASE_URL", pre=True)
    def set_database_url(cls, v, values):
        """Set database URL based on environment"""
        if "ENVIRONMENT" in values and values["ENVIRONMENT"] == "production":
            # Use PostgreSQL in production
            return v or "postgresql://user:password@localhost/iso22000_fsms"
        else:
            # Use SQLite in development
            return v or "sqlite:///./iso22000_fsms.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings() 