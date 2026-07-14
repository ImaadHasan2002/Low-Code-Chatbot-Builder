from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Botcraft"
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    # BASE URLs
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "core_db"

    # JWT settings
    SECRET_KEY: str = "botcraft-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True

    # AWS settings
    AWS_REGION: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_BUCKET_URL: str = ""

    # Pinecone settings
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX_NAME: str = ""
    PINECONE_HOST: str = ""
    # Serverless spec used when auto-creating a missing index
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI settings
    OPENAI_API_KEY: str = ""

    # Anthropic settings
    ANTHROPIC_API_KEY: str = ""

    # CORS: comma-separated list of allowed origins
    CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list:
        if self.CORS_ORIGINS:
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return [self.FRONTEND_URL, "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
