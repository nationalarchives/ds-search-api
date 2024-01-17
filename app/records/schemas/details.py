from pydantic import BaseModel


class Details(BaseModel):
    type: str
    id: str = ""
    # dump: dict = {}  # TEMP
    source_url: str = ""

    def __init__(self, id: str):
        super().__init__()
        self.id = id

    def toJSON(self):
        return self.__dict__


class Record(Details):
    type: str = "record"
    ref: str | None = None
    former_ref: str | None = None
    title: str = ""
    description: str = ""
    date: str = ""
    is_digitised: bool | None = None
    held_by: dict | None = None
    legal_status: str | None = None
    closure_status: str | None = None
    access_condition: str | None = None
    languages: list[str] | None = None

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
    archon_code: str = ""
    opening_times: str = ""
    disabled_access: str = ""
    information: str = ""
    fee: str = ""
    appointment: str = ""
    contact_info: dict = {}
    places: list[str] = []
    accumulation_dates: list[str] = []
    agents: dict = {}
    manifestations: list[dict] = []

    def __init__(self, id: str):
        super().__init__(id)
