from pydantic import BaseModel, ConfigDict


class FilterOption(BaseModel):
    name: str = ""
    value: str | int = ""

    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value


class Filter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = ""
    type: str = ""
    options: list[FilterOption] = []

    def __init__(self, title, type):
        super().__init__()
        self.title = title
        self.type = type

    def add_filter_option(self, name, value):
        option = FilterOption(name, value)
        self.options.append(option)
