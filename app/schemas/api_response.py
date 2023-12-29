class APIResponse:
    def __init__(self):
        self.count = 0
        self.results = ""

    def set_count(self, count):
        self.count = count

    def set_results(self, results):
        self.results = results

    def toJSON(self):
        return self.__dict__
