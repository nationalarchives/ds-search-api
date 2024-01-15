from app.records import router
from app.schemas import Filter
from app.sources.rosetta import RosettaRecordDetails, RosettaRecordsSearch

from .schemas import Record, RecordArchive, RecordCreator, RecordSearchResults


@router.get("/")
async def index(
    q: str = "",
    page: int | None = 1,
    groups: str | None = None,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    if groups:
        # group:(tna,digitised,nonTna,creator,archive)
        rosetta_api.add_parameter("filter", f"group:({groups})")
    results = rosetta_api.get_result(page, highlight)
    return results


@router.get("/filters/")
async def filters() -> list[Filter]:
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


@router.get("/internal/")
async def internal(
    q: str = "",
    page: int | None = 1,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    rosetta_api.add_parameter("filter", "group:(tna)")
    results = rosetta_api.get_result(page, highlight)
    return results


@router.get("/external/")
async def external(
    q: str = "",
    page: int | None = 1,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    rosetta_api.add_parameter("filter", "group:(nonTna)")
    results = rosetta_api.get_result(page, highlight)
    return results


@router.get("/external/filters/")
async def external_filters() -> list[Filter]:
    filters = []
    return filters


@router.get("/creators/")
async def creators(
    q: str = "",
    page: int | None = 1,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    rosetta_api.add_parameter("filter", "group:(creator)")
    results = rosetta_api.get_result(page, highlight)
    return results


@router.get("/creators/filters/")
async def creators_filters() -> list[Filter]:
    filters = []
    return filters


@router.get("/archives/")
async def archives(
    q: str = "",
    page: int | None = 1,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    rosetta_api.add_parameter("filter", "group:(archive)")
    results = rosetta_api.get_result(page, highlight)
    return results


@router.get("/archives/filters/")
async def archives_filters() -> list[Filter]:
    filters = []
    return filters


@router.get("/{id}/")
async def item(
    id: str,
):  # ) -> Record | RecordCreator | RecordArchive:
    rosetta_api = RosettaRecordDetails()
    result = rosetta_api.get_result(id)
    return result
