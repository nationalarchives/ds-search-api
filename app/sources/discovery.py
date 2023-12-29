import json

import requests
from app.records.schemas.record import Record
from app.records.schemas.records_response import RecordsResponse
from config import Config
from flask import current_app

from .api import GetAPI


class DiscoveryRecords(GetAPI):
    def __init__(self):
        self.api_url = Config().DISCOVERY_API_URL
        self.filters = {"sps.sortByOption": "RELEVANCE"}
        pass

    def add_query(self, query_string):
        self.add_parameter("sps.searchQuery", query_string)

    def build_query_string(self):
        print(self.filters)
        return "&".join(
            ["=".join((key, str(value))) for key, value in self.filters.items()]
        )

    def get_results(self, page=1):
        self.add_parameter("sps.page", page)
        url = f"{self.api_url}/records?{self.build_query_string()}"
        raw_results = self.execute(url)
        results = []
        for r in raw_results["records"]:
            record = Record()
            record.set_id(r["id"])
            record.set_ref(r["reference"])
            record.set_title(r["title"])
            results.append(record.toJSON())
        response = RecordsResponse()
        response.set_count(raw_results["count"])
        response.set_results(results)
        return response.toJSON()
