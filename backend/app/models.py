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


class PlanetStateFlagsResponse(BaseModel):
    retrograde: bool = False
    combust: bool = False
    exalted: bool = False
    debilitated: bool = False


class ChartPlanetResponse(BaseModel):
    name: str
    short_name: str
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float
    state_flags: PlanetStateFlagsResponse


class D1AscendantResponse(BaseModel):
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float


class D1HouseResponse(BaseModel):
    house_number: int
    sign: str
    sign_index: int
    sign_number: int
    planets: list[ChartPlanetResponse]


class D1ChartResponse(BaseModel):
    chart: Literal["D-1", "Transit"]
    chart_style: Literal["north_indian"]
    name: str
    birth_datetime: BirthDateTimeRequest
    location: LocationRequest
    settings: CalculationSettingsRequest
    ascendant: D1AscendantResponse
    houses: list[D1HouseResponse]


class ChartPointResponse(BaseModel):
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float


class BhavaChalitPlanetResponse(BaseModel):
    name: str
    short_name: str
    rashi_sign: str
    rashi_sign_index: int
    rashi_sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float
    bhava_house_number: int
    state_flags: PlanetStateFlagsResponse


class BhavaChalitHouseResponse(BaseModel):
    house_number: int
    display_number: int
    start: ChartPointResponse
    cusp: ChartPointResponse
    end: ChartPointResponse
    planets: list[BhavaChalitPlanetResponse]


class BhavaChalitChartResponse(BaseModel):
    chart: Literal["Bhava Chalit"]
    chart_style: Literal["north_indian"]
    name: str
    birth_datetime: BirthDateTimeRequest
    location: LocationRequest
    settings: CalculationSettingsRequest
    ascendant: ChartPointResponse
    houses: list[BhavaChalitHouseResponse]


class RelatedSignificatorPlanetResponse(BaseModel):
    planet: str
    short_name: str
    occupied_house: int | None
    rashi_lord_houses: list[int]
    significations: list[int]


class SignificatorPlanetResponse(BaseModel):
    role: str
    planet: str
    short_name: str
    occupied_house: int | None
    rashi_lord_houses: list[int]
    significations: list[int]
    original_planet: str | None = None
    original_short_name: str | None = None
    is_duplicate_replacement: bool = False
    node_rashi_lord: RelatedSignificatorPlanetResponse | None = None


class HouseSignificatorLevelResponse(BaseModel):
    level: int
    items: list[SignificatorPlanetResponse]


class HouseSignificatorResponse(BaseModel):
    house_number: int
    source_sub_lord: str
    source_sub_lord_short_name: str
    levels: list[HouseSignificatorLevelResponse]


class HouseSignificatorsChartResponse(BaseModel):
    name: str
    birth_datetime: BirthDateTimeRequest
    location: LocationRequest
    settings: CalculationSettingsRequest
    houses: list[HouseSignificatorResponse]


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
