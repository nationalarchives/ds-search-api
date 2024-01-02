import os

from app.lib.util import strtobool


class Config:
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = strtobool(os.getenv("DEBUG", "False"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    DISCOVERY_API_URL = os.environ.get("DISCOVERY_API_URL")
    WAGTAIL_API_URL = os.environ.get("WAGTAIL_API_URL")
