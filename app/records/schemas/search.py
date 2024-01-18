from app.schemas import APISearchResponse, APISearchResult
from pydantic import ConfigDict


class RecordSearchResult(APISearchResult):
    type: str = ""
    ref: str | None = None
    date: str | None = None
    held_by: dict | None = None

    def __str__(self):
        return f"Record {self.id}"

    def toJSON(self):
        return self.__dict__


class RecordSearchResults(APISearchResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[RecordSearchResult] = []
    results_stats: dict = {
        "tna": None,
        "digitised": None,
        "nonTna": None,
        "creator": None,
        "archive": None,
    }
