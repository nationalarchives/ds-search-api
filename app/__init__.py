import logging

from app.lib import cache
from config import Config
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(gunicorn_error_logger.level)

    cache.init_app(app)

    SWAGGER_URL = "/docs"
    API_URL = "http://localhost:65534/spec"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "National Archives Search API"},
    )

    app.register_blueprint(swaggerui_blueprint)

    from .main import bp as main_bp
    from .records import bp as records_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(records_bp, url_prefix="/records")

    return app
