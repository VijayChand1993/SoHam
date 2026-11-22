from collections.abc import Callable
from typing import Any

import pytest


def kp_rows_match_percentage(
    rows: list[dict[str, Any]],
    expected_rows: list[tuple[str, str, str, str, str, str, str]],
    ignored_fields: set[str],
) -> tuple[int, int, float, list[str]]:
    compared = 0
    matched = 0
    mismatches = []
    field_getters = [
        ("label", lambda row: row["label"]),
        ("sign", lambda row: row["sign"]),
        ("dms", lambda row: row["dms"]),
        ("rasi_lord", lambda row: row["kp"]["rasi_lord"]),
        ("star_lord", lambda row: row["kp"]["star_lord"]),
        ("sub_lord", lambda row: row["kp"]["sub_lord"]),
        ("sub_sub_lord", lambda row: row["kp"]["sub_sub_lord"]),
    ]

    for row, (label, sign, dms, rasi_lord, star_lord, sub_lord, sub_sub_lord) in zip(
        rows,
        expected_rows,
        strict=True,
    ):
        expected_by_field = {
            "label": label,
            "sign": sign,
            "dms": dms,
            "rasi_lord": rasi_lord,
            "star_lord": star_lord,
            "sub_lord": sub_lord,
            "sub_sub_lord": sub_sub_lord,
        }

        row_label = expected_by_field["label"]
        for field_name, field_getter in field_getters:
            if field_name in ignored_fields:
                continue
            compared += 1
            actual = field_getter(row)
            expected = expected_by_field[field_name]
            if actual == expected:
                matched += 1
                continue
            mismatches.append(
                f"{row_label}.{field_name}: expected={expected!r}, actual={actual!r}"
            )

    percentage = matched / compared * 100
    return matched, compared, percentage, mismatches


def assert_paid_reference_match_percentage(
    rows: list[dict[str, Any]],
    expected_rows: list[tuple[str, str, str, str, str, str, str]],
    *,
    title: str,
    record_reference_result: Callable[
        [str, bool, int, int, float, float, str, list[str] | None],
        None,
    ],
    show_kp_mismatches: bool,
    ignored_fields: set[str] | None = None,
    minimum_percentage: float = 85.0,
) -> None:
    ignored_fields = ignored_fields or set()
    matched, compared, percentage, mismatches = kp_rows_match_percentage(
        rows,
        expected_rows,
        ignored_fields,
    )
    passed = percentage >= minimum_percentage
    record_reference_result(
        title,
        passed,
        matched,
        compared,
        percentage,
        minimum_percentage,
        ", ".join(sorted(ignored_fields)) if ignored_fields else "-",
        mismatches if show_kp_mismatches else None,
    )
    assert passed, (
        f"{title} failed: matched {matched}/{compared} values "
        f"({percentage:.2f}%), threshold {minimum_percentage:.2f}%."
    )


@pytest.mark.golden
class Test001:
    @pytest.mark.cuspal
    def test_cuspal_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        vj_chart_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", vj_chart_payload)

        expected_cusps = [
            ("House-1", "♈Aries", "13:22:28", "Mars♂", "Venus♀", "Venus♀", "Venus♀"),
            ("House-2", "♉︎Taurus", "13:10:09", "Venus♀", "Moon☾", "Rahu☊", "Ketu☋"),
            ("House-3", "♊︎Gemini", "08:53:49", "Mercury☿", "Rahu☊", "Jupiter♃", "Jupiter♃"),
            ("House-4", "♋︎Cancer", "04:19:07", "Moon☾", "Saturn♄", "Saturn♄", "Venus♀"),
            ("House-5", "♌︎Leo", "02:45:47", "Sun☉", "Ketu☋", "Venus♀", "Mercury☿"),
            ("House-6", "♍︎Virgo", "06:24:57", "Mercury☿", "Sun☉", "Mercury☿", "Rahu☊"),
            ("House-7", "♎︎Libra", "13:22:28", "Venus♀", "Rahu☊", "Mercury☿", "Moon☾"),
            ("House-8", "♏︎Scorpio", "13:10:09", "Mars♂", "Saturn♄", "Rahu☊", "Rahu☊"),
            ("House-9", "♐︎Sagittarius", "08:53:49", "Jupiter♃", "Ketu☋", "Jupiter♃", "Moon☾"),
            ("House-10", "♑︎Capricorn", "04:19:07", "Saturn♄", "Sun☉", "Saturn♄", "Moon☾"),
            ("House-11", "♒︎Aquarius", "02:45:47", "Saturn♄", "Mars♂", "Venus♀", "Venus♀"),
            ("House-12", "♓︎Pisces", "06:24:57", "Jupiter♃", "Saturn♄", "Mercury☿", "Mars♂"),
        ]

        assert_paid_reference_match_percentage(
            data["cusps"],
            expected_cusps,
            title="Cuspal Position Tests / Test001",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            minimum_percentage=100.0,
            ignored_fields={"dms"},
        )

    @pytest.mark.planetary
    def test_planetary_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        vj_chart_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", vj_chart_payload)

        expected_planets = [
            ("Ascendant", "♈Aries", "13:22:28", "Mars♂", "Venus♀", "Venus♀", "Venus♀"),
            ("Sun☉", "♍︎Virgo", "21:38:14", "Mercury☿", "Moon☾", "Venus♀", "Jupiter♃"),
            ("Moon☾", "♐︎Sagittarius", "27:54:35", "Jupiter♃", "Sun☉", "Moon☾", "Saturn♄"),
            ("Mars♂", "♍︎Virgo", "18:43:49", "Mercury☿", "Moon☾", "Mercury☿", "Mars♂"),
            ("Mercury☿", "♍︎Virgo", "03:53:40", "Mercury☿", "Sun☉", "Saturn♄", "Venus♀"),
            ("Jupiter♃", "♊︎Gemini", "16:34:33", "Mercury☿", "Rahu☊", "Venus♀", "Jupiter♃"),
            ("Venus♀", "♏︎Scorpio", "06:16:20", "Mars♂", "Saturn♄", "Mercury☿", "Moon☾"),
            ("Saturn♄", "♐︎Sagittarius", "14:17:13", "Jupiter♃", "Venus♀", "Venus♀", "Rahu☊"),
            ("Rahu☊", "♑︎Capricorn", "29:18:43", "Saturn♄", "Mars♂", "Saturn♄", "Mars♂"),
            ("Ketu☋", "♋︎Cancer", "29:18:43", "Moon☾", "Mercury☿", "Saturn♄", "Mars♂"),
        ]

        assert_paid_reference_match_percentage(
            data["planets"],
            expected_planets,
            title="Planetary Position Tests / Test001",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            minimum_percentage=100.0,
            ignored_fields={"dms"},
        )


@pytest.mark.golden
class Test002:
    @pytest.mark.cuspal
    def test_cuspal_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        vijay_chand_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", vijay_chand_paid_reference_payload)

        expected_cusps = [
            ("House-1", "♐︎Sagittarius", "18:08:40", "Jupiter♃", "Venus♀", "Rahu☊", "Rahu☊"),
            ("House-2", "♑︎Capricorn", "24:35:17", "Saturn♄", "Mars♂", "Rahu☊", "Jupiter♃"),
            ("House-3", "♓︎Pisces", "02:20:13", "Jupiter♃", "Jupiter♃", "Rahu☊", "Mercury☿"),
            ("House-4", "♈Aries", "04:59:28", "Mars♂", "Ketu☋", "Mars♂", "Jupiter♃"),
            ("House-5", "♉︎Taurus", "01:33:36", "Venus♀", "Sun☉", "Jupiter♃", "Saturn♄"),
            ("House-6", "♉︎Taurus", "24:46:04", "Venus♀", "Mars♂", "Rahu☊", "Saturn♄"),
            ("House-7", "♊︎Gemini", "18:08:40", "Mercury☿", "Rahu☊", "Moon☾", "Moon☾"),
            ("House-8", "♋︎Cancer", "24:35:17", "Moon☾", "Mercury☿", "Rahu☊", "Jupiter♃"),
            ("House-9", "♍︎Virgo", "02:20:13", "Mercury☿", "Sun☉", "Jupiter♃", "Venus♀"),
            ("House-10", "♎︎Libra", "04:59:28", "Venus♀", "Mars♂", "Sun☉", "Mars♂"),
            ("House-11", "♏︎Scorpio", "01:33:36", "Mars♂", "Jupiter♃", "Rahu☊", "Rahu☊"),
            ("House-12", "♏︎Scorpio", "24:46:04", "Mars♂", "Mercury☿", "Rahu☊", "Saturn♄"),
        ]

        assert_paid_reference_match_percentage(
            data["cusps"],
            expected_cusps,
            title="Cuspal Position Tests / Test002",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )

    @pytest.mark.planetary
    def test_planetary_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        vijay_chand_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", vijay_chand_paid_reference_payload)

        expected_planets = [
            ("Sun☉", "♓︎Pisces", "18:24:48", "Jupiter♃", "Mercury☿", "Mercury☿", "Saturn♄"),
            ("Moon☾", "♋︎Cancer", "09:29:10", "Moon☾", "Saturn♄", "Venus♀", "Jupiter♃"),
            ("Mars♂", "♊︎Gemini", "25:01:13", "Mercury☿", "Jupiter♃", "Mercury☿", "Rahu☊"),
            ("Mercury☿", "♒︎Aquarius", "21:01:35", "Saturn♄", "Jupiter♃", "Jupiter♃", "Venus♀"),
            ("Jupiter♃", "♍︎Virgo", "15:49:19", "Mercury☿", "Moon☾", "Saturn♄", "Saturn♄"),
            ("Venus♀", "♓︎Pisces", "17:58:16", "Jupiter♃", "Mercury☿", "Mercury☿", "Rahu☊"),
            ("Saturn♄", "♒︎Aquarius", "03:00:19", "Saturn♄", "Mars♂", "Venus♀", "Venus♀"),
            ("Rahu☊", "♏︎Scorpio", "20:38:01", "Mars♂", "Mercury☿", "Venus♀", "Jupiter♃"),
            ("Ketu☋", "♉︎Taurus", "20:38:01", "Venus♀", "Moon☾", "Venus♀", "Venus♀"),
        ]

        assert_paid_reference_match_percentage(
            data["planets"][1:],
            expected_planets,
            title="Planetary Position Tests / Test002",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )


@pytest.mark.golden
class Test003:
    @pytest.mark.cuspal
    def test_cuspal_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        test003_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", test003_paid_reference_payload)

        expected_cusps = [
            ("House-1", "♋︎Cancer", "08:25:37", "Moon☾", "Saturn♄", "Venus♀", "Venus♀"),
            ("House-2", "♌︎Leo", "01:39:35", "Sun☉", "Ketu☋", "Venus♀", "Rahu☊"),
            ("House-3", "♌︎Leo", "28:45:33", "Sun☉", "Sun☉", "Mars♂", "Saturn♄"),
            ("House-4", "♎︎Libra", "00:35:07", "Venus♀", "Mars♂", "Mercury☿", "Venus♀"),
            ("House-5", "♏︎Scorpio", "05:01:07", "Mars♂", "Saturn♄", "Saturn♄", "Rahu☊"),
            ("House-6", "♐︎Sagittarius", "08:14:33", "Jupiter♃", "Ketu☋", "Jupiter♃", "Mercury☿"),
            ("House-7", "♑︎Capricorn", "08:25:37", "Saturn♄", "Sun☉", "Venus♀", "Moon☾"),
            ("House-8", "♒︎Aquarius", "01:39:35", "Saturn♄", "Mars♂", "Mercury☿", "Saturn♄"),
            ("House-9", "♒︎Aquarius", "28:45:33", "Saturn♄", "Jupiter♃", "Venus♀", "Ketu☋"),
            ("House-10", "♈Aries", "00:35:07", "Mars♂", "Ketu☋", "Ketu☋", "Saturn♄"),
            ("House-11", "♉︎Taurus", "05:01:07", "Venus♀", "Sun☉", "Saturn♄", "Jupiter♃"),
            ("House-12", "♊︎Gemini", "08:14:33", "Mercury☿", "Rahu☊", "Rahu☊", "Venus♀"),
        ]

        assert_paid_reference_match_percentage(
            data["cusps"],
            expected_cusps,
            title="Cuspal Position Tests / Test003",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )

    @pytest.mark.planetary
    def test_planetary_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        test003_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", test003_paid_reference_payload)

        expected_planets = [
            ("Sun☉", "♏︎Scorpio", "00:31:29", "Mars♂", "Jupiter♃", "Moon☾", "Sun☉"),
            ("Moon☾", "♐︎Sagittarius", "02:22:56", "Jupiter♃", "Ketu☋", "Venus♀", "Saturn♄"),
            ("Mars♂", "♎︎Libra", "19:45:45", "Venus♀", "Rahu☊", "Mars♂", "Ketu☋"),
            ("Mercury☿", "♎︎Libra", "12:57:28", "Venus♀", "Rahu☊", "Mercury☿", "Venus♀"),
            ("Jupiter♃", "♒︎Aquarius", "14:51:42", "Saturn♄", "Rahu☊", "Ketu☋", "Rahu☊"),
            ("Venus♀", "♏︎Scorpio", "03:03:32", "Mars♂", "Jupiter♃", "Rahu☊", "Moon☾"),
            ("Saturn♄", "♊︎Gemini", "25:14:51", "Mercury☿", "Jupiter♃", "Mercury☿", "Jupiter♃"),
            ("Rahu☊", "♏︎Scorpio", "16:49:52", "Mars♂", "Mercury☿", "Mercury☿", "Mercury☿"),
            ("Ketu☋", "♉︎Taurus", "16:49:52", "Venus♀", "Moon☾", "Saturn♄", "Sun☉"),
        ]

        assert_paid_reference_match_percentage(
            data["planets"][1:],
            expected_planets,
            title="Planetary Position Tests / Test003",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )


@pytest.mark.golden
class Test004:
    @pytest.mark.cuspal
    def test_cuspal_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        test004_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", test004_paid_reference_payload)

        expected_cusps = [
            ("House-1", "♏︎Scorpio", "07:27:38", "Mars♂", "Saturn♄", "Ketu☋", "Venus♀"),
            ("House-2", "♐︎Sagittarius", "06:46:19", "Jupiter♃", "Ketu☋", "Rahu☊", "Ketu☋"),
            ("House-3", "♑︎Capricorn", "07:37:49", "Saturn♄", "Sun☉", "Ketu☋", "Saturn♄"),
            ("House-4", "♒︎Aquarius", "10:08:27", "Saturn♄", "Rahu☊", "Jupiter♃", "Mars♂"),
            ("House-5", "♓︎Pisces", "12:16:45", "Jupiter♃", "Saturn♄", "Mars♂", "Jupiter♃"),
            ("House-6", "♈Aries", "11:29:16", "Mars♂", "Ketu☋", "Mercury☿", "Mercury☿"),
            ("House-7", "♉︎Taurus", "07:27:38", "Venus♀", "Sun☉", "Ketu☋", "Jupiter♃"),
            ("House-8", "♊︎Gemini", "06:46:19", "Mercury☿", "Rahu☊", "Rahu☊", "Rahu☊"),
            ("House-9", "♋︎Cancer", "07:37:49", "Moon☾", "Saturn♄", "Ketu☋", "Mars♂"),
            ("House-10", "♌︎Leo", "10:08:27", "Sun☉", "Ketu☋", "Saturn♄", "Venus♀"),
            ("House-11", "♍︎Virgo", "12:16:45", "Mercury☿", "Moon☾", "Rahu☊", "Jupiter♃"),
            ("House-12", "♎︎Libra", "11:29:16", "Venus♀", "Rahu☊", "Saturn♄", "Venus♀"),
        ]

        assert_paid_reference_match_percentage(
            data["cusps"],
            expected_cusps,
            title="Cuspal Position Tests / Test004",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )

    @pytest.mark.planetary
    def test_planetary_position(
        self,
        post_json: Callable[[str, dict[str, Any]], dict[str, Any]],
        test004_paid_reference_payload: dict[str, Any],
        record_reference_result: Callable[
            [str, bool, int, int, float, float, str, list[str] | None],
            None,
        ],
        show_kp_mismatches: bool,
    ) -> None:
        data = post_json("/api/kp-details", test004_paid_reference_payload)

        expected_planets = [
            ("Sun☉", "♋︎Cancer", "12:07:53", "Moon☾", "Saturn♄", "Mars♂", "Mars♂"),
            ("Moon☾", "♑︎Capricorn", "09:22:47", "Saturn♄", "Sun☉", "Venus♀", "Saturn♄"),
            ("Mars♂", "♉︎Taurus", "27:08:45", "Venus♀", "Mars♂", "Jupiter♃", "Venus♀"),
            ("Mercury☿", "♊︎Gemini", "23:37:00", "Mercury☿", "Jupiter♃", "Saturn♄", "Jupiter♃"),
            ("Jupiter♃", "♋︎Cancer", "12:14:28", "Moon☾", "Saturn♄", "Mars♂", "Rahu☊"),
            ("Venus♀", "♌︎Leo", "27:10:12", "Sun☉", "Sun☉", "Sun☉", "Mercury☿"),
            ("Saturn♄", "♓︎Pisces", "20:36:28", "Jupiter♃", "Mercury☿", "Venus♀", "Jupiter♃"),
            ("Rahu☊", "♒︎Aquarius", "05:43:32", "Saturn♄", "Mars♂", "Moon☾", "Rahu☊"),
            ("Ketu☋", "♌︎Leo", "05:43:32", "Sun☉", "Ketu☋", "Rahu☊", "Rahu☊"),
            ("Uranus⛢", "♉︎Taurus", "10:47:05", "Venus♀", "Moon☾", "Moon☾", "Mercury☿"),
            ("Neptune♆", "♓︎Pisces", "10:09:15", "Jupiter♃", "Saturn♄", "Venus♀", "Mercury☿"),
            ("Pluto♇", "♑︎Capricorn", "10:06:01", "Saturn♄", "Moon☾", "Moon☾", "Mars♂"),
        ]

        assert_paid_reference_match_percentage(
            data["planets"][1:],
            expected_planets,
            title="Planetary Position Tests / Test004",
            record_reference_result=record_reference_result,
            show_kp_mismatches=show_kp_mismatches,
            ignored_fields={"dms"},
        )
