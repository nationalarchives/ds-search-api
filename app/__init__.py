from config import Config
from fastapi import FastAPI, Request


def create_app():
    config = Config()
    app = FastAPI(log_level=config.LOG_LEVEL)

    from .records import routes as record_routes

    app.include_router(
        record_routes.router, prefix="/records", tags=["records"]
    )

    @app.get("/healthcheck/live", include_in_schema=False)
    def healthcheck():
        return "ok"

    return app
