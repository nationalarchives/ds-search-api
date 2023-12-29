import json


class Record:
    def __init__(self):
        self.id = ""
        self.ref = ""
        self.title = ""

    def set_id(self, id):
        self.id = id

    def set_ref(self, ref):
        self.ref = ref

    def set_title(self, title):
        self.title = title

    def __str__(self):
        return f"Record {self.id}"

    def toJSON(self):
        return self.__dict__
