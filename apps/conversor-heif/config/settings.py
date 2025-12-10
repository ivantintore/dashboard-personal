from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import datetime


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Conversor HEIC a JPG"
    app_version: str = f"1.0.{int(datetime.datetime.now().timestamp())}"
    debug: bool = False
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: Path = Path("uploads")
    allowed_extensions: set = {".heic", ".heif", ".pdf"}
    
    # Image conversion settings
    default_quality: int = 85
    max_quality: int = 100
    min_quality: int = 1
    
    # PDF processing settings
    max_pdf_pages: int = 100
    max_images_per_page: int = 10
    
    # Output settings
    output_format: str = "JPEG"
    output_extension: str = ".jpg"
    
    # Security settings
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
