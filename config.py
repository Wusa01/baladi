import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-only-change-this-key"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///baladi.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    LANGUAGES = ["ar", "fr"]
    BABEL_DEFAULT_LOCALE = "ar"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    WTF_CSRF_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"

    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
