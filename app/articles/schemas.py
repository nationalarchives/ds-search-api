from app.schemas import APIResponse, APIResult
from pydantic import ConfigDict


class Article(APIResult):
    url: str = ""
    type: str = ""
    first_published: str = ""
    image: dict | None = None

    def __str__(self):
        return f"Article {self.title}"

    def toJSON(self):
        return self.__dict__


class ArticleSearchResults(APIResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[Article] = []
