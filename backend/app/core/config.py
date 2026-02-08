from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="AutoInvest", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Database
    database_url: str = Field(alias="DATABASE_URL")
    database_url_sync: str = Field(alias="DATABASE_URL_SYNC")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Security
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    
    # External APIs
    finnhub_api_key: Optional[str] = Field(default=None, alias="FINNHUB_API_KEY")
    alpha_vantage_api_key: Optional[str] = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    news_api_key: Optional[str] = Field(default=None, alias="NEWS_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    polygon_api_key: Optional[str] = Field(default=None, alias="POLYGON_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    
    # Data Paths
    raw_data_path: str = Field(default="./data/raw", alias="RAW_DATA_PATH")
    processed_data_path: str = Field(default="./data/processed", alias="PROCESSED_DATA_PATH")
    qlib_data_path: str = Field(default="./data/qlib_data", alias="QLIB_DATA_PATH")
    
    # Model Settings
    model_cache_path: str = Field(default="./models/cache", alias="MODEL_CACHE_PATH")
    default_model_type: str = Field(default="temporal_fusion_transformer", alias="DEFAULT_MODEL_TYPE")
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
