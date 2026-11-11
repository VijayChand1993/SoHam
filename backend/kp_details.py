import argparse

from rich.console import Console
from rich.table import Table

from kp_core import (
    BirthDateTime,
    CalculationSettings,
    Location,
    PositionRow,
    calculate_kp_chart,
    parse_dms,
)


def _prompt_if_missing(value, prompt, cast=str):
    if value is not None:
        return cast(value)
    return cast(input(prompt).strip())


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print KP lord details using PyJHora."
    )
    parser.add_argument("--name")
    parser.add_argument("--date", help="Birth date as YYYY-MM-DD")
    parser.add_argument("--time", help="Birth time as HH:MM or HH:MM:SS")
    parser.add_argument("--place")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--lat-dms", help="Latitude as DD:MM or DD:MM:SS")
    parser.add_argument("--lon-dms", help="Longitude as DD:MM or DD:MM:SS")
    parser.add_argument("--tz", type=float, help="Timezone offset, e.g. 5.5 for IST")
    parser.add_argument("--ayanamsa", default="KP")
    parser.add_argument("--house-method", default="3")
    return parser.parse_args()


def _parse_house_method(value):
    value = str(value).strip()
    return int(value) if value.lstrip("-").isdigit() else value


def get_chart_inputs():
    args = parse_args()
    name = _prompt_if_missing(args.name, "Name: ")
    date_text = _prompt_if_missing(args.date, "Birth date (YYYY-MM-DD): ")
    time_text = _prompt_if_missing(args.time, "Birth time (HH:MM[:SS]): ")
    place = _prompt_if_missing(args.place, "Birth place name: ")
    if args.lat_dms is not None:
        latitude = parse_dms(args.lat_dms)
    else:
        latitude = _prompt_if_missing(args.lat, "Latitude decimal degrees: ", float)
    if args.lon_dms is not None:
        longitude = parse_dms(args.lon_dms)
    else:
        longitude = _prompt_if_missing(args.lon, "Longitude decimal degrees: ", float)
    timezone = _prompt_if_missing(args.tz, "Timezone offset, e.g. 5.5 for IST: ", float)

    year, month, day = [int(part) for part in date_text.split("-")]
    time_parts = [int(part) for part in time_text.split(":")]
    if len(time_parts) == 2:
        time_parts.append(0)
    if len(time_parts) != 3:
        raise ValueError("Birth time must be HH:MM or HH:MM:SS")

    return (
        name,
        BirthDateTime(
            year=year,
            month=month,
            day=day,
            hour=time_parts[0],
            minute=time_parts[1],
            second=time_parts[2],
        ),
        Location(
            name=place,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
        ),
        CalculationSettings(
            ayanamsa_mode=args.ayanamsa,
            house_cusp_method=_parse_house_method(args.house_method),
        ),
    )


def _build_table(title, first_column, rows: list[PositionRow]):
    table = Table(title=title)
    table.add_column(first_column, no_wrap=True)
    table.add_column("Sign", no_wrap=True)
    table.add_column("D-M-S", no_wrap=True)
    table.add_column("KP No.", justify="right")
    table.add_column("Rasi Lord")
    table.add_column("Star Lord")
    table.add_column("Sub Lord")
    table.add_column("Sub-Sub Lord")
    table.add_column("Sookshma")
    table.add_column("Praana")
    table.add_column("Deha")

    for row in rows:
        table.add_row(
            row.label,
            row.sign,
            row.dms,
            str(row.kp.kp_number),
            row.kp.rasi_lord,
            row.kp.star_lord,
            row.kp.sub_lord,
            row.kp.sub_sub_lord,
            row.kp.sookshma_lord,
            row.kp.praana_lord,
            row.kp.deha_lord,
        )

    return table


def main():
    name, birth_datetime, location, settings = get_chart_inputs()
    chart = calculate_kp_chart(
        name=name,
        birth_datetime=birth_datetime,
        location=location,
        settings=settings,
    )

    console = Console(width=180)
    console.print(
        f"Settings: ayanamsa={chart.settings.ayanamsa_mode}, "
        f"house_method={chart.settings.house_cusp_method}, "
        f"true_nodes={chart.settings.use_true_nodes}"
    )
    console.print(
        f"Location: {chart.location.name}, "
        f"lat={chart.location.latitude:.6f}, "
        f"lon={chart.location.longitude:.6f}, "
        f"tz={chart.location.timezone:g}"
    )
    console.print(_build_table(f"Cuspal Positions - {chart.name}", "Cusp", chart.cusps))
    console.print(_build_table(f"Planetary Positions - {chart.name}", "Planet", chart.planets))



if __name__ == "__main__":
    main()
