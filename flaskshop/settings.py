# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from pathlib import Path

# if os.environ['ENV'] == 'dev':
#     ENV = "dev"

class DBConfig:
    if os.environ['FLASK_ENV'] == 'prod':
        db_type = os.getenv("DB_TYPE", "postgresql")
        user = os.getenv("DB_USER", "glenbert_colt")
        passwd = os.getenv("DB_PASSWD", "Nelly3253")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", 5432)
        db_name = os.getenv("DB_NAME", "glenbert_flaskshop")
        if db_type == "postgresql":
            db_uri = f"postgresql://{user}:{passwd}@{host}:{port}/{db_name}"
        elif db_type == "mysql":
            db_uri = (
                f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"
            )
        redis_uri = "redis://localhost:6379"
        esearch_uri = "localhost"
    else:
        db_type = os.getenv("DB_TYPE", "mysql")
        user = os.getenv("DB_USER", "root")
        passwd = os.getenv("DB_PASSWD", "Nelly3253")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", 3306)
        db_name = os.getenv("DB_NAME", "flaskshop")
        if db_type == "postgresql":
            db_uri = f"postgresql://{user}:{passwd}@{host}:{port}/{db_name}"
        elif db_type == "mysql":
            db_uri = (
                f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"
            )
        redis_uri = "redis://localhost:6379"
        esearch_uri = "localhost"


# class DBConfig:
#     db_type = os.getenv("DB_TYPE", "mysql")
#     user = os.getenv("DB_USER", "root")
#     passwd = os.getenv("DB_PASSWD", "Nelly3253")
#     host = os.getenv("DB_HOST", "127.0.0.1")
#     port = os.getenv("DB_PORT", 3306)
#     db_name = os.getenv("DB_NAME", "flaskshop")
#     if db_type == "postgresql":
#         db_uri = f"postgresql://{user}:{passwd}@{host}:{port}/{db_name}"
#     elif db_type == "mysql":
#         db_uri = (
#             f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"
#         )
#     redis_uri = "redis://localhost:6379"
#     esearch_uri = "localhost"


class Config:
    ENV = "dev"
    FLASK_DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "thisisashop")

    # Redis
    # if redis is enabled, it can be used for:
    #   - cache
    #   - save product description
    #   - save page content
    USE_REDIS = False
    REDIS_URL = os.getenv("REDIS_URI", DBConfig.redis_uri)

    # Elasticsearch
    # if elasticsearch is enabled, the home page will have a search bar
    # and while add a product, the search index will get update
    USE_ES = False
    ES_HOSTS = [
        os.getenv("ESEARCH_URI", DBConfig.esearch_uri),
    ]

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", DBConfig.db_uri)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_QUERY_TIMEOUT = 0.1  # log the slow database query, and unit is second
    SQLALCHEMY_RECORD_QUERIES = True

    # Dir
    APP_DIR = Path(__file__).parent  # This directory
    PROJECT_ROOT = APP_DIR.parent
    STATIC_DIR = APP_DIR / "static"
    UPLOAD_FOLDER = "upload"
    UPLOAD_DIR = STATIC_DIR / UPLOAD_FOLDER
    DASHBOARD_TEMPLATE_FOLDER = APP_DIR / "templates" / "dashboard"
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/placeholders")

    PURCHASE_URI = os.getenv("PURCHASE_URI", "")

    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = os.getenv("FLASK_DEBUG", False)  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = False

    MESSAGE_QUOTA = 10

    LANGUAGES = {"en": "English"}
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "en_US")
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")
    BABEL_TRANSLATION_DIRECTORIES = os.getenv(
        "BABEL_TRANSLATION_DIRECTORIES", "../translations"
    )
    BABEL_CURRENCY = os.getenv("BABEL_CURRENCY", "USD")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "mail.glenbertsfish.com")
    MAIL_PORT = os.getenv("MAIL_PORT", 587)
    MAIL_TLS = os.getenv("MAIL_TLS", True)
    MAIL_SSL = os.getenv("MAIL_SSL", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "orders@glenbertsfish.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "Nelly3253")

    GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")


class ProdConfig(Config):
    ENV = "prod"
    FLASK_DEBUG = False
    DEBUG_TB_ENABLED = False
