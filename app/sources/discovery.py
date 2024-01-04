from app.records.schemas import Record, RecordSearchResults
from config import Config

from .api import GetAPI


class DiscoveryRecords(GetAPI):
    def __init__(self):
        self.api_url = Config().DISCOVERY_API_URL
        self.add_parameter("sps.sortByOption", "RELEVANCE")

    def add_query(self, query_string: str) -> None:
        self.add_parameter("sps.searchQuery", query_string)

    def get_results(self, page: int | None = 1) -> dict:
        self.add_parameter("sps.page", page)
        self.add_parameter("sps.resultsPageSize", self.results_per_page)
        url = f"{self.api_url}/records{self.build_query_string()}"
        raw_results = self.execute(url)
        response = RecordSearchResults()
        for r in raw_results["records"]:
            record = Record()
            record.id = r["id"]
            record.ref = r["reference"]
            record.title = r["title"]
            response.results.append(record)
        response.count = raw_results["count"]
        return response.toJSON()
