import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import {
  BhavaChalitChartResponse,
  calculateBhavaChalitChart,
  calculateD1Chart,
  calculateKpChart,
  D1ChartResponse,
  D1House,
  KpChartResponse,
  PlaceSearchResult,
  PositionRow,
  searchPlaces
} from "./api/kpClient";
import { NorthIndianChart } from "./components/NorthIndianChart";

const defaultDate = "1993-04-02";
const defaultTime = "01:15:00";

type LocationMode = "place" | "coordinates";

const defaultPlaces: PlaceSearchResult[] = [
  {
    display_name: "Delhi, India",
    city: "Delhi",
    state: "Delhi",
    country: "India",
    latitude: 28.6139,
    longitude: 77.209,
    timezone: 5.5,
    elevation: 0,
    source: "default"
  },
  {
    display_name: "Mumbai, Maharashtra, India",
    city: "Mumbai",
    state: "Maharashtra",
    country: "India",
    latitude: 19.076,
    longitude: 72.8777,
    timezone: 5.5,
    elevation: 0,
    source: "default"
  },
  {
    display_name: "Bangalore, Karnataka, India",
    city: "Bangalore",
    state: "Karnataka",
    country: "India",
    latitude: 12.9716,
    longitude: 77.5946,
    timezone: 5.5,
    elevation: 0,
    source: "default"
  },
  {
    display_name: "Chennai, Tamil Nadu, India",
    city: "Chennai",
    state: "Tamil Nadu",
    country: "India",
    latitude: 13.0878,
    longitude: 80.2785,
    timezone: 5.5,
    elevation: 14,
    source: "default"
  },
  {
    display_name: "Kolkata, West Bengal, India",
    city: "Kolkata",
    state: "West Bengal",
    country: "India",
    latitude: 22.5726,
    longitude: 88.3639,
    timezone: 5.5,
    elevation: 0,
    source: "default"
  }
];

function parseDateTime(dateValue: string, timeValue: string) {
  const [year, month, day] = dateValue.split("-").map(Number);
  const [hour, minute, second = 0] = timeValue.split(":").map(Number);

  return { year, month, day, hour, minute, second };
}

function parseCoordinate(value: string, label: string, min: number, max: number) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`${label} must be between ${min} and ${max}.`);
  }

  return parsed;
}

function adaptBhavaChalitHouses(chart: BhavaChalitChartResponse): D1House[] {
  return chart.houses.map((house) => ({
    house_number: house.house_number,
    sign: house.cusp.sign,
    sign_index: house.cusp.sign_index,
    sign_number: house.display_number,
    planets: house.planets.map((planet) => ({
      name: planet.name,
      short_name: planet.short_name,
      sign: planet.rashi_sign,
      sign_index: planet.rashi_sign_index,
      sign_number: planet.rashi_sign_number,
      degree: planet.degree,
      degree_decimal: planet.degree_decimal,
      absolute_longitude: planet.absolute_longitude,
      state_flags: planet.state_flags
    }))
  }));
}

function ResultsTable({ rows }: { rows: PositionRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[820px] border-collapse">
        <thead>
          <tr>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">Name</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">Sign</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">D-M-S</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">RL</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">STL</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">SL</th>
            <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs whitespace-nowrap uppercase">SSL</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.label}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.sign}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.dms}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.kp.rasi_lord}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.kp.star_lord}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.kp.sub_lord}</td>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">{row.kp.sub_sub_lord}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [name, setName] = useState("VJ");
  const [date, setDate] = useState(defaultDate);
  const [time, setTime] = useState(defaultTime);
  const [locationMode, setLocationMode] = useState<LocationMode>("place");
  const [placeQuery, setPlaceQuery] = useState("");
  const [placeResults, setPlaceResults] = useState<PlaceSearchResult[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<PlaceSearchResult | null>(null);
  const [manualLatitude, setManualLatitude] = useState("29.418");
  const [manualLongitude, setManualLongitude] = useState("80.207");
  const [manualTimezone, setManualTimezone] = useState("5.5");
  const [includeWesternPlanets, setIncludeWesternPlanets] = useState(false);
  const [chart, setChart] = useState<KpChartResponse | null>(null);
  const [d1Chart, setD1Chart] = useState<D1ChartResponse | null>(null);
  const [bhavaChalitChart, setBhavaChalitChart] =
    useState<BhavaChalitChartResponse | null>(null);
  const [status, setStatus] = useState("");
  const [isSearchingPlaces, setIsSearchingPlaces] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const latestPlaceSearchId = useRef(0);

  const selectedPlaceLabel = useMemo(() => {
    if (!selectedPlace) {
      return "No place selected";
    }

    return `${selectedPlace.display_name} (${selectedPlace.latitude}, ${selectedPlace.longitude}, UTC${selectedPlace.timezone >= 0 ? "+" : ""}${selectedPlace.timezone})`;
  }, [selectedPlace]);

  const visiblePlaces = useMemo(() => {
    const queryLength = placeQuery.trim().length;
    if (queryLength === 0) {
      return defaultPlaces;
    }

    if (queryLength < 3) {
      return [];
    }

    return placeResults.slice(0, 8);
  }, [placeQuery, placeResults]);

  useEffect(() => {
    const query = placeQuery.trim();
    latestPlaceSearchId.current += 1;
    const searchId = latestPlaceSearchId.current;

    if (locationMode !== "place") {
      setIsSearchingPlaces(false);
      return;
    }

    if (query.length < 3) {
      setPlaceResults([]);
      setIsSearchingPlaces(false);
      return;
    }

    setIsSearchingPlaces(true);

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await searchPlaces(query, 8);
        if (latestPlaceSearchId.current !== searchId) {
          return;
        }

        setPlaceResults(response.results);
        if (!response.count) {
          setStatus("No matching places found.");
        }
      } catch (error) {
        if (latestPlaceSearchId.current !== searchId) {
          return;
        }

        setStatus(error instanceof Error ? error.message : "Place search failed.");
      } finally {
        if (latestPlaceSearchId.current === searchId) {
          setIsSearchingPlaces(false);
        }
      }
    }, 300);

    return () => window.clearTimeout(timeoutId);
  }, [locationMode, placeQuery]);

  function getRequestLocation() {
    if (locationMode === "place") {
      if (!selectedPlace) {
        throw new Error("Select a place before calculating.");
      }

      return {
        name: selectedPlace.display_name,
        latitude: selectedPlace.latitude,
        longitude: selectedPlace.longitude,
        timezone: selectedPlace.timezone,
        elevation: selectedPlace.elevation
      };
    }

    return {
      name: "Manual coordinates",
      latitude: parseCoordinate(manualLatitude, "Latitude", -90, 90),
      longitude: parseCoordinate(manualLongitude, "Longitude", -180, 180),
      timezone: parseCoordinate(manualTimezone, "Timezone", -14, 14),
      elevation: 0
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Calculating chart...");
    setIsCalculating(true);

    try {
      const payload = {
        name,
        birth_datetime: parseDateTime(date, time),
        location: getRequestLocation(),
        settings: {
          ayanamsa_mode: "KP",
          house_cusp_method: 3,
          use_true_nodes: false,
          include_western_planets: includeWesternPlanets
        }
      };
      const [kpResponse, d1Response, bhavaChalitResponse] = await Promise.all([
        calculateKpChart(payload),
        calculateD1Chart(payload),
        calculateBhavaChalitChart(payload)
      ]);

      setChart(kpResponse);
      setD1Chart(d1Response);
      setBhavaChalitChart(bhavaChalitResponse);
      setStatus("Chart calculated.");
    } catch (error) {
      setChart(null);
      setD1Chart(null);
      setBhavaChalitChart(null);
      setStatus(error instanceof Error ? error.message : "Chart calculation failed.");
    } finally {
      setIsCalculating(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f5f7fa] px-4 py-4 font-sans text-[#18202b] sm:px-7 sm:py-7">
      <div className="mx-auto grid max-w-[1180px] gap-6">
      <section className="grid gap-[18px] rounded-lg border border-[#d8e0e8] bg-white p-5">
        <div>
          <h1 className="m-0 text-[28px]">SoHam</h1>
          <p className="m-0 text-sm text-[#5d6876]">FastAPI backend at http://127.0.0.1:8000</p>
        </div>

        <form className="grid gap-3.5" onSubmit={handleSubmit}>
          <div className="grid gap-3.5 md:grid-cols-3">
            <label className="grid gap-1.5 text-[13px] font-semibold">
              Name
              <input
                className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label className="grid gap-1.5 text-[13px] font-semibold">
              Date
              <input
                className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                type="date"
                value={date}
                onChange={(event) => setDate(event.target.value)}
              />
            </label>
            <label className="grid gap-1.5 text-[13px] font-semibold">
              Time
              <input
                className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                type="time"
                step="1"
                value={time}
                onChange={(event) => setTime(event.target.value)}
              />
            </label>
          </div>

          <div
            className="inline-grid w-full grid-cols-2 rounded-lg border border-[#cbd5df] bg-[#eef3f7] p-[3px] sm:w-[340px]"
            role="tablist"
            aria-label="Location input mode"
          >
            <button
              aria-selected={locationMode === "place"}
              className={`min-h-[34px] cursor-pointer rounded-md px-3.5 text-[#314154] ${
                locationMode === "place"
                  ? "border border-[#b9c4cf] bg-white text-[#18202b]"
                  : "border border-transparent bg-transparent"
              }`}
              type="button"
              onClick={() => setLocationMode("place")}
            >
              Search Place
            </button>
            <button
              aria-selected={locationMode === "coordinates"}
              className={`min-h-[34px] cursor-pointer rounded-md px-3.5 text-[#314154] ${
                locationMode === "coordinates"
                  ? "border border-[#b9c4cf] bg-white text-[#18202b]"
                  : "border border-transparent bg-transparent"
              }`}
              type="button"
              onClick={() => setLocationMode("coordinates")}
            >
              Coordinates
            </button>
          </div>

          <div className="grid min-h-[360px] content-start gap-3.5 md:min-h-[238px]">
            {locationMode === "place" ? (
              <>
                <label className="grid gap-1.5 text-[13px] font-semibold">
                  Place
                  <span className="relative">
                    <input
                      className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2 pr-9"
                      value={placeQuery}
                      onChange={(event) => {
                        setPlaceQuery(event.target.value);
                        setSelectedPlace(null);
                        setStatus("");
                      }}
                    />
                    {isSearchingPlaces && (
                      <span
                        aria-label="Searching places"
                        className="pointer-events-none absolute top-1/2 right-3 h-4 w-4 -translate-y-1/2 animate-spin rounded-full border-2 border-[#cbd5df] border-t-[#214668]"
                      />
                    )}
                  </span>
                </label>

                {visiblePlaces.length > 0 && (
                  <div className="grid max-w-[960px] grid-cols-1 gap-1.5 md:grid-cols-4">
                    {visiblePlaces.map((place) => (
                      <button
                        className="min-h-11 cursor-pointer rounded-md border border-[#b9c4cf] bg-[#eef3f7] px-3.5 py-2 text-left break-words text-[#18202b]"
                        type="button"
                        key={`${place.display_name}-${place.latitude}-${place.longitude}`}
                        onClick={() => {
                          setSelectedPlace(place);
                          setPlaceResults([]);
                          setStatus("");
                        }}
                      >
                        {place.display_name}
                      </button>
                    ))}
                  </div>
                )}

                <div className="rounded-md border border-[#d8e0e8] bg-[#f5f7fa] p-2.5 text-sm text-[#5d6876]">
                  {selectedPlaceLabel}
                </div>
              </>
            ) : (
              <div className="grid gap-3.5 md:grid-cols-3">
                <label className="grid gap-1.5 text-[13px] font-semibold">
                  Latitude
                  <input
                    className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                    inputMode="decimal"
                    max="90"
                    min="-90"
                    required
                    step="any"
                    type="number"
                    value={manualLatitude}
                    onChange={(event) => setManualLatitude(event.target.value)}
                  />
                </label>
                <label className="grid gap-1.5 text-[13px] font-semibold">
                  Longitude
                  <input
                    className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                    inputMode="decimal"
                    max="180"
                    min="-180"
                    required
                    step="any"
                    type="number"
                    value={manualLongitude}
                    onChange={(event) => setManualLongitude(event.target.value)}
                  />
                </label>
                <label className="grid gap-1.5 text-[13px] font-semibold">
                  Timezone
                  <input
                    className="min-h-10 w-full rounded-md border border-[#b9c4cf] px-2.5 py-2"
                    inputMode="decimal"
                    max="14"
                    min="-14"
                    required
                    step="any"
                    type="number"
                    value={manualTimezone}
                    onChange={(event) => setManualTimezone(event.target.value)}
                  />
                </label>
              </div>
            )}
          </div>

          <label className="flex items-center gap-2 text-[13px] font-semibold">
            <input
              checked={includeWesternPlanets}
              className="h-4 w-4 accent-[#214668]"
              type="checkbox"
              onChange={(event) => setIncludeWesternPlanets(event.target.checked)}
            />
            Include Uranus, Neptune, Pluto
          </label>

          <button
            className="min-h-10 cursor-pointer rounded-md border border-[#214668] bg-[#214668] px-3.5 text-white disabled:cursor-wait disabled:opacity-65"
            type="submit"
            disabled={isCalculating}
          >
            Calculate
          </button>
        </form>

        {status && <div className="text-sm text-[#5d6876]">{status}</div>}
      </section>

      {(chart || d1Chart || bhavaChalitChart) && (
        <section className="grid gap-6 rounded-lg border border-[#d8e0e8] bg-white p-5">
          {(d1Chart || bhavaChalitChart) && (
            <div className="grid gap-6 lg:grid-cols-2">
              {d1Chart && (
                <div>
                  <h2 className="mb-2.5 text-lg">Rashi Chart</h2>
                  <NorthIndianChart houses={d1Chart.houses} />
                </div>
              )}

              {bhavaChalitChart && (
                <div>
                  <h2 className="mb-2.5 text-lg">Bhava Chalit</h2>
                  <NorthIndianChart houses={adaptBhavaChalitHouses(bhavaChalitChart)} />
                </div>
              )}
            </div>
          )}

          {chart && (
            <>
              <div>
                <h2 className="mb-2.5 text-lg">Cuspal Positions</h2>
                <ResultsTable rows={chart.cusps} />
              </div>

              <div>
                <h2 className="mb-2.5 text-lg">Planetary Positions</h2>
                <ResultsTable rows={chart.planets} />
              </div>
            </>
          )}
        </section>
      )}
      </div>
    </main>
  );
}
