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
    iaid: str | None = None
    former_ref: str | None = None
    title: str | None = None
    summary_title: str | None = None
    description: str | None = None
    date: str | None = None
    is_digitised: bool | None = None
    held_by: dict = {}
    legal_status: str | None = None
    closure_status: str | None = None
    access_condition: str | None = None
    languages: list[str] = []
    related_materials: list[dict] = []
    hierarchy: list[dict] = []

    def __init__(self, id: str):
        super().__init__(id)


class Aggregation(Details):
    type: str = "aggregation"
    ref: str | None = None
    iaid: str | None = None
    title: str | None = None
    summary_title: str | None = None
    description: str | None = None
    physical_description: str | None = None
    administrative_background: str | None = None
    arrangement: str | None = None
    date: str | None = None
    is_digitised: bool | None = None
    held_by: dict = {}
    creators: list[dict] = []
    acquisition: list[dict] = []
    unpublished_finding_aids: str | None = None
    legal_status: str | None = None
    closure_status: str | None = None
    access_condition: str | None = None
    languages: list[str] = []
    related_materials: list[dict] = []
    hierarchy: list[dict] = []

    def __init__(self, id: str):
        super().__init__(id)


class RecordCreator(Details):
    type: str = "creator"
    name: str | None = None
    date: str | None = None
    places: list[str] = []
    identifier: str | None = None
    history: str | None = None

    def __init__(self, id: str):
        super().__init__(id)


class RecordCreatorPerson(RecordCreator):
    type: str = "person"
    name_parts: dict = {}
    date: str | None = None
    gender: str | None = None
    functions: str | None = None
    biography: str | None = None

    def __init__(self, id: str):
        super().__init__(id)


class RecordArchive(Details):
    type: str = "archive"
    name: str | None = None
    archon_code: str | None = None
    repository_url: str | None = None
    opening_times: str | None = None
    holidays: str | None = None
    disabled_access: str | None = None
    information: str | None = None
    fees: str | None = None
    tickets: str | None = None
    appointments: str | None = None
    contact_info: dict = {}
    places: list[str] = []
    accumulation_dates: list[str] = []
    agents: dict = {}
    manifestations: list[dict] = []

    def __init__(self, id: str):
        super().__init__(id)
