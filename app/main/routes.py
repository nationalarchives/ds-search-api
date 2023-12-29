from app.lib import cache, cache_key_prefix
from app.main import bp
from flask import current_app, jsonify, request
from flask_swagger import swagger


@bp.route("/")
# @cache.cached(key_prefix=cache_key_prefix)
def index():
    return 'Are you looking for the <a href="/docs">docs</a>?'


@bp.route("/spec")
# @cache.cached(key_prefix=cache_key_prefix)
def spec():
    swag = swagger(current_app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "National Archives Search API"
    return jsonify(swag)
