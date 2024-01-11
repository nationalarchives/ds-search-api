from app.records import router
from app.schemas import Filter
from app.sources.rosetta import RosettaRecords

from .schemas import RecordSearchResults


@router.get("/")
async def index(
    q: str = "",
    page: int | None = 1,
    group: str | None = None,
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecords()
    rosetta_api.add_query(q)
    if group:
        # group:(tna,digitised,nonTna,creator,archive)
        rosetta_api.add_parameter("filter", f"group:({group})")
    results = rosetta_api.get_results(page, highlight)
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
