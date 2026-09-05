from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "GitHub Ranker API"
    secret_key: str = "dev-secret"
    database_url: str = "sqlite:///./ranker.db"
    github_token: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_business: str = ""
    frontend_url: str = "http://localhost:3000"
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
