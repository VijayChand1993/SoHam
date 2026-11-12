# Direct Ruling Planets Calculation

This document explains the logic used to calculate `direct_ruling_planets` in the KP chart API.

## API Output

The calculation is returned as part of:

```text
POST /api/kp-chart
```

Response field:

```json
{
  "direct_ruling_planets": {
    "items": [],
    "unique_planets": []
  }
}
```

`items` keeps every ruling planet role row, including duplicates. `unique_planets` is only a convenience list of unique planet short names.

## Base RP Formula

The backend calculates these base ruling planets from the KP chart details:

| RP | Source | Meaning |
| --- | --- | --- |
| RP1 | Ascendant cusp Rashi Lord | Rashi lord of House 1 cusp |
| RP2 | Moon Star Lord | Star lord of Moon |
| RP3 | Moon Rashi Lord | Rashi lord of Moon |
| RP4 | Day Lord | Planet ruling the weekday of the chart date |
| RP5 | Moon | Moon itself is always added as a ruling planet |

Duplicates are intentionally preserved. For example, if Moon appears as both RP3 and RP5, both rows remain in `items`.

## Day Lord Mapping

The weekday is calculated from the chart date, and mapped as:

| Weekday | Day Lord |
| --- | --- |
| Sunday | Sun |
| Monday | Moon |
| Tuesday | Mars |
| Wednesday | Mercury |
| Thursday | Jupiter |
| Friday | Venus |
| Saturday | Saturn |

## Rahu/Ketu Transit Rule

Rahu or Ketu can become an additional ruling planet only through current transit.

The backend calculates the current transit D1 chart at request time using:

- the same selected location
- the same timezone
- the same ayanamsa/settings

Then it checks:

1. Build the set of signs owned by the base RP planets.
2. Look at current transit Rahu and Ketu sign placement in the D1/Rashi chart.
3. If transit Rahu or transit Ketu is placed in a sign owned by one of the base RP planets, add that node as an additional ruling planet.

Important: birth-time Rahu/Ketu placement is not used for this inclusion rule.

## Enrichment Fields

Each ruling planet row includes extra context from the chart:

```json
{
  "label": "RP1",
  "role": "asc_rashi_lord",
  "planet": "Jupiter",
  "short_name": "Ju",
  "state_flags": {
    "retrograde": false,
    "combust": false,
    "exalted": false,
    "debilitated": false
  },
  "bhava_house_number": 9,
  "house_rashi_lord": "Mercury",
  "house_rashi_lord_short_name": "Me",
  "rashi": "Virgo",
  "rashi_number": 6,
  "reason": null
}
```

`state_flags` is calculated from the current transit position of that planet at request time. The same selected location, timezone, ayanamsa, and settings are used for this transit-state snapshot.

These details are resolved from Bhava Chalit placement:

- `bhava_house_number`: house where the RP planet is placed in Bhava Chalit
- `rashi`: cusp sign/rashi name of that Bhava Chalit house
- `rashi_number`: Aries = 1 through Pisces = 12
- `house_rashi_lord`: rashi lord of that Bhava Chalit house

For transit node rows, `reason` explains why the node was included, for example:

```text
Transit Rahu is in Aquarius, ruled by Saturn
```

## Code Locations

Main implementation:

```text
backend/kp_core.py
```

Important helpers:

- `_direct_ruling_planets(...)`
- `_direct_ruling_planet_item(...)`
- `_transit_node_ruling_planets(...)`
- `_bhava_house_context(...)`
- `_day_lord(...)`

API response models:

```text
backend/app/models.py
```

Important models:

- `DirectRulingPlanetItemResponse`
- `DirectRulingPlanetsResponse`

## Notes

- RP calculation is attached to the KP chart response because RP1, RP2, and RP3 depend directly on KP details.
- Bhava Chalit is used for the house/rashi context of each RP planet.
- D1/Rashi transit is used only for checking whether current transit Rahu/Ketu should be added.
- The backend keeps duplicate RP role rows by design.
