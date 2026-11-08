from pydantic settings import BaseSettings, SettingConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Individualized Nutritional and Fitness Orientation"

    # SQLite default database URL
    DATABASE_URL: str = "sqlite:///./fitness_app.db"

    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
        
    # Gemini API Key (for the chatbot module)
    GEMINI_API_KEY: str = ""
    
    # Allowed origins for CORS (allowing React Vite frontend)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    
    # Singleton instance used throughout the app
    settings = Settings()