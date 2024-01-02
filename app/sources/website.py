from app.articles.schemas import Article, ArticleSearchResults
from config import Config

from .api import GetAPI


class WebsiteArticles(GetAPI):
    def __init__(self):
        self.api_url = Config().WAGTAIL_API_URL

    def add_query(self, query_string: str) -> None:
        self.add_parameter("search", query_string)

    def build_query_string(self) -> str:
        return "&".join(
            ["=".join((key, str(value))) for key, value in self.filters.items()]
        )

    def get_results(self, page: int | None = 1) -> dict:
        offset = (page - 1) * self.results_per_page
        self.add_parameter("offset", offset)
        self.add_parameter("limit", self.results_per_page)
        url = f"{self.api_url}/pages/?{self.build_query_string()}"
        raw_results = self.execute(url)
        response = ArticleSearchResults()
        for a in raw_results["items"]:
            article = Article()
            article.title = a["title"]
            article.url = a["meta"]["html_url"]
            article.type = a["meta"]["type"]
            article.id = a["id"]
            article.first_published = a["meta"]["first_published_at"]
            response.results.append(article)
        response.count = raw_results["meta"]["total_count"]
        return response.toJSON()
