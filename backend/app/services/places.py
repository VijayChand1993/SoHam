from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from math import asin, cos, radians, sin, sqrt
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


def _distance_km(
    latitude: float,
    longitude: float,
    other_latitude: float,
    other_longitude: float,
) -> float:
    earth_radius_km = 6371.0088
    lat1 = radians(latitude)
    lat2 = radians(other_latitude)
    delta_lat = radians(other_latitude - latitude)
    delta_lon = radians(other_longitude - longitude)
    haversine = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(haversine))


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


def nearest_place(latitude: float, longitude: float) -> tuple[PlaceSearchResult, float]:
    _ensure_place_database_loaded()

    records = getattr(place_db, "_backend").records
    if not records:
        raise ValueError("Place database is not loaded.")

    nearest_record = None
    nearest_distance = float("inf")

    for record in records:
        try:
            record_latitude = float(record["latitude"])
            record_longitude = float(record["longitude"])
        except (KeyError, TypeError, ValueError):
            continue

        distance = _distance_km(
            latitude,
            longitude,
            record_latitude,
            record_longitude,
        )
        if distance < nearest_distance:
            nearest_record = record
            nearest_distance = distance

    if nearest_record is None:
        raise ValueError("No place records are available.")

    return _record_to_place_result(nearest_record), nearest_distance


def to_core_location(location: LocationRequest) -> Location:
    return Location(**location.model_dump())
