"""
Application configuration, loaded from environment variables (.env).
Centralizing config here means no hard-coded secrets/paths anywhere else.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Smart Traffic Prediction System"
    ENV: str = "development"
    DEBUG: bool = True

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = "postgresql+psycopg2://traffic_user:traffic_pass@localhost:5432/traffic_db"

    # --- Auth / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"  # override via env var in real deployments
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- File storage ---
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"
    MODEL_DIR: str = "saved_models"

    # --- ML/DL ---
    RANDOM_STATE: int = 42
    LSTM_SEQUENCE_LENGTH: int = 24  # e.g. 24 timesteps of history to predict next step

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"  # comma-separated list; add your deployed frontend URL

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
