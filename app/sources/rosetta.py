import math

from app.records.schemas import Record, RecordSearchResults
from config import Config

from .api import GetAPI


class RosettaRecords(GetAPI):
    def __init__(self):
        self.api_url = Config().ROSETTA_API_URL

    def add_query(self, query_string: str) -> None:
        self.add_parameter("q", query_string)

    def get_results(
        self, page: int | None = 1, highlight: bool | None = False
    ) -> dict:
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
            details = r["detail"]["@template"]["details"]
            record.ref = (
                details["referenceNumber"]
                if "referenceNumber" in details
                else None
            )
            record.title = (
                details["summaryTitle"] if "summaryTitle" in details else None
            )
            record.description = (
                details["description"][0] if "description" in details else None
            )
            record.covering_date = (
                details["dateCovering"] if "dateCovering" in details else None
            )
            record.held_by = details["heldBy"] if "heldBy" in details else None
            # if highlight and "highLight" in r:
            #     if "@template.details.summaryTitle" in r["highLight"]:
            #         record.title = r["highLight"]["@template.details.summaryTitle"][0]
            #     if "@template.details.description" in r["highLight"]:
            #         record.title = r["highLight"]["@template.details.description"][0]
            response.results.append(record)
        response.count = (
            raw_results["stats"]["total"]
            if raw_results["stats"]["total"] <= 10000
            else 10000
        )
        response.results_per_page = self.results_per_page
        response.page = page
        return response.toJSON() if response.page_in_range() else {}
