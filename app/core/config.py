from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URL: Optional[str] = None
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_DB: str = "fastapi_db"

    REDIS_URL: Optional[str] = None
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LINKEDIN_ACCESS_TOKEN_URL: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None
    LINKEDIN_AUTH_URL: Optional[str] = None
    LINKEDIN_REST_URL: Optional[str] = None
    LINKEDIN_SCOPE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_url(self) -> str:
        if self.MONGODB_URL:
            return self.MONGODB_URL
        
        auth_str = ""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            auth_str = f"{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
            
        return f"mongodb://{auth_str}{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

settings = Settings() 