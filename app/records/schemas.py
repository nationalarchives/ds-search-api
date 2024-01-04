from app.schemas import APIResponse, APIResult
from pydantic import ConfigDict


class Record(APIResult):
    ref: str | None = ""

    def __str__(self):
        return f"Record {self.id}"

    def toJSON(self):
        return self.__dict__


class RecordSearchResults(APIResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    count: int = 0
    results: list[Record] = []
