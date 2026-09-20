from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./biz_intel.db"
    anthropic_api_key: str = ""
    google_places_api_key: str = ""
    tavily_api_key: str = ""
    mock_mode: bool = True
    llm_model: str = "claude-sonnet-4-6"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
