from app.records import router
from app.sources.discovery import DiscoveryRecords

from .schemas import RecordSearchResults


@router.get("/")
async def index(
    q: str | None = "*", page: int | None = 1
) -> RecordSearchResults:
    discovery_api = DiscoveryRecords()
    discovery_api.add_query(q or "*")
    results = discovery_api.get_results(page)
    return results
