from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app


_REFERENCE_RESULTS: list[dict[str, str]] = []


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--show-kp-mismatches",
        action="store_true",
        default=False,
        help="Show detailed field mismatches for KP golden percentage tests.",
    )


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def vj_chart_payload() -> dict[str, Any]:
    return {
        "name": "VJ",
        "birth_datetime": {
            "year": 1989,
            "month": 10,
            "day": 8,
            "hour": 19,
            "minute": 4,
            "second": 0,
        },
        "location": {
            "name": "Manual coordinates",
            "latitude": 18.102,
            "longitude": 79.3666666667,
            "timezone": 5.5,
            "elevation": 0,
        },
        "settings": {
            "ayanamsa_mode": "KP",
            "house_cusp_method": 3,
            "use_true_nodes": False,
            "include_western_planets": False,
        },
    }


@pytest.fixture
def vijay_chand_paid_reference_payload() -> dict[str, Any]:
    return {
        "name": "Vijay Chand",
        "birth_datetime": {
            "year": 1993,
            "month": 4,
            "day": 2,
            "hour": 1,
            "minute": 15,
            "second": 0,
        },
        "location": {
            "name": "Pithoragarh",
            "latitude": 29 + 35 / 60 + 1 / 3600,
            "longitude": 80 + 12 / 60 + 34 / 3600,
            "timezone": 5.5,
            "elevation": 0,
        },
        "settings": {
            "ayanamsa_mode": "KP",
            "house_cusp_method": 3,
            "use_true_nodes": True,
            "include_western_planets": False,
        },
    }


@pytest.fixture
def test003_paid_reference_payload() -> dict[str, Any]:
    return {
        "name": "Test003",
        "birth_datetime": {
            "year": 1974,
            "month": 11,
            "day": 16,
            "hour": 22,
            "minute": 10,
            "second": 0,
        },
        "location": {
            "name": "Manual coordinates",
            "latitude": 29 + 59 / 60,
            "longitude": 76 + 51 / 60,
            "timezone": 5.5,
            "elevation": 0,
        },
        "settings": {
            "ayanamsa_mode": "KP",
            "house_cusp_method": 3,
            "use_true_nodes": True,
            "include_western_planets": False,
        },
    }


@pytest.fixture
def test004_paid_reference_payload() -> dict[str, Any]:
    return {
        "name": "Test004",
        "birth_datetime": {
            "year": 2026,
            "month": 7,
            "day": 29,
            "hour": 14,
            "minute": 12,
            "second": 41,
        },
        "location": {
            "name": "Hyderabad",
            "latitude": 17 + 23 / 60 + 3 / 3600,
            "longitude": 78 + 27 / 60 + 23 / 3600,
            "timezone": 5.5,
            "elevation": 0,
        },
        "settings": {
            "ayanamsa_mode": "KP",
            "house_cusp_method": 3,
            "use_true_nodes": True,
            "include_western_planets": True,
        },
    }


@pytest.fixture
def instant_prashna_payload(vj_chart_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "location": deepcopy(vj_chart_payload["location"]),
        "settings": deepcopy(vj_chart_payload["settings"]),
    }


@pytest.fixture
def post_json(client: TestClient) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    def _post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = client.post(path, json=payload)
        assert response.status_code == 200, response.text
        return response.json()

    return _post_json


@pytest.fixture
def record_reference_result() -> Callable[[str, bool, int, int, float, float, str], None]:
    def _record(
        title: str,
        passed: bool,
        matched: int,
        compared: int,
        percentage: float,
        threshold: float,
        ignored: str,
        mismatches: list[str] | None = None,
    ) -> None:
        _REFERENCE_RESULTS.append(
            {
                "test": title,
                "status": "PASS" if passed else "FAIL",
                "matched": f"{matched}/{compared}",
                "match": f"{percentage:.2f}%",
                "threshold": f"{threshold:.2f}%",
                "ignored": ignored,
                "mismatches": "\n".join(mismatches or []),
            }
        )

    return _record


@pytest.fixture
def show_kp_mismatches(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--show-kp-mismatches"))


def pytest_terminal_summary(terminalreporter: Any) -> None:
    if not _REFERENCE_RESULTS:
        return

    headers = ["Test", "Status", "Matched", "Match", "Threshold", "Ignored"]
    rows = [
        [
            result["test"],
            result["status"],
            result["matched"],
            result["match"],
            result["threshold"],
            result["ignored"],
        ]
        for result in _REFERENCE_RESULTS
    ]
    widths = [
        max(len(str(row[index])) for row in [headers, *rows])
        for index in range(len(headers))
    ]

    def format_row(row: list[str]) -> str:
        return " | ".join(value.ljust(width) for value, width in zip(row, widths))

    terminalreporter.write_sep("-", "KP Golden Match Summary")
    terminalreporter.write_line(format_row(headers))
    terminalreporter.write_line("-+-".join("-" * width for width in widths))
    for row in rows:
        terminalreporter.write_line(format_row(row))

    if not terminalreporter.config.getoption("--show-kp-mismatches"):
        return

    mismatch_results = [
        result for result in _REFERENCE_RESULTS if result.get("mismatches")
    ]
    if not mismatch_results:
        return

    terminalreporter.write_sep("-", "KP Golden Mismatches")
    for result in mismatch_results:
        terminalreporter.write_line(result["test"])
        terminalreporter.write_line(result["mismatches"])
