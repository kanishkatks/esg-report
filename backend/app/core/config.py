"""
Configuration settings for the RAG Chatbot application.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = "RAG Chatbot API"
    version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Mistral API Configuration
    mistral_api_key: str
    mistral_model: str = "mistral-large-latest"

    # Weaviate Configuration
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: Optional[str] = None

    # Document Processing Configuration
    max_file_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Logging Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
