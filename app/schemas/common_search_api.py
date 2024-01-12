import math

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict


class APISearchResult(BaseModel):
    title: str | None = None
    id: int | str = ""
    description: str | None = None

    def toJSON(self):
        return self.__dict__


class APISearchResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    count: int = 0
    page: int = 1
    pages: int = 1
    result_range_min: int = 0
    result_range_max: int = 0
    results_per_page: int = 0
    results: list[APISearchResult] = []

    def get_pages(self):
        return (
            math.ceil(self.count / self.results_per_page)
            if self.results_per_page
            else 0
        )

    def get_result_range_min(self):
        return (self.results_per_page * (self.page - 1)) + 1

    def get_result_range_max(self):
        page_max = self.results_per_page * self.page
        return page_max if page_max <= self.count else self.count

    def page_in_range(self):
        return self.get_pages() == 0 or (
            self.page > 0 and self.page <= self.get_pages()
        )

    def toJSON(self):
        if self.page_in_range():
            return self.__dict__ | {
                "pages": self.get_pages(),
                "result_range_min": self.get_result_range_min(),
                "result_range_max": self.get_result_range_max(),
                "foo": "bar",
                "results": [result.toJSON() for result in self.results],
            }
        raise HTTPException(
            status_code=404, detail=f"Page {self.page} out of range"
        )
