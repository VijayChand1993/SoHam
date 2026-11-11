import contextlib
import io
from dataclasses import asdict, dataclass
from typing import Any

with contextlib.redirect_stdout(io.StringIO()):
    from jhora import const, utils
    from jhora.horoscope.chart import charts

drik = utils.hora_engine_proxy


DEFAULT_AYANAMSA_MODE = "KP"
DEFAULT_HOUSE_CUSP_METHOD = 3  # PyJHora: KP Method / Placidus cusps.
DEFAULT_USE_TRUE_NODES = False
DEFAULT_INCLUDE_WESTERN_PLANETS = False
DEFAULT_ELEVATION = 0.0


@dataclass(frozen=True)
class BirthDateTime:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int = 0


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: float
    elevation: float = DEFAULT_ELEVATION


@dataclass(frozen=True)
class CalculationSettings:
    ayanamsa_mode: str = DEFAULT_AYANAMSA_MODE
    house_cusp_method: int | str = DEFAULT_HOUSE_CUSP_METHOD
    use_true_nodes: bool = DEFAULT_USE_TRUE_NODES
    include_western_planets: bool = DEFAULT_INCLUDE_WESTERN_PLANETS


@dataclass(frozen=True)
class KpLordDetails:
    kp_number: int
    rasi_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    sookshma_lord: str
    praana_lord: str
    deha_lord: str


@dataclass(frozen=True)
class PositionRow:
    label: str
    sign: str
    sign_index: int
    dms: str
    absolute_longitude: float
    kp: KpLordDetails


@dataclass(frozen=True)
class KpChart:
    name: str
    birth_datetime: BirthDateTime
    location: Location
    settings: CalculationSettings
    cusps: list[PositionRow]
    planets: list[PositionRow]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_dms(value: str) -> float:
    parts = str(value).strip().replace(" ", ":").split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError("DMS value must be DD[:MM[:SS]]")

    sign = -1 if parts[0].strip().startswith("-") else 1
    degrees = abs(float(parts[0]))
    minutes = float(parts[1]) if len(parts) >= 2 else 0.0
    seconds = float(parts[2]) if len(parts) == 3 else 0.0
    if minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60:
        raise ValueError("DMS minutes and seconds must be between 0 and 59")

    return sign * (degrees + minutes / 60.0 + seconds / 3600.0)


def planet_name(planet_id: int | str) -> str:
    if planet_id == const._ascendant_symbol:
        return "Ascendant"
    return utils.PLANET_NAMES[planet_id]


def split_longitude(total_degrees: float) -> tuple[int, float]:
    return drik.dasavarga_from_long(total_degrees)


def format_sign_dms(total_degrees: float) -> tuple[str, int, str]:
    sign_index, sign_degrees = split_longitude(total_degrees)
    sign_name = utils.RAASI_LIST[sign_index]
    degrees = int(sign_degrees)
    minutes_float = (sign_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = round((minutes_float - minutes) * 60)
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    return sign_name, sign_index, f"{degrees:02d}:{minutes:02d}:{seconds:02d}"


def _kp_lord_details(total_degrees: float, kp_details: list[int]) -> KpLordDetails:
    sign_index, _ = split_longitude(total_degrees)
    kp_number, star, sub, sub_sub, sookshma, praana, deha = kp_details
    return KpLordDetails(
        kp_number=kp_number,
        rasi_lord=planet_name(const._house_owners_list[sign_index]),
        star_lord=planet_name(star),
        sub_lord=planet_name(sub),
        sub_sub_lord=planet_name(sub_sub),
        sookshma_lord=planet_name(sookshma),
        praana_lord=planet_name(praana),
        deha_lord=planet_name(deha),
    )


def _position_row(label: str, total_degrees: float, kp_details: list[int]) -> PositionRow:
    sign, sign_index, dms = format_sign_dms(total_degrees)
    return PositionRow(
        label=label,
        sign=sign,
        sign_index=sign_index,
        dms=dms,
        absolute_longitude=total_degrees % 360.0,
        kp=_kp_lord_details(total_degrees, kp_details),
    )


def _apply_settings(settings: CalculationSettings) -> None:
    drik.set_planet_list(
        set_rahu_ketu_as_true_nodes=settings.use_true_nodes,
        include_western_planets=settings.include_western_planets,
    )
    drik.set_ayanamsa_mode(settings.ayanamsa_mode)


def calculate_kp_chart(
    *,
    name: str,
    birth_datetime: BirthDateTime,
    location: Location,
    settings: CalculationSettings | None = None,
) -> KpChart:
    settings = settings or CalculationSettings()
    _apply_settings(settings)

    date = drik.Date(birth_datetime.year, birth_datetime.month, birth_datetime.day)
    time = (birth_datetime.hour, birth_datetime.minute, birth_datetime.second)
    place = drik.Place(
        location.name,
        location.latitude,
        location.longitude,
        location.timezone,
        location.elevation,
    )
    jd = utils.julian_day_number(date, time)

    planet_positions = charts.divisional_chart(
        jd,
        place,
        divisional_chart_factor=1,
        chart_method=1,
        exclude_non_planets=True,
    )
    planet_count = (
        const._pp_count_upto_pluto
        if const._INCLUDE_URANUS_TO_PLUTO
        else const._pp_count_upto_ketu
    )
    planet_positions = planet_positions[:planet_count]
    planet_kp = charts.get_KP_lords_from_planet_positions(planet_positions)

    position_by_object = {
        planet: sign * 30 + degrees
        for planet, (sign, degrees) in planet_positions
    }
    planets = [
        _position_row(planet_name(planet), position_by_object[planet], kp_details)
        for planet, kp_details in planet_kp.items()
    ]

    bhava_info = charts._bhaava_madhya_new(
        jd,
        place,
        divisional_chart_factor=1,
        bhava_madhya_method=settings.house_cusp_method,
    )
    cusps = []
    for house_number, (_, (_, cusp_longitude, _), _) in enumerate(bhava_info, start=1):
        label = f"House-{house_number}"
        kp_details = utils.kp_lords_for_longitude(label, cusp_longitude)[label]
        cusps.append(_position_row(label, cusp_longitude, kp_details))

    return KpChart(
        name=name,
        birth_datetime=birth_datetime,
        location=location,
        settings=settings,
        cusps=cusps,
        planets=planets,
    )
