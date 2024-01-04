from app.articles import router
from app.sources.website import WebsiteArticles, get_time_periods, get_topics

from .schemas import ArticleFilter, ArticleSearchResults


@router.get("/")
async def index(
    q: str | None = "", page: int | None = 1
) -> ArticleSearchResults:
    website_api = WebsiteArticles()
    website_api.add_query(q or "")
    results = website_api.get_results(page)
    return results


@router.get("/filters/")
async def filters() -> list[ArticleFilter]:
    filters = []
    time_period_filter = ArticleFilter("Time period")
    for time_period in get_time_periods():
        time_period_filter.add_filter_option(
            time_period["name"], time_period["value"]
        )
    filters.append(time_period_filter)
    topics_filter = ArticleFilter("Topics")
    for topic in get_topics():
        topics_filter.add_filter_option(topic["name"], topic["value"])
    filters.append(topics_filter)
    return filters
