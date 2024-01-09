from pydantic import BaseModel, ConfigDict

from .api_result import APIResult


class APIResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    count: int = 0
    pages: int = 0
    results: list[APIResult] = []

    def toJSON(self):
        return self.__dict__ | {
            "results": [result.toJSON() for result in self.results]
        }
