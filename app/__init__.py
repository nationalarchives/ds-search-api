import os

import sentry_sdk
from fastapi import FastAPI


def get_config():
    config_class = os.getenv("CONFIG", "config.Production")
    components = config_class.split(".")
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod()


def create_app():
    config = get_config()

    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            traces_sample_rate=config.SENTRY_SAMPLE_RATE,
            profiles_sample_rate=config.SENTRY_SAMPLE_RATE,
        )

    app = FastAPI(title="ETNA Search API", log_level=config.LOG_LEVEL)
    app.state.config = config
    base_uri = "/api/v1"

    @app.get("/healthcheck/live/", include_in_schema=False)
    def healthcheck():
        return {"status": "ok"}

    from .articles import routes as article_routes
    from .records import routes as record_routes

    app.include_router(
        record_routes.router, prefix=f"{base_uri}/records", tags=["Records"]
    )
    app.include_router(
        article_routes.router, prefix=f"{base_uri}/articles", tags=["Articles"]
    )

    return app
