from app.schemas import APISearchResponse, APISearchResult
from pydantic import ConfigDict


class Article(APISearchResult):
    url: str = ""
    type_label: str = ""
    # first_published: str = ""
    image: dict | None = None

    def __str__(self):
        return f"Article {self.title}"

    def toJSON(self):
        return self.__dict__


class ArticleSearchResults(APISearchResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[Article] = []
