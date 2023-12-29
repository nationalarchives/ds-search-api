from abc import ABC, abstractmethod

import requests
from flask import current_app


class BaseAPI(ABC):
    @abstractmethod
    def get_results(self):
        pass


class GetAPI(BaseAPI):
    def __init__(self):
        self.filters = {}
        pass

    def add_parameter(self, key, value):
        self.filters[key] = value

    def execute(self, url):
        r = requests.get(url)
        if r.status_code == 404:
            current_app.logger.error(f"Resource not found: {url}")
            raise Exception("Resource not found")
            return {}
        if r.status_code == requests.codes.ok:
            try:
                return r.json()
            except requests.exceptions.JSONDecodeError:
                current_app.logger.error("API provided non-JSON response")
                raise ConnectionError("API provided non-JSON response")
        raise ConnectionError("Request to API failed")
