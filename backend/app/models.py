from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


KP_CHART_REQUEST_EXAMPLE = {
    "name": "VJ",
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
        "latitude": 29.418,
        "longitude": 80.207,
        "timezone": 5.5,
    },
    "settings": {
        "ayanamsa_mode": "KP",
        "house_cusp_method": 3,
        "use_true_nodes": False,
        "include_western_planets": False,
    },
}


class BirthDateTimeRequest(BaseModel):
    year: int = Field(..., ge=1)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    second: int = Field(0, ge=0, le=59)


class LocationRequest(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: float = Field(..., ge=-14, le=14)
    elevation: float = 0.0


class CalculationSettingsRequest(BaseModel):
    ayanamsa_mode: str = "KP"
    house_cusp_method: int | str = 3
    use_true_nodes: bool = False
    include_western_planets: bool = False


class KpChartRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": KP_CHART_REQUEST_EXAMPLE})

    name: str = ""
    birth_datetime: BirthDateTimeRequest
    location: LocationRequest
    settings: CalculationSettingsRequest = Field(
        default_factory=CalculationSettingsRequest
    )


class KpLordResponse(BaseModel):
    kp_number: int
    rasi_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    sookshma_lord: str
    praana_lord: str
    deha_lord: str


class PositionRowResponse(BaseModel):
    label: str
    sign: str
    sign_index: int
    dms: str
    absolute_longitude: float
    kp: KpLordResponse


class KpChartResponse(BaseModel):
    name: str
    birth_datetime: BirthDateTimeRequest
    location: LocationRequest
    settings: CalculationSettingsRequest
    cusps: list[PositionRowResponse]
    planets: list[PositionRowResponse]


class PlaceSearchResult(BaseModel):
    display_name: str
    city: str = ""
    state: str = ""
    country: str = ""
    latitude: float
    longitude: float
    timezone: float
    elevation: float = 0.0
    source: str = "pyjhora"


class PlaceSearchResponse(BaseModel):
    query: str
    count: int
    results: list[PlaceSearchResult]


class HealthResponse(BaseModel):
    status: Literal["ok"]
