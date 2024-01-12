from pydantic import BaseModel


class Details(BaseModel):
    type: str
    id: str = ""
    # dump: dict = {}  # TEMP

    def __init__(self, id: str):
        super().__init__()
        self.id = id

    def toJSON(self):
        return self.__dict__


class Record(Details):
    type: str = "record"
    ref: str | None = None
    title: str = ""
    date: str = ""
    is_digitised: bool | None = None

    def __init__(self, id: str):
        super().__init__(id)


class ExternalRecord(Details):
    type: str = "external_record"
    ref: str | None = None
    title: str = ""
    covering_date: str | None = None
    held_by: str | None = None

    def __init__(self, id: str):
        super().__init__(id)


class RecordCreator(Details):
    type: str = "creator"
    name: str = ""
    date: str = ""
    places: list[str] = []
    identifier: str = ""
    history: str = ""

    def __init__(self, id: str):
        super().__init__(id)


class RecordCreatorPerson(RecordCreator):
    type: str = "person"
    name_parts: dict = {}
    date: str = ""
    gender: str = ""
    functions: str = ""
    biography: str = ""

    def __init__(self, id: str):
        super().__init__(id)


class RecordArchive(Details):
    type: str = "archive"
    name: str = ""
    archon: str = ""
    places: list[str] = []
    agents: dict = {}
    contact_info: dict = {}

    def __init__(self, id: str):
        super().__init__(id)
