from datetime import datetime, timedelta, timezone

from kp_core import (
    BirthDateTime,
    CalculationSettings,
    calculate_bhava_chalit_chart,
    calculate_d1_chart,
    calculate_house_significators,
    calculate_kp_chart,
)

from app.models import (
    BhavaChalitChartResponse,
    BirthDateTimeRequest,
    D1ChartResponse,
    HouseSignificatorsChartResponse,
    InstantPrashnaRequest,
    InstantPrashnaResponse,
    KpChartRequest,
    KpChartResponse,
)
from app.services.places import to_core_location


def _current_datetime_for_timezone(timezone_offset: float) -> BirthDateTimeRequest:
    local_datetime = datetime.now(timezone.utc) + timedelta(hours=timezone_offset)
    return BirthDateTimeRequest(
        year=local_datetime.year,
        month=local_datetime.month,
        day=local_datetime.day,
        hour=local_datetime.hour,
        minute=local_datetime.minute,
        second=local_datetime.second,
    )


def calculate_chart_response(request: KpChartRequest) -> KpChartResponse:
    chart = calculate_kp_chart(
        name=request.name,
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    return KpChartResponse.model_validate(chart.to_dict())


def calculate_d1_chart_response(request: KpChartRequest) -> D1ChartResponse:
    chart = calculate_d1_chart(
        name=request.name,
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    return D1ChartResponse.model_validate(chart.to_dict())


def calculate_transit_chart_response(request: KpChartRequest) -> D1ChartResponse:
    chart = calculate_d1_chart(
        name=request.name or "Transit",
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    chart_data = chart.to_dict()
    chart_data["chart"] = "Transit"
    return D1ChartResponse.model_validate(chart_data)


def calculate_bhava_chalit_chart_response(
    request: KpChartRequest,
) -> BhavaChalitChartResponse:
    chart = calculate_bhava_chalit_chart(
        name=request.name,
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    return BhavaChalitChartResponse.model_validate(chart.to_dict())


def calculate_house_significators_response(
    request: KpChartRequest,
) -> HouseSignificatorsChartResponse:
    chart = calculate_house_significators(
        name=request.name,
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    return HouseSignificatorsChartResponse.model_validate(chart.to_dict())


def calculate_instant_prashna_response(
    request: InstantPrashnaRequest,
) -> InstantPrashnaResponse:
    calculated_datetime = _current_datetime_for_timezone(request.location.timezone)
    chart_request = KpChartRequest(
        name="Instant Prashna",
        birth_datetime=calculated_datetime,
        location=request.location,
        settings=request.settings,
    )

    return InstantPrashnaResponse(
        mode="instant_prashna",
        calculated_datetime=calculated_datetime,
        location=request.location,
        settings=request.settings,
        kp_chart=calculate_chart_response(chart_request),
        d1_chart=calculate_d1_chart_response(chart_request),
        bhava_chalit_chart=calculate_bhava_chalit_chart_response(chart_request),
        house_significators=calculate_house_significators_response(chart_request),
    )
