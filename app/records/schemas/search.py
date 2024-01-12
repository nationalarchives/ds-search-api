from app.schemas import APISearchResponse, APISearchResult
from pydantic import ConfigDict


class RecordSearchResult(APISearchResult):
    ref: str | None = None
    date: str | None = None
    held_by: str | None = None

    def __str__(self):
        return f"Record {self.id}"

    def toJSON(self):
        return self.__dict__


class RecordSearchResults(APISearchResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[RecordSearchResult] = []
