"""
Configuration management for the application
"""
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings

# Get the backend directory (parent of app/)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings"""
    
    # Database - MySQL
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "lenskart_search"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    
    # Legacy PostgreSQL settings (for backwards compatibility)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lenskart_search"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    
    # Vector DB
    VECTOR_DB_PATH: str = "./data/vector_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Groq API
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"  # or llama-3.3-70b-versatile
    
    # Message Queue (Redis Streams)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Learning Parameters
    CTR_WEIGHT: float = 0.3
    CONVERSION_WEIGHT: float = 0.5
    BOUNCE_PENALTY: float = 0.2
    SEMANTIC_WEIGHT: float = 0.4
    BEHAVIOR_WEIGHT: float = 0.6
    
    # Search Parameters
    TOP_K_RESULTS: int = 20
    TOP_K_FOR_AI_RERANK: int = 50
    
    # Personalization Parameters
    ENABLE_PERSONALIZATION: bool = True
    USER_PREFERENCE_WEIGHT: float = 0.2  # γ in ranking formula
    MIN_INTERACTIONS_FOR_PERSONALIZATION: int = 3
    CATEGORY_AFFINITY_WEIGHT: float = 0.4
    BRAND_AFFINITY_WEIGHT: float = 0.3
    INTERACTION_HISTORY_WEIGHT: float = 0.3
    MAX_SEARCH_HISTORY: int = 50  # Maximum search queries to store
    MAX_RECENT_PRODUCTS: int = 100  # Maximum recent products to track
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

