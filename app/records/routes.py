from app.records import router
from app.sources import DiscoveryRecords

from .schemas import RecordsResponse


@router.get("/")
def index(q: str | None = "*", page: int | None = 1) -> RecordsResponse:
    discovery_api = DiscoveryRecords()
    discovery_api.add_query(q or "*")
    results = discovery_api.get_results(page)
    return results
