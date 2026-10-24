import os
from pathlib import Path
from dotenv import load_dotenv

import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def get_database_url() -> str:
    env_db = os.getenv("DATABASE_URL")
    
    # Check if running in Vercel or AWS Lambda serverless read-only environment
    is_serverless = bool(os.getenv("VERCEL")) or bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME")) or bool(os.getenv("NOW_REGION"))
    
    is_readonly_fs = False
    try:
        test_file = BASE_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
    except Exception:
        is_readonly_fs = True

    if is_serverless or is_readonly_fs:
        tmp_db = Path("/tmp/restaurant.db")
        if not tmp_db.exists():
            # Copy pre-seeded template database to writable /tmp
            candidates = [
                BASE_DIR / "restaurant.db",
                BASE_DIR.parent / "restaurant.db",
                Path(__file__).resolve().parent.parent.parent / "restaurant.db"
            ]
            for cand in candidates:
                if cand.exists():
                    try:
                        shutil.copyfile(cand, tmp_db)
                        os.chmod(tmp_db, 0o666)
                        break
                    except Exception:
                        pass
        else:
            try:
                os.chmod(tmp_db, 0o666)
            except Exception:
                pass
        return f"sqlite:///{tmp_db}"

    if env_db:
        return env_db

    return f"sqlite:///{BASE_DIR / 'restaurant.db'}"

class Settings:
    PROJECT_NAME: str = "Savory AI Bistro"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "savory-super-secret-jwt-key-2026-michelin-star")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    DATABASE_URL: str = get_database_url()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Firebase Cloud Settings
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    FIREBASE_CREDENTIALS_JSON: str = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "savory-ai-bistro")
    FIREBASE_SYNC_ENABLED: bool = os.getenv("FIREBASE_SYNC_ENABLED", "true").lower() in ("true", "1")

settings = Settings()
