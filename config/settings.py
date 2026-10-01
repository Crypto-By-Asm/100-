from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Crypto Bot by ASM Traders"
    app_env: str = "development"
    secret_key: str = "change-this-to-a-long-random-secret-key-at-least-32-chars"

    gemini_api_key: str = ""
    binance_base_url: str = "https://api.binance.com"

    database_url: str = "sqlite:///./crypto_bot.db"

    blog_auto_generate: bool = True
    blog_batch_size: int = 30
    blog_language: str = "en"
    site_url: str = "https://your-domain.example"

    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
