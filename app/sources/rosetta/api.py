from app.lib.api import GetAPI
from app.records.schemas import (
    Aggregation,
    Record,
    RecordArchive,
    RecordCreator,
    RecordCreatorPerson,
    RecordSearchResult,
    RecordSearchResults,
)
from config import Config

from .lib import RosettaResponseParser, RosettaSourceParser


class RosettaRecords(GetAPI):
    api_base_url = Config().ROSETTA_API_URL


class RosettaRecordsSearch(RosettaRecords):
    def __init__(self):
        super().__init__()
        self.api_path = "/search"
        self.add_parameter("includeSource", True)

    def add_query(self, query_string: str) -> None:
        self.add_parameter("q", query_string)

    def get_result(
        self, page: int | None = 1, highlight: bool | None = False
    ) -> dict:
        offset = (page - 1) * self.results_per_page
        self.add_parameter("size", self.results_per_page)
        self.add_parameter("from", offset)
        url = self.build_url()
        raw_results = self.execute(url)
        return self.parse_results(raw_results, page, url)

    def parse_results(self, raw_results, page, source_url) -> dict:
        response = RecordSearchResults()
        response.source_url = source_url
        for r in raw_results["metadata"]:
            parsed_data = RosettaSourceParser(r["_source"])
            record = RecordSearchResult()
            type = parsed_data.type()
            if type == "repository":
                type = "archive"
            if type == "agent":
                type = "creator"
                if parsed_data.actual_type() == "person":
                    type = "person"
            record.type = type
            record.id = parsed_data.id()
            record.ref = parsed_data.reference_number()
            record.title = parsed_data.title()
            record.description = parsed_data.description()
            record.date = parsed_data.date()
            record.held_by = parsed_data.held_by()
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


class RosettaRecordDetails(RosettaRecords):
    def __init__(self):
        super().__init__()
        self.api_path = "/fetch"

    def get_result(self, id: str) -> dict:
        self.add_parameter("id", id)
        self.add_parameter("includeSource", True)
        url = self.build_url()
        raw_results = self.execute(url)
        return self.parse_results(raw_results, url)

    def parse_results(self, raw_results, source_url):
        parsed_data = RosettaResponseParser(raw_results)
        if parsed_data.type() == "record":
            record = Record(parsed_data.id())
            record.ref = parsed_data.identifier()
            record.iaid = parsed_data.iaid()
            record.former_ref = parsed_data.former_identifier()
            record.title = parsed_data.title()
            record.description = parsed_data.description()
            record.date = parsed_data.date_range()
            record.is_digitised = parsed_data.is_digitised()
            record.held_by = parsed_data.held_by()
            record.legal_status = parsed_data.legal_status()
            record.closure_status = parsed_data.closure_status()
            record.access_condition = parsed_data.access_condition()
            record.languages = parsed_data.languages()
            record.hierarchy = (
                parsed_data.hierarchies()[0]
                if len(parsed_data.hierarchies())
                else []
            )
            record.source_url = source_url
            return record.toJSON()
        if parsed_data.type() == "aggregation":
            record = Aggregation(parsed_data.id())
            record.ref = parsed_data.identifier()
            record.iaid = parsed_data.iaid()
            record.title = parsed_data.title()
            record.description = parsed_data.description()
            record.physical_description = parsed_data.physical_description()
            record.administrative_background = (
                parsed_data.administrative_background()
            )
            record.arrangement = parsed_data.arrangement()
            record.date = parsed_data.date_range()
            record.is_digitised = parsed_data.is_digitised()
            record.held_by = parsed_data.held_by()
            record.creators = parsed_data.creators()
            record.acquisition = parsed_data.acquisition()
            record.unpublished_finding_aids = (
                parsed_data.unpublished_finding_aids()
            )
            record.legal_status = parsed_data.legal_status()
            record.closure_status = parsed_data.closure_status()
            record.access_condition = parsed_data.access_condition()
            record.languages = parsed_data.languages()
            record.hierarchy = (
                parsed_data.hierarchies()[0]
                if len(parsed_data.hierarchies())
                else []
            )
            record.source_url = source_url
            return record.toJSON()
        if (
            parsed_data.type() == "archive"
            or parsed_data.type() == "repository"
        ):
            record = RecordArchive(parsed_data.id())
            record.name = parsed_data.title()
            record.archon_code = parsed_data.reference_number()
            record.opening_times = parsed_data.place_opening_times()
            record.disabled_access = parsed_data.place_disabled_access()
            record.information = parsed_data.place_comments()
            record.fee = parsed_data.place_fee()
            record.appointment = parsed_data.place_appointment()
            record.places = parsed_data.places()
            record.contact_info = parsed_data.contact_info()
            record.agents = parsed_data.agents()
            record.manifestations = parsed_data.manifestations()
            record.accumulation_dates = parsed_data.accumulation_dates()
            record.source_url = source_url
            return record.toJSON()
        if parsed_data.type() == "agent":
            if parsed_data.actual_type() == "person":
                record = RecordCreatorPerson(parsed_data.id())
                record.name = parsed_data.name()
                record.name_parts = parsed_data.names()
                record.date = parsed_data.date()
                record.gender = parsed_data.gender()
                record.identifier = parsed_data.identifier()
                record.functions = parsed_data.functions()
                record.history = parsed_data.functions()
                record.biography = parsed_data.biography()
                record.source_url = source_url
                return record.toJSON()
            record = RecordCreator(parsed_data.id())
            record.name = parsed_data.title()
            record.date = parsed_data.date()
            record.places = parsed_data.places()
            record.identifier = parsed_data.identifier()
            record.history = parsed_data.functions()
            record.source_url = source_url
            return record.toJSON()
        raise Exception(
            f"Respone type '{parsed_data.type()}' is not recognised"
        )
