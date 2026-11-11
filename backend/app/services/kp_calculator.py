from kp_core import (
    BirthDateTime,
    CalculationSettings,
    calculate_bhava_chalit_chart,
    calculate_d1_chart,
    calculate_kp_chart,
)

from app.models import (
    BhavaChalitChartResponse,
    D1ChartResponse,
    KpChartRequest,
    KpChartResponse,
)
from app.services.places import to_core_location


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
