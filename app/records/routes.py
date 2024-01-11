from app.records import router
from app.sources.rosetta import RosettaRecords

from .schemas import RecordSearchResults


@router.get("/")
async def index(
    q: str = "", page: int | None = 1, highlight: bool | None = False
) -> RecordSearchResults:
    rosetta_api = RosettaRecords()
    rosetta_api.add_query(q)
    print(highlight)
    results = rosetta_api.get_results(page, highlight)
    return results
