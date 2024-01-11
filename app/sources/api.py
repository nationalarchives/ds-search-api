import urllib.parse
from abc import ABC, abstractmethod

import requests


class BaseAPI(ABC):
    @abstractmethod
    def get_results(self):
        pass


class GetAPI(BaseAPI):
    results_per_page: int = 20
    params: dict = {}

    def add_parameter(self, key: str, value: str | int) -> None:
        self.params[key] = value

    def build_query_string(self) -> str:
        return (
            "?" + urllib.parse.urlencode(self.params)
            if len(self.params)
            else ""
        )

    def execute(self, url: str) -> dict:
        r = requests.get(url)
        if r.status_code == 404:
            raise Exception("Resource not found")
        if r.status_code == requests.codes.ok:
            try:
                return r.json()
            except requests.exceptions.JSONDecodeError:
                raise ConnectionError("API provided non-JSON response")
        raise ConnectionError("Request to API failed")
