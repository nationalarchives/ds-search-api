from app.articles import router
from app.schemas import Filter
from app.sources.website import WebsiteArticles, get_time_periods, get_topics

from .schemas import ArticleSearchResults


@router.get("/")
async def index(
    q: str | None = None,
    type: str | None = None,
    order: str | None = None,
    page: int | None = 1,
) -> ArticleSearchResults:
    website_api = WebsiteArticles()
    # website_api.params = {}  # TODO: Why are params persisting?
    if q:
        website_api.add_query(q)
    if type:
        website_api.add_parameter("type", type)
    else:
        website_api.add_parameter(
            "type",
            ",".join(
                [
                    "articles.ArticlePage",
                    "articles.FocusedArticlePage",
                    "articles.RecordArticlePage",
                    "collections.HighlightGalleryPage",
                    "collections.TimePeriodExplorerPage",
                    "collections.TopicExplorerPage",
                ]
            ),
        )
    if order == "alphabetical" or order == "alphabetical:asc":
        website_api.add_parameter("order", "title")
    elif order == "alphabetical:desc":
        website_api.add_parameter("order", "-title")
    elif order == "date" or order == "date:desc":
        website_api.add_parameter("order", "-first_published_at")
    elif order == "date:asc":
        website_api.add_parameter("order", "first_published_at")
    results = website_api.get_result(page)
    return results
