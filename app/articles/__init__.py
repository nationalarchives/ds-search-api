from fastapi import APIRouter

router = APIRouter()

from app.articles import routes  # noqa: E402,F401
