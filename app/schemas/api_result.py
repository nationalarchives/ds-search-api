from pydantic import BaseModel


class APIResult(BaseModel):
    def toJSON(self):
        return self.__dict__
