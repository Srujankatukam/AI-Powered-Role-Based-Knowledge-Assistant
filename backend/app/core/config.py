"""
Configuration settings for the AI Knowledge Assistant
"""
from typing import List, Optional
from pydantic import BaseSettings, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Knowledge Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # OpenAI (Optional - only needed for GPT models)
    OPENAI_API_KEY: Optional[str] = None
    
    # LLM Configuration (Open Source)
    LLM_TYPE: str = "huggingface"  # Options: "huggingface", "ollama", "llama_cpp"
    LLM_MODEL_NAME: str = "microsoft/DialoGPT-medium"  # Default HuggingFace model
    LLM_DEVICE: str = "cpu"  # Options: "cpu", "cuda", "mps"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_LENGTH: int = 512
    LLM_USE_QUANTIZATION: bool = False
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2:7b"
    
    # Llama.cpp Configuration
    LLAMA_CPP_MODEL_PATH: str = "./data/llm_models/llama-2-7b-chat.gguf"
    LLAMA_CPP_N_CTX: int = 2048
    
    # Embedding Model Configuration
    EMBEDDING_MODEL_TYPE: str = "sentence-transformers"  # Options: "sentence-transformers", "huggingface"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"  # Default Sentence Transformers model
    HUGGINGFACE_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"  # For HuggingFace models
    EMBEDDING_DEVICE: str = "cpu"  # Options: "cpu", "cuda", "mps"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Azure Key Vault
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    KEY_VAULT_URL: Optional[str] = None
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "knowledge-assistant"
    
    # Web Search (Open Source)
    WEB_SEARCH_ENGINE: str = "duckduckgo"  # Options: "duckduckgo", "google", "bing"
    WEB_SEARCH_MAX_RESULTS: int = 5
    WEB_SEARCH_TIMEOUT: int = 10
    EXTRACT_ARTICLE_CONTENT: bool = False
    
    # Monitoring (Open Source)
    ENABLE_MONITORING: bool = True
    MONITORING_DB_PATH: str = "./data/monitoring.db"
    PROMETHEUS_METRICS_ENABLED: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",  # Streamlit
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".txt", ".docx", ".md"]
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure data directories exist
Path(settings.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
Path("./data/documents").mkdir(parents=True, exist_ok=True)
Path("./data/embeddings").mkdir(parents=True, exist_ok=True)