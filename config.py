import os

from app.lib.util import strtobool


class Base(object):
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

    DEBUG = strtobool(os.getenv("DEBUG", "False"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

    ROSETTA_API_URL = os.environ.get("ROSETTA_API_URL").rstrip("/")
    WAGTAIL_API_URL = os.environ.get("WAGTAIL_API_URL").rstrip("/")

    ELASTICSEARCH_RESULTS_LIMIT = int(
        os.environ.get("ELASTICSEARCH_RESULTS_LIMIT", "10000")
    )


class Production(Base):
    pass


class Staging(Base):
    pass


class Develop(Base):
    DEBUG = strtobool(os.getenv("DEBUG", "True"))


class Test(Base):
    ENVIRONMENT = "test"

    DEBUG = True
