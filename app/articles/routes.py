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
    website_api.params = {}  # TODO: Why are params persisting?
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


@router.get("/filters/")
async def filters() -> list[Filter]:
    filters = []

    # time_period_filter = Filter("Time period", "multiple")
    # for time_period in get_time_periods():
    #     time_period_filter.add_filter_option(
    #         time_period["name"], time_period["value"]
    #     )
    # filters.append(time_period_filter)

    # topics_filter = Filter("Topic", "multiple")
    # topics = get_topics()
    # for topic in sorted(topics, key=lambda x: x["name"]):
    #     topics_filter.add_filter_option(topic["name"], topic["value"])
    # filters.append(topics_filter)

    types_filter = Filter("Type", "multiple")
    types_filter.add_filter_option(
        "Article", "articles.ArticlePage,articles.FocusedArticlePage"
    )
    types_filter.add_filter_option(
        "Gallery", "collections.HighlightGalleryPage"
    )
    types_filter.add_filter_option(
        "Records revealed", "articles.RecordArticlePage"
    )
    types_filter.add_filter_option(
        "Time period", "collections.TimePeriodExplorerPage"
    )
    types_filter.add_filter_option("Topic", "collections.TopicExplorerPage")
    filters.append(types_filter)

    return filters
