from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient


def assert_request_echo(data: dict[str, Any], payload: dict[str, Any]) -> None:
    assert data["name"] == payload["name"]
    assert data["birth_datetime"] == payload["birth_datetime"]
    assert data["location"] == payload["location"]
    assert data["settings"] == payload["settings"]


def assert_kp_position_row(row: dict[str, Any]) -> None:
    assert set(row) == {"label", "sign", "sign_index", "dms", "absolute_longitude", "kp"}
    assert isinstance(row["label"], str)
    assert isinstance(row["sign"], str)
    assert isinstance(row["sign_index"], int)
    assert isinstance(row["dms"], str)
    assert isinstance(row["absolute_longitude"], float)

    kp = row["kp"]
    assert set(kp) == {
        "deha_lord",
        "kp_number",
        "praana_lord",
        "rasi_lord",
        "sookshma_lord",
        "star_lord",
        "sub_lord",
        "sub_sub_lord",
    }
    assert isinstance(kp["kp_number"], int)
    assert all(isinstance(kp[key], str) for key in kp if key != "kp_number")


def assert_chart_planet(row: dict[str, Any]) -> None:
    assert set(row) == {
        "name",
        "short_name",
        "sign",
        "sign_index",
        "sign_number",
        "degree",
        "degree_decimal",
        "absolute_longitude",
        "state_flags",
    }
    assert isinstance(row["name"], str)
    assert isinstance(row["short_name"], str)
    assert isinstance(row["sign"], str)
    assert isinstance(row["sign_index"], int)
    assert isinstance(row["sign_number"], int)
    assert isinstance(row["degree"], str)
    assert isinstance(row["degree_decimal"], float)
    assert isinstance(row["absolute_longitude"], float)
    assert set(row["state_flags"]) == {
        "retrograde",
        "combust",
        "exalted",
        "debilitated",
    }


def test_health(client: Any) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_kp_chart_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    vj_chart_payload: dict[str, Any],
) -> None:
    data = post_json("/api/kp-details", vj_chart_payload)

    assert_request_echo(data, vj_chart_payload)
    assert len(data["cusps"]) == 12
    assert len(data["planets"]) >= 10
    assert all(item["label"] == f"House-{index}" for index, item in enumerate(data["cusps"], start=1))
    assert all(item["label"] for item in data["planets"])
    assert_kp_position_row(data["cusps"][0])
    assert_kp_position_row(data["planets"][0])

    ruling_planets = data["direct_ruling_planets"]
    assert set(ruling_planets) == {"items", "unique_planets"}
    assert len(ruling_planets["items"]) > 0
    assert len(ruling_planets["unique_planets"]) > 0


def test_d1_chart_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    vj_chart_payload: dict[str, Any],
) -> None:
    data = post_json("/api/chart/d-1", vj_chart_payload)

    assert_request_echo(data, vj_chart_payload)
    assert data["chart"] == "D-1"
    assert data["chart_style"] == "north_indian"
    assert set(data["ascendant"]) == {
        "sign",
        "sign_index",
        "sign_number",
        "degree",
        "degree_decimal",
        "absolute_longitude",
    }
    assert len(data["houses"]) == 12
    assert all(house["house_number"] == index for index, house in enumerate(data["houses"], start=1))
    assert all("planets" in house for house in data["houses"])


def test_transit_chart_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    vj_chart_payload: dict[str, Any],
) -> None:
    data = post_json("/api/chart/transit", vj_chart_payload)

    assert_request_echo(data, vj_chart_payload)
    assert data["chart"] == "Transit"
    assert data["chart_style"] == "north_indian"
    assert len(data["houses"]) == 12


def test_bhava_chalit_chart_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    vj_chart_payload: dict[str, Any],
) -> None:
    data = post_json("/api/chart/bhava-chalit", vj_chart_payload)

    assert_request_echo(data, vj_chart_payload)
    assert data["chart"] == "Bhava Chalit"
    assert data["chart_style"] == "north_indian"
    assert len(data["houses"]) == 12
    assert all(house["house_number"] == index for index, house in enumerate(data["houses"], start=1))
    assert all(set(house) == {"house_number", "display_number", "start", "cusp", "end", "planets"} for house in data["houses"])


def test_house_significators_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    vj_chart_payload: dict[str, Any],
) -> None:
    data = post_json("/api/kp/house-significators", vj_chart_payload)

    assert_request_echo(data, vj_chart_payload)
    assert len(data["houses"]) == 12
    for index, house in enumerate(data["houses"], start=1):
        assert house["house_number"] == index
        assert isinstance(house["source_sub_lord"], str)
        assert isinstance(house["source_sub_lord_short_name"], str)
        assert len(house["levels"]) > 0


def test_instant_prashna_shape(
    post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
    instant_prashna_payload: dict[str, Any],
) -> None:
    data = post_json("/api/kp/instant-prashna", instant_prashna_payload)

    assert data["mode"] == "instant_prashna"
    assert data["location"] == instant_prashna_payload["location"]
    assert data["settings"] == instant_prashna_payload["settings"]
    assert set(data["calculated_datetime"]) == {"year", "month", "day", "hour", "minute", "second"}
    assert len(data["kp_chart"]["cusps"]) == 12
    assert len(data["d1_chart"]["houses"]) == 12
    assert len(data["bhava_chalit_chart"]["houses"]) == 12
    assert len(data["house_significators"]["houses"]) == 12


def today_prediction_payload() -> dict[str, Any]:
    return {
        "asc_rashi_lord": {"planet": "Mo", "house": 5, "rashi": "Aries"},
        "moon_placement": {"planet": "Mo", "house": 5, "rashi": "Aries"},
        "moon_star_lord": {"planet": "Su", "house": 11, "rashi": "Libra"},
        "moon_rashi_lord": {"planet": "Ve", "house": 10, "rashi": "Virgo"},
        "day_lord": {"planet": "Ve", "house": 10, "rashi": "Virgo"},
        "transit_node_ke_in_base_rp_sign": {
            "planet": "Ke",
            "house": 8,
            "rashi": "Cancer",
        },
        "transit_node_ra_in_base_rp_sign": {
            "planet": "Ra",
            "house": 10,
            "rashi": "Capricorn",
        },
    }


def test_today_prediction_shape(client: TestClient, monkeypatch: Any) -> None:
    from app.models import TodayPredictionResponse

    def mock_prediction(_: Any) -> TodayPredictionResponse:
        return TodayPredictionResponse(prediction="Mocked AI response")

    monkeypatch.setattr("app.main.calculate_today_prediction_response", mock_prediction)

    response = client.post("/api/ai/today-prediction", json=today_prediction_payload())

    assert response.status_code == 200
    assert response.json() == {"prediction": "Mocked AI response"}


def test_today_prediction_rejects_invalid_rashi(client: TestClient) -> None:
    payload = today_prediction_payload()
    payload["transit_node_ra_in_base_rp_sign"]["rashi"] = "Capricon"

    response = client.post("/api/ai/today-prediction", json=payload)

    assert response.status_code == 422


def test_today_prediction_rejects_invalid_planet(client: TestClient) -> None:
    payload = today_prediction_payload()
    payload["transit_node_ra_in_base_rp_sign"]["planet"] = "Re"

    response = client.post("/api/ai/today-prediction", json=payload)

    assert response.status_code == 422


def test_today_prediction_accepts_missing_transit_nodes(
    client: TestClient,
    monkeypatch: Any,
) -> None:
    from app.models import TodayPredictionResponse

    def mock_prediction(_: Any) -> TodayPredictionResponse:
        return TodayPredictionResponse(prediction="Mocked AI response")

    monkeypatch.setattr("app.main.calculate_today_prediction_response", mock_prediction)
    payload = today_prediction_payload()
    del payload["transit_node_ke_in_base_rp_sign"]
    del payload["transit_node_ra_in_base_rp_sign"]

    response = client.post("/api/ai/today-prediction", json=payload)

    assert response.status_code == 200
    assert response.json() == {"prediction": "Mocked AI response"}
