import os

from app.lib.util import strtobool


class Config:
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = strtobool(os.getenv("DEBUG", "False"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    ROSETTA_API_URL = os.environ.get("ROSETTA_API_URL").rstrip("/")
    WAGTAIL_API_URL = os.environ.get("WAGTAIL_API_URL").rstrip("/")
    ELASTICSEARCH_RESULTS_LIMIT = int(
        os.environ.get("ELASTICSEARCH_RESULTS_LIMIT", "10000")
    )
