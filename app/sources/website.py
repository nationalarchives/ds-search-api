import math

from app.articles.schemas import Article, ArticleSearchResults
from app.lib.api import GetAPI
from app.schemas import Filter
from config import Config


class WagtailAPI(GetAPI):
    api_base_url = Config().WAGTAIL_API_URL

    def __init__(self):
        self.api_base_url

    def get_result(self) -> dict:
        url = f"{self.api_base_url}/pages/{self.build_query_string()}"
        return self.execute(url)


class WebsiteArticles(WagtailAPI):
    api_path = "/pages/"

    def add_query(self, query_string: str) -> None:
        self.add_parameter("search", query_string)

    def filters(self) -> list[Filter]:
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

    def get_result(self, page: int | None = 1) -> dict:
        offset = (page - 1) * self.results_per_page
        self.add_parameter("offset", offset)
        self.add_parameter("limit", self.results_per_page)
        # self.add_parameter("fields", "search_description,teaser_image_jpg")  # TODO: Not all pages have a teaser image
        self.add_parameter("fields", "search_description")
        url = self.build_url()
        raw_results = self.execute(url)
        response = ArticleSearchResults()
        for a in raw_results["items"]:
            article = Article()
            article.title = a["title"]
            article.url = a["meta"]["html_url"]
            article.type = a["meta"]["type"]
            article.id = a["id"]
            article.first_published = a["meta"]["first_published_at"]
            article.description = a["meta"]["search_description"]
            # article.image = a["teaser_image_jpg"]
            # TODO: Temp until all pages have a teaser_image
            page_details_api = WebsiteArticles()
            page_details_url = f"{self.api_base_url}{self.api_path}{article.id}"
            page_details = page_details_api.execute(page_details_url)
            article.description = page_details["meta"]["search_description"]
            article.image = page_details["teaser_image"]["image_jpeg"]
            response.results.append(article)
        response.count = raw_results["meta"]["total_count"]
        response.results_per_page = self.results_per_page
        response.page = page
        response.source_url = url
        response.filters = self.filters()
        return response.toJSON()


def get_time_periods():
    api = WagtailAPI()
    # api.results_per_page = 100  # TODO: Make higher
    api.params = {}  # TODO: Why isn't this blank by default?
    api.add_parameter("child_of", 54)  # TODO: Make variable
    results = api.get_result()
    time_periods = [
        {"name": time_period["title"], "value": time_period["id"]}
        for time_period in results["items"]
    ]
    return time_periods


def get_topics():
    api = WagtailAPI()
    # api.results_per_page = 100  # TODO: Make higher
    api.params = {}  # TODO: Why isn't this blank by default?
    api.add_parameter("child_of", 53)  # TODO: Make variable
    results = api.get_result()
    topics = [
        {"name": topic["title"], "value": topic["id"]}
        for topic in results["items"]
    ]
    return topics
