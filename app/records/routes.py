from app.records import router
from app.schemas import Filter
from app.sources.rosetta import (
    RosettaRecordDetails,
    RosettaRecordsSearch,
    RosettaRecordsSearchStats,
)
from fastapi import HTTPException

from .schemas import Record, RecordArchive, RecordCreator, RecordSearchResults


@router.get("/")
async def index(
    q: str = "",
    page: int | None = 1,
    groups: str | None = None,  # group:(tna,digitised,nonTna,creator,archive)
    highlight: bool | None = False,
) -> RecordSearchResults:
    rosetta_api = RosettaRecordsSearch()
    rosetta_api.add_query(q)
    rosetta_api.add_parameter("filter", f"group:({groups})" if groups else "")
    results = rosetta_api.get_result(page, highlight)
    return results


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


@router.get("/{id}/")
async def item(
    id: str,
):  # ) -> Record | RecordCreator | RecordArchive:
    rosetta_api = RosettaRecordDetails()
    try:
        result = rosetta_api.get_result(id)
    except Exception:
        raise HTTPException(status_code=404, detail="Record not found")
    return result
