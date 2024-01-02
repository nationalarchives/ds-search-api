from app.schemas import APIResponse, APIResult
from pydantic import ConfigDict


class Article(APIResult):
    title: str = ""
    url: str = ""
    type: str = ""
    id: int = 0
    first_published: str = ""

    def __str__(self):
        return f"Article {self.title}"

    def toJSON(self):
        return self.__dict__


class ArticleSearchResults(APIResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    count: int = 0
    results: list[Article] = []
