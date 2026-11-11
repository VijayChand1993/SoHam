from kp_core import (
    BirthDateTime,
    CalculationSettings,
    calculate_kp_chart,
)

from app.models import KpChartRequest, KpChartResponse
from app.services.places import to_core_location


def calculate_chart_response(request: KpChartRequest) -> KpChartResponse:
    chart = calculate_kp_chart(
        name=request.name,
        birth_datetime=BirthDateTime(**request.birth_datetime.model_dump()),
        location=to_core_location(request.location),
        settings=CalculationSettings(**request.settings.model_dump()),
    )
    return KpChartResponse.model_validate(chart.to_dict())
