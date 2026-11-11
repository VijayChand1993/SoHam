from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from threading import Lock

from jhora import const, place_db
from kp_core import Location

from app.models import LocationRequest, PlaceSearchResult


_PLACE_SEARCH_ENGINE = const.PLACE_DATABASE_ENGINE.CSV_5K
_PLACE_DB_LOCK = Lock()
_place_db_initialized = False


def _ensure_place_database_loaded() -> None:
    global _place_db_initialized

    if _place_db_initialized:
        return

    with _PLACE_DB_LOCK:
        if _place_db_initialized:
            return

        const.set_place_database_engine(_PLACE_SEARCH_ENGINE)
        place_db.set_auto_download_place_database(False)

        output_buffer = StringIO()
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            place_db.use_database_for_world_cities(True)

        _place_db_initialized = True


def _record_to_place_result(record: dict) -> PlaceSearchResult:
    return PlaceSearchResult(
        display_name=record.get("display_label") or record.get("name", ""),
        city=record.get("city_name", ""),
        state=record.get("state", ""),
        country=record.get("country", ""),
        latitude=float(record["latitude"]),
        longitude=float(record["longitude"]),
        timezone=float(record["timezone"]),
        elevation=float(record.get("elevation", 0.0)),
        source=record.get("source", "pyjhora"),
    )


def search_places(query: str, limit: int = 10) -> list[PlaceSearchResult]:
    normalized_query = query.strip()
    if not normalized_query:
        return []

    safe_limit = max(1, min(limit, 25))
    _ensure_place_database_loaded()

    output_buffer = StringIO()
    with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
        matches = place_db.search_places_contains(normalized_query, safe_limit * 3)

    results: list[PlaceSearchResult] = []
    seen: set[tuple[str, float, float]] = set()

    for match in matches:
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            record = place_db.get_location_record(match)
        if not record:
            continue

        result = _record_to_place_result(record)
        dedupe_key = (
            result.display_name,
            round(result.latitude, 4),
            round(result.longitude, 4),
        )
        if dedupe_key in seen:
            continue

        results.append(result)
        seen.add(dedupe_key)
        if len(results) >= safe_limit:
            break

    return results


def to_core_location(location: LocationRequest) -> Location:
    return Location(**location.model_dump())
