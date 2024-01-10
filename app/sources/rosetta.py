import math

from app.records.schemas import Record, RecordSearchResults
from config import Config

from .api import GetAPI


class RosettaRecords(GetAPI):
    def __init__(self):
        self.api_url = Config().ROSETTA_API_URL

    def add_query(self, query_string: str) -> None:
        self.add_parameter("q", query_string)

    def get_results(self, page: int | None = 1) -> dict:
        offset = (page - 1) * self.results_per_page
        self.add_parameter("size", self.results_per_page)
        self.add_parameter("from", offset)
        url = f"{self.api_url}/search{self.build_query_string()}"
        raw_results = self.execute(url)
        response = RecordSearchResults()
        print(url)
        for r in raw_results["metadata"]:
            record = Record()
            record.id = r["id"]
            record.ref = (
                r["detail"]["@template"]["details"]["referenceNumber"]
                if "referenceNumber" in r["detail"]["@template"]["details"]
                else None
            )
            record.title = r["summaryTitle"]
            response.results.append(record)
        response.count = raw_results["stats"]["total"]
        response.results_per_page = self.results_per_page
        response.page = page
        return (
            response.toJSON() if response.page_in_range() else {"None": "None"}
        )
