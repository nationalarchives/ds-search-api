from app.schemas import APIResponse, APIResult
from pydantic import ConfigDict


class Record(APIResult):
    ref: str | None = None
    covering_date: str | None = None
    held_by: str | None = None

    def __str__(self):
        return f"Record {self.id}"

    def toJSON(self):
        return self.__dict__


class RecordSearchResults(APIResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    results: list[Record] = []
