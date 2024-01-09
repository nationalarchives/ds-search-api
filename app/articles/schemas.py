from app.schemas import APIResponse, APIResult
from pydantic import BaseModel, ConfigDict


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

    count: int = 0
    pages: int = 0
    results: list[Article] = []


class ArticleFilterOption(BaseModel):
    name: str = ""
    value: str | int = ""

    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value


class ArticleFilter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    options: list[ArticleFilterOption] = []

    def __init__(self, title):
        super().__init__()
        self.title = title

    def add_filter_option(self, name, value):
        option = ArticleFilterOption(name, value)
        self.options.append(option)
