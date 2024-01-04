from pydantic import BaseModel


class APIResult(BaseModel):
    title: str | None = None
    id: int | str = ""
    description: str | None = None

    def toJSON(self):
        return self.__dict__
