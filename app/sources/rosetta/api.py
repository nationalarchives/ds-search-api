from app.lib.api import GetAPI
from app.records.schemas import (
    Record,
    RecordArchive,
    RecordCreator,
    RecordCreatorPerson,
    RecordSearchResult,
    RecordSearchResults,
)
from app.schemas import Filter

from app import get_config

from .lib import RosettaResponseParser, RosettaSourceParser

# from pydash import objects


class RosettaRecords(GetAPI):
    api_base_url = get_config().ROSETTA_API_URL


class RosettaRecordsSearch(RosettaRecords):
    def __init__(self):
        super().__init__()
        self.api_path = "/search"
        self.add_parameter("includeSource", True)

    def add_query(self, query_string: str) -> None:
        self.add_parameter("q", query_string)

    def filters(self) -> list[Filter]:
        filters = []

        refine_filter = Filter("Refine results", "text")
        filters.append(refine_filter)

        covering_date_filter = Filter("Covering date", "daterange")
        filters.append(covering_date_filter)

        collections_filter = Filter("Collections", "multiple")
        collections_filter.add_filter_option(
            "Admiralty, Navy, Royal Marines, and Coastguard", "0"
        )
        collections_filter.add_filter_option(
            "Air Ministry and Royal Air Force records", "1"
        )
        filters.append(collections_filter)

        level_filter = Filter("Level", "multiple")
        level_filter.add_filter_option("Division", "0")
        level_filter.add_filter_option("Item", "1")
        filters.append(level_filter)

        return filters

    def get_result(
        self, page: int | None = 1, highlight: bool | None = False
    ) -> dict:
        offset = (page - 1) * self.results_per_page
        self.add_parameter("size", self.results_per_page)
        self.add_parameter("from", offset)
        url = self.build_url()
        print(url)
        raw_results = self.execute(url)
        results = self.parse_results(raw_results, page, url, highlight)
        # TODO: Can we get aggregated stats?
        # stats_api = RosettaRecordsSearchStats(self.params["q"])
        # results_stats = stats_api.get_result()
        # results.results_stats = results_stats
        results.filters = self.filters()
        return results.toJSON() if results.page_in_range() else {}

    def parse_results(
        self,
        raw_results: dict,
        page: int,
        source_url: str,
        highlight: bool | None = False,
    ) -> RecordSearchResults:
        response = RecordSearchResults()
        response.source_url = source_url
        for r in raw_results["metadata"]:
            parsed_data = RosettaSourceParser(r)
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
            record.title = parsed_data.title(highlight)
            record.description = parsed_data.description(highlight)
            record.date_from = parsed_data.date_from()
            record.date_to = parsed_data.date_to()
            record.held_by = parsed_data.held_by()
            response.results.append(record)
        response.count = (
            raw_results["stats"]["total"]
            if raw_results["stats"]["total"] <= 10000
            else 10000
        )
        response.results_per_page = self.results_per_page
        response.page = page
        return response


# class RosettaRecordsSearchStats(RosettaRecords):
#     def __init__(self, query_string):
#         super().__init__()
#         self.api_path = "/search"
#         self.add_parameter("q", query_string)

#     def get_result(self) -> dict:
#         stats = {
#             "tna": None,
#             "digitised": None,
#             "nonTna": None,
#             "creator": None,
#             "archive": None,
#         }
#         for group in stats:
#             self.add_parameter("filter", f"group:({group})")
#             url = self.build_url()
#             # print(url)
#             raw_results = self.execute(url)
#             # print(url)
#             results_count = objects.get(raw_results, "stats.total")
#             stats[group] = results_count
#         return stats


class RosettaRecordsSearchAll(RosettaRecords):
    def __init__(self):
        super().__init__()
        self.api_path = "/searchAll"


class RosettaRecordDetails(RosettaRecords):
    def __init__(self):
        super().__init__()
        self.api_path = "/fetch"

    def get_result(self, id: str) -> dict:
        self.add_parameter("id", id)
        self.add_parameter("includeSource", True)
        url = self.build_url()
        print(url)
        raw_results = self.execute(url)
        return self.parse_results(raw_results, url)

    def parse_results(self, raw_results, source_url):
        try:
            parsed_data = RosettaResponseParser(raw_results)
        except Exception:
            raise Exception("Response is not recognised")
        if (
            parsed_data.type() == "record"
            or parsed_data.type() == "aggregation"
        ):
            record = Record(parsed_data.id())
            record.identifier = parsed_data.identifier()
            record.former_identifier = parsed_data.former_identifier()
            record.title = parsed_data.title()
            record.summary_title = parsed_data.summary_title()
            record.description = parsed_data.description()
            record.physical_description = parsed_data.physical_description()
            record.administrative_background = (
                parsed_data.administrative_background()
            )
            record.arrangement = parsed_data.arrangement()
            record.date_from = parsed_data.date_from()
            record.date_to = parsed_data.date_to()
            record.is_digitised = parsed_data.is_digitised()
            record.held_by = parsed_data.held_by()
            record.creators = parsed_data.creators()
            record.acquisition = parsed_data.acquisition()
            record.legal_status = parsed_data.legal_status()
            record.closure_status = parsed_data.closure_status()
            record.access_condition = parsed_data.access_condition()
            record.notes = parsed_data.notes()
            record.unpublished_finding_aids = (
                parsed_data.unpublished_finding_aids()
            )
            record.languages = parsed_data.languages()
            record.related_materials = parsed_data.related_materials()
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
            record.repository_url = parsed_data.repository_url()
            record.opening_times = parsed_data.place_opening_times()
            record.holidays = parsed_data.place_holidays()
            record.disabled_access = parsed_data.place_disabled_access()
            record.information = parsed_data.place_comments()
            record.fees = parsed_data.place_fee()
            record.tickets = parsed_data.place_tickets()
            record.appointments = parsed_data.place_appointment()
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
                record.identifier = parsed_data.identifier()
                record.former_identifier = parsed_data.former_identifier()
                record.date = parsed_data.date()
                record.birth = parsed_data.date_from()
                record.death = parsed_data.date_to()
                record.gender = parsed_data.gender()
                record.functions = parsed_data.functions()
                record.history = parsed_data.functions()
                record.biography = parsed_data.biography()
                record.source_url = source_url
                return record.toJSON()
            record = RecordCreator(parsed_data.id())
            record.name = parsed_data.title()
            record.identifier = parsed_data.identifier()
            record.former_identifier = parsed_data.former_identifier()
            record.date_from = parsed_data.date_from()
            record.date_to = parsed_data.date_to()
            record.places = parsed_data.places()
            record.identifier = parsed_data.identifier()
            record.history = parsed_data.functions()
            record.source_url = source_url
            return record.toJSON()
        raise Exception(
            f"Respone type '{parsed_data.type()}' is not recognised"
        )
