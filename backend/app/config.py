from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Thư mục gốc của backend (chứa .env, file .db, scripts/, data/)
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Individualized Nutritional and Fitness Orientation"

    # SQLite mặc định. Đường dẫn tương đối được tính từ thư mục backend/
    DATABASE_URL: str = "sqlite:///./fitness_app.db"

    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Gemini API Key (for the chatbot module)
    GEMINI_API_KEY: str = ""

    # Step 2 (Asset Handling): "github_cdn" | "cloudinary" | "s3"
    ASSET_STORAGE_PROVIDER: str = "github_cdn"
    ASSET_BASE_URL: str = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"

    # Cloudinary (tùy chọn khi ASSET_STORAGE_PROVIDER="cloudinary")
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER: str = "fitness_app/exercises"

    # AWS S3 (tùy chọn khi ASSET_STORAGE_PROVIDER="s3")
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "ap-southeast-1"
    AWS_S3_PREFIX: str = "exercises"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # Allowed origins for CORS (allowing React Vite frontend)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton instance used throughout the app
settings = Settings()
