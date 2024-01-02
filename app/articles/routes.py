from app.articles import router
from app.sources.website import WebsiteArticles

from .schemas import ArticleSearchResults


@router.get("/")
async def index(
    q: str | None = "", page: int | None = 1
) -> ArticleSearchResults:
    website_api = WebsiteArticles()
    website_api.add_query(q or "")
    results = website_api.get_results(page)
    return results
