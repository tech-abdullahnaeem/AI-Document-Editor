"""
Configuration management for RAG LaTeX Fixer
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Configuration
    PRIMARY_MODEL: str = "gemini-2.0-flash-exp"
    FALLBACK_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # RAG Configuration
    RETRIEVAL_TOP_K: int = 5
    RERANK_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "knowledge_base"
    TEMPLATES_DIR: Path = KNOWLEDGE_BASE_DIR / "templates"
    FIXES_DIR: Path = KNOWLEDGE_BASE_DIR / "fixes"
    PATTERNS_DIR: Path = KNOWLEDGE_BASE_DIR / "patterns"
    EMBEDDINGS_DIR: Path = KNOWLEDGE_BASE_DIR / "embeddings"
    
    # System Configuration
    MAX_RETRIES: int = 3
    COMPILATION_TIMEOUT: int = 30
    LOG_LEVEL: str = "INFO"
    
    # Supported Formats
    SUPPORTED_FORMATS: list = [
        "IEEE_two_column",
        "ACM_format",
        "Springer_format",
        "generic"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables from FastAPI

# Global settings instance
settings = Settings()

# Ensure directories exist
settings.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
settings.TEMPLATES_DIR.mkdir(exist_ok=True)
settings.FIXES_DIR.mkdir(exist_ok=True)
settings.PATTERNS_DIR.mkdir(exist_ok=True)
settings.EMBEDDINGS_DIR.mkdir(exist_ok=True)
