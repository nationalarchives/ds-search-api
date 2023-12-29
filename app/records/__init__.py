from flask import Blueprint

bp = Blueprint("records", __name__)

from app.records import routes  # noqa: E402,F401
