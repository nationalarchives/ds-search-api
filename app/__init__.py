from config import Config
from fastapi import FastAPI


def create_app():
    config = Config()
    app = FastAPI(log_level=config.LOG_LEVEL)

    @app.get("/healthcheck/live/", include_in_schema=False)
    def healthcheck():
        return {"status": "ok"}

    from .articles import routes as article_routes
    from .records import routes as record_routes

    app.include_router(
        record_routes.router, prefix="/records", tags=["records"]
    )
    app.include_router(
        article_routes.router, prefix="/articles", tags=["articles"]
    )

    return app
