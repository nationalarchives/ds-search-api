from fastapi import APIRouter

router = APIRouter()

from app.records import routes  # noqa: E402,F401
