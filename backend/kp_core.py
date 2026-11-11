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


@dataclass(frozen=True)
class PlanetStateFlags:
    retrograde: bool = False
    combust: bool = False
    exalted: bool = False
    debilitated: bool = False


@dataclass(frozen=True)
class ChartPoint:
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float


@dataclass(frozen=True)
class ChartPlanet:
    name: str
    short_name: str
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float
    state_flags: PlanetStateFlags


@dataclass(frozen=True)
class D1Ascendant:
    sign: str
    sign_index: int
    sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float


@dataclass(frozen=True)
class D1House:
    house_number: int
    sign: str
    sign_index: int
    sign_number: int
    planets: list[ChartPlanet]


@dataclass(frozen=True)
class D1Chart:
    chart: str
    chart_style: str
    name: str
    birth_datetime: BirthDateTime
    location: Location
    settings: CalculationSettings
    ascendant: D1Ascendant
    houses: list[D1House]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BhavaChalitPlanet:
    name: str
    short_name: str
    rashi_sign: str
    rashi_sign_index: int
    rashi_sign_number: int
    degree: str
    degree_decimal: float
    absolute_longitude: float
    bhava_house_number: int
    state_flags: PlanetStateFlags


@dataclass(frozen=True)
class BhavaChalitHouse:
    house_number: int
    display_number: int
    start: ChartPoint
    cusp: ChartPoint
    end: ChartPoint
    planets: list[BhavaChalitPlanet]


@dataclass(frozen=True)
class BhavaChalitChart:
    chart: str
    chart_style: str
    name: str
    birth_datetime: BirthDateTime
    location: Location
    settings: CalculationSettings
    ascendant: ChartPoint
    houses: list[BhavaChalitHouse]

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


def chart_planet_name(planet_id: int | str) -> str:
    names = {
        const._ascendant_symbol: "Ascendant",
        const.SUN_ID: "Sun",
        const.MOON_ID: "Moon",
        const.MARS_ID: "Mars",
        const.MERCURY_ID: "Mercury",
        const.JUPITER_ID: "Jupiter",
        const.VENUS_ID: "Venus",
        const.SATURN_ID: "Saturn",
        const.RAHU_ID: "Rahu",
        const.KETU_ID: "Ketu",
        9: "Uranus",
        10: "Neptune",
        11: "Pluto",
    }
    return names.get(planet_id, planet_name(planet_id))


def chart_planet_short_name(planet_id: int | str) -> str:
    short_names = {
        const._ascendant_symbol: "Asc",
        const.SUN_ID: "Su",
        const.MOON_ID: "Mo",
        const.MARS_ID: "Ma",
        const.MERCURY_ID: "Me",
        const.JUPITER_ID: "Ju",
        const.VENUS_ID: "Ve",
        const.SATURN_ID: "Sa",
        const.RAHU_ID: "Ra",
        const.KETU_ID: "Ke",
        9: "Ur",
        10: "Ne",
        11: "Pl",
    }
    return short_names.get(planet_id, chart_planet_name(planet_id))


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


def _chart_point(total_degrees: float) -> ChartPoint:
    absolute_longitude = total_degrees % 360.0
    sign, sign_index, degree = format_sign_dms(absolute_longitude)
    _, degree_decimal = split_longitude(absolute_longitude)
    return ChartPoint(
        sign=sign,
        sign_index=sign_index,
        sign_number=sign_index + 1,
        degree=degree,
        degree_decimal=degree_decimal,
        absolute_longitude=absolute_longitude,
    )


def _apply_settings(settings: CalculationSettings) -> None:
    drik.set_planet_list(
        set_rahu_ketu_as_true_nodes=settings.use_true_nodes,
        include_western_planets=settings.include_western_planets,
    )
    drik.set_ayanamsa_mode(settings.ayanamsa_mode)


def _date_time_place(
    birth_datetime: BirthDateTime,
    location: Location,
) -> tuple[Any, tuple[int, int, int], Any, float]:
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
    return date, time, place, jd


def _d1_positions(jd: float, place: Any) -> list[tuple[int | str, tuple[int, float]]]:
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
    return planet_positions[:planet_count]


def _planet_state_flags(
    planet: int | str,
    sign_index: int,
    planet_positions: list[tuple[int | str, tuple[int, float]]],
    retrograde_planets: set[int],
    combust_planets: set[int],
) -> PlanetStateFlags:
    if planet == const._ascendant_symbol:
        return PlanetStateFlags()

    is_rahu_ketu = planet in {const.RAHU_ID, const.KETU_ID}
    is_classical_planet = planet in const.SUN_TO_SATURN
    return PlanetStateFlags(
        retrograde=is_rahu_ketu or planet in retrograde_planets,
        combust=planet in combust_planets,
        exalted=(
            utils.is_planet_in_exalation(
                planet,
                sign_index,
                planet_positions,
                enforce_deep_exaltation=False,
            )
            if is_classical_planet
            else False
        ),
        debilitated=(
            utils.is_planet_in_debilitation(
                planet,
                sign_index,
                planet_positions,
                enforce_deep_debilitation=False,
            )
            if is_classical_planet
            else False
        ),
    )


def _chart_planet(
    planet: int | str,
    sign_index: int,
    degree_decimal: float,
    state_flags: PlanetStateFlags | None = None,
) -> ChartPlanet:
    absolute_longitude = sign_index * 30.0 + degree_decimal
    point = _chart_point(absolute_longitude)
    return ChartPlanet(
        name=chart_planet_name(planet),
        short_name=chart_planet_short_name(planet),
        sign=point.sign,
        sign_index=point.sign_index,
        sign_number=point.sign_number,
        degree=point.degree,
        degree_decimal=point.degree_decimal,
        absolute_longitude=point.absolute_longitude,
        state_flags=state_flags or PlanetStateFlags(),
    )


def _bhava_chalit_planet(
    planet: int | str,
    sign_index: int,
    degree_decimal: float,
    bhava_house_number: int,
    state_flags: PlanetStateFlags | None = None,
) -> BhavaChalitPlanet:
    point = _chart_point(sign_index * 30.0 + degree_decimal)
    return BhavaChalitPlanet(
        name=chart_planet_name(planet),
        short_name=chart_planet_short_name(planet),
        rashi_sign=point.sign,
        rashi_sign_index=point.sign_index,
        rashi_sign_number=point.sign_number,
        degree=point.degree,
        degree_decimal=point.degree_decimal,
        absolute_longitude=point.absolute_longitude,
        bhava_house_number=bhava_house_number,
        state_flags=state_flags or PlanetStateFlags(),
    )


def calculate_kp_chart(
    *,
    name: str,
    birth_datetime: BirthDateTime,
    location: Location,
    settings: CalculationSettings | None = None,
) -> KpChart:
    settings = settings or CalculationSettings()
    _apply_settings(settings)

    _, _, place, jd = _date_time_place(birth_datetime, location)

    planet_positions = _d1_positions(jd, place)
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


def calculate_d1_chart(
    *,
    name: str,
    birth_datetime: BirthDateTime,
    location: Location,
    settings: CalculationSettings | None = None,
) -> D1Chart:
    settings = settings or CalculationSettings()
    _apply_settings(settings)

    _, _, place, jd = _date_time_place(birth_datetime, location)
    planet_positions = _d1_positions(jd, place)
    position_by_object = {
        planet: (sign_index, degree_decimal)
        for planet, (sign_index, degree_decimal) in planet_positions
    }

    asc_sign_index, asc_degree_decimal = position_by_object[const._ascendant_symbol]
    ascendant_planet = _chart_planet(
        const._ascendant_symbol,
        asc_sign_index,
        asc_degree_decimal,
    )
    ascendant = D1Ascendant(
        sign=ascendant_planet.sign,
        sign_index=ascendant_planet.sign_index,
        sign_number=ascendant_planet.sign_number,
        degree=ascendant_planet.degree,
        degree_decimal=ascendant_planet.degree_decimal,
        absolute_longitude=ascendant_planet.absolute_longitude,
    )

    houses = [
        D1House(
            house_number=house_number,
            sign=utils.RAASI_LIST[(asc_sign_index + house_number - 1) % 12],
            sign_index=(asc_sign_index + house_number - 1) % 12,
            sign_number=((asc_sign_index + house_number - 1) % 12) + 1,
            planets=[],
        )
        for house_number in range(1, 13)
    ]

    retrograde_planets = set(drik.planets_in_retrograde(jd, place))
    combust_planets = set(charts.planets_in_combustion(planet_positions))
    houses[0].planets.append(ascendant_planet)

    for planet, (sign_index, degree_decimal) in planet_positions:
        if planet == const._ascendant_symbol:
            continue

        house_number = ((sign_index - asc_sign_index) % 12) + 1
        state_flags = _planet_state_flags(
            planet,
            sign_index,
            planet_positions,
            retrograde_planets,
            combust_planets,
        )
        houses[house_number - 1].planets.append(
            _chart_planet(planet, sign_index, degree_decimal, state_flags)
        )

    return D1Chart(
        chart="D-1",
        chart_style="north_indian",
        name=name,
        birth_datetime=birth_datetime,
        location=location,
        settings=settings,
        ascendant=ascendant,
        houses=houses,
    )


def calculate_bhava_chalit_chart(
    *,
    name: str,
    birth_datetime: BirthDateTime,
    location: Location,
    settings: CalculationSettings | None = None,
) -> BhavaChalitChart:
    settings = settings or CalculationSettings()
    _apply_settings(settings)

    _, _, place, jd = _date_time_place(birth_datetime, location)
    planet_positions = _d1_positions(jd, place)
    position_by_object = {
        planet: (sign_index, degree_decimal)
        for planet, (sign_index, degree_decimal) in planet_positions
    }
    asc_sign_index, asc_degree_decimal = position_by_object[const._ascendant_symbol]
    ascendant = _chart_point(asc_sign_index * 30.0 + asc_degree_decimal)

    retrograde_planets = set(drik.planets_in_retrograde(jd, place))
    combust_planets = set(charts.planets_in_combustion(planet_positions))
    bhava_info = charts._bhaava_madhya_new(
        jd,
        place,
        divisional_chart_factor=1,
        bhava_madhya_method=settings.house_cusp_method,
        ascendant_is_middle_of_house=False,
    )

    houses = []
    for house_number, (
        _,
        (start_longitude, middle_longitude, end_longitude),
        planets,
    ) in enumerate(bhava_info, start=1):
        cusp = _chart_point(start_longitude)
        house_planets = []

        for planet in planets:
            sign_index, degree_decimal = position_by_object[planet]
            state_flags = _planet_state_flags(
                planet,
                sign_index,
                planet_positions,
                retrograde_planets,
                combust_planets,
            )
            house_planets.append(
                _bhava_chalit_planet(
                    planet,
                    sign_index,
                    degree_decimal,
                    house_number,
                    state_flags,
                )
            )

        houses.append(
            BhavaChalitHouse(
                house_number=house_number,
                display_number=cusp.sign_number,
                start=_chart_point(start_longitude),
                cusp=cusp,
                end=_chart_point(end_longitude),
                planets=house_planets,
            )
        )

    return BhavaChalitChart(
        chart="Bhava Chalit",
        chart_style="north_indian",
        name=name,
        birth_datetime=birth_datetime,
        location=location,
        settings=settings,
        ascendant=ascendant,
        houses=houses,
    )
