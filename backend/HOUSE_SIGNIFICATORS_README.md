# House Significators Calculation

This document explains the backend logic used for the KP house significators API.

## API Output

The calculation is returned by:

```text
POST /api/kp/house-significators
```

It is also included inside:

```text
POST /api/kp/instant-prashna
```

Response shape:

```json
{
  "houses": [
    {
      "house_number": 1,
      "source_sub_lord": "Rahu",
      "source_sub_lord_short_name": "Ra",
      "levels": []
    }
  ]
}
```

The API returns this calculation for all 12 houses.

## Core Rule

For every house, the backend starts from the cusp sub lord of that house.

For a house whose sub lord is `a`:

| Level | Source | Meaning |
| --- | --- | --- |
| Level 1 | `a` | Sub lord of the house cusp |
| Level 2 item 1 | `STL(a)` | Star lord of the cusp sub lord |
| Level 2 item 2 | `SL(a)` | Sub lord of the cusp sub lord |
| Level 3 item 1 | `STL(STL(a))` | Star lord of Level 2 item 1 |
| Level 3 item 2 | `STL(SL(a))` | Star lord of Level 2 item 2 |

The KP lord data for planets comes from PyJHora's KP planet positions.

## Signification Numbers

For each significator planet, the backend calculates:

```json
{
  "occupied_house": 7,
  "rashi_lord_houses": [4, 11, 12],
  "significations": [7, 4, 11, 12]
}
```

The numbers are built as:

1. The Bhava Chalit house occupied by the planet.
2. The cusp numbers whose rashi lord is that planet.

The final `significations` list is unique, but preserves order. This means the occupied house comes first, followed by rashi-lord houses that were not already present.

## Bhava Chalit Usage

House occupation is based on Bhava Chalit placement, not only D1/Rashi sign placement.

The backend uses PyJHora Bhava Madhya/KP cusp logic with the configured house cusp method:

```text
settings.house_cusp_method
```

In this app, the default is:

```text
3
```

This is the KP/Placidus cusp method already used elsewhere in the app.

## Cusp Rashi Lord Houses

For every cusp, the backend determines the cusp rashi lord.

Example:

```text
If houses 4, 11, and 12 have Mars as their cusp rashi lord,
then Mars has rashi_lord_houses = [4, 11, 12].
```

These house numbers are added after the occupied house when building `significations`.

## Rahu/Ketu Special Case

When the significator planet is Rahu or Ketu, the backend also includes that node's Bhava Chalit rashi lord.

The node response includes:

```json
{
  "node_rashi_lord": {
    "planet": "Mars",
    "short_name": "Ma",
    "occupied_house": 7,
    "rashi_lord_houses": [4, 11, 12],
    "significations": [7, 4, 11, 12]
  }
}
```

The node's rashi lord is based on Bhava Chalit context.

## Duplicate Replacement Rule

For Level 2 and Level 3, each level has two planets.

If both planets in the same level are the same, the second planet is replaced by the Bhava Chalit rashi lord of that second planet.

Example:

```text
Level 2 raw planets: Jupiter, Jupiter
Final Level 2 planets: Jupiter, rashi lord of Jupiter's Bhava Chalit placement
```

When this happens, the response marks the second item with:

```json
{
  "is_duplicate_replacement": true,
  "original_planet": "Jupiter",
  "original_short_name": "Ju"
}
```

## Response Fields

Each item in a level contains:

```json
{
  "role": "STL_OF_SL",
  "planet": "Mercury",
  "short_name": "Me",
  "occupied_house": 2,
  "rashi_lord_houses": [7, 9],
  "significations": [2, 7, 9],
  "original_planet": null,
  "original_short_name": null,
  "is_duplicate_replacement": false,
  "node_rashi_lord": null
}
```

## Code Locations

Main implementation:

```text
backend/kp_core.py
```

Important helpers:

- `calculate_house_significators(...)`
- `_cusp_lord_context(...)`
- `_bhava_placement_context(...)`
- `_planet_significations(...)`
- `_significator_planet(...)`
- `_replace_second_duplicate_with_bhava_rashi_lord(...)`

API service wrapper:

```text
backend/app/services/kp_calculator.py
```

API route:

```text
backend/app/main.py
```

Response models:

```text
backend/app/models.py
```

Important models:

- `HouseSignificatorsChartResponse`
- `HouseSignificatorResponse`
- `HouseSignificatorLevelResponse`
- `SignificatorPlanetResponse`
- `RelatedSignificatorPlanetResponse`

## Notes

- The endpoint always returns all 12 houses.
- House occupation comes from Bhava Chalit.
- Cusp rashi-lord ownership comes from cusp positions.
- Signification numbers are unique, with the occupied house first.
- Rahu/Ketu include their Bhava Chalit rashi lord as an additional related planet.
