import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { LoaderCircle, LocateFixed } from "lucide-react";

import {
  BhavaChalitChartResponse,
  calculateBhavaChalitChart,
  calculateD1Chart,
  calculateHouseSignificators,
  calculateInstantPrashna,
  calculateKpChart,
  calculateTransitChart,
  BirthDateTimeRequest,
  D1ChartPlanet,
  D1ChartResponse,
  D1House,
  HouseSignificator,
  HouseSignificatorsChartResponse,
  KpChartRequest,
  KpChartResponse,
  PlaceSearchResult,
  PositionRow,
  reversePlace,
  SignificatorPlanet,
  searchPlaces
} from "./api/kpClient";
import { NorthIndianChart } from "./components/NorthIndianChart";

const defaultDate = "1993-04-02";
const defaultTime = "01:15:00";

type LocationMode = "place" | "coordinates";
type ChartMode = "birth_chart" | "instant_prashna";
type ChartResult = {
  chart: KpChartResponse;
  d1Chart: D1ChartResponse;
  bhavaChalitChart: BhavaChalitChartResponse;
  houseSignificators: HouseSignificatorsChartResponse;
  instantPrashnaDateTime: BirthDateTimeRequest | null;
};

function CurrentLocationButton({
  isLoading,
  onClick
}: {
  isLoading: boolean;
  onClick: () => void;
}) {
  return (
    <button
      aria-label="Use current location"
      className="inline-grid min-h-10 min-w-10 cursor-pointer place-items-center rounded-md border border-[#214668] bg-white text-[#214668] disabled:cursor-wait disabled:opacity-65"
      disabled={isLoading}
      title={isLoading ? "Detecting current location" : "Use current location"}
      type="button"
      onClick={onClick}
    >
      {isLoading ? (
        <LoaderCircle aria-hidden="true" className="h-4 w-4 animate-spin" />
      ) : (
        <LocateFixed aria-hidden="true" className="h-4 w-4" />
      )}
    </button>
  );
}

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

function currentDateTimeForTimezone(timezone: number) {
  const now = new Date();
  const localTime = new Date(now.getTime() + timezone * 60 * 60 * 1000);

  return {
    year: localTime.getUTCFullYear(),
    month: localTime.getUTCMonth() + 1,
    day: localTime.getUTCDate(),
    hour: localTime.getUTCHours(),
    minute: localTime.getUTCMinutes(),
    second: localTime.getUTCSeconds()
  };
}

function formatCalculatedDateTime(
  dateTime: BirthDateTimeRequest,
  timezoneOffset: number
) {
  const formatter = new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "UTC"
  });
  const displayDate = new Date(
    Date.UTC(
      dateTime.year,
      dateTime.month - 1,
      dateTime.day,
      dateTime.hour,
      dateTime.minute,
      dateTime.second
    )
  );
  const timezoneLabel = `UTC${timezoneOffset >= 0 ? "+" : ""}${timezoneOffset}`;

  return `${formatter.format(displayDate)} ${timezoneLabel}`;
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

function formatHouseList(values: number[]) {
  return values.length ? values.join(", ") : "-";
}

function formatSignificatorText(item: SignificatorPlanet) {
  return `${item.short_name} ${formatHouseList(item.significations)}`;
}

function SignificatorCell({ item }: { item?: SignificatorPlanet }) {
  if (!item) {
    return <span className="text-[#9aa5b1]">-</span>;
  }

  return (
    <div className="grid gap-1">
      <div className="font-semibold text-[#18202b]">
        {formatSignificatorText(item)}
      </div>
      {item.node_rashi_lord && (
        <div className="text-xs text-[#5d6876]">
          {item.node_rashi_lord.short_name} RL {formatHouseList(item.node_rashi_lord.rashi_lord_houses)}
        </div>
      )}
      {item.is_duplicate_replacement && item.original_short_name && (
        <div className="text-xs text-[#5d6876]">
          {item.original_short_name} replaced by {item.short_name}
        </div>
      )}
    </div>
  );
}

function significatorRows(house: HouseSignificator) {
  const level1 = house.levels.find((level) => level.level === 1)?.items ?? [];
  const level2 = house.levels.find((level) => level.level === 2)?.items ?? [];
  const level3 = house.levels.find((level) => level.level === 3)?.items ?? [];

  return [
    { label: "SL", primary: level1[0], secondary: undefined },
    { label: "STL", primary: level2[0], secondary: level3[0] },
    { label: "SL", primary: level2[1], secondary: level3[1] }
  ];
}

function HouseSignificatorModal({
  house,
  onClose
}: {
  house: HouseSignificator;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-[#18202b]/45 p-4"
      role="presentation"
      onMouseDown={onClose}
    >
      <div
        aria-modal="true"
        className="max-h-[86vh] w-full max-w-[860px] overflow-auto rounded-lg border border-[#d8e0e8] bg-white p-5 shadow-xl"
        role="dialog"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h2 className="m-0 text-lg">House {house.house_number} Significators</h2>
            <div className="text-sm text-[#5d6876]">SL {house.source_sub_lord_short_name}</div>
          </div>
          <button
            aria-label="Close"
            className="min-h-8 min-w-8 rounded-md border border-[#b9c4cf] bg-white px-2 text-[#314154]"
            type="button"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] border-collapse">
            <thead>
              <tr>
                <th className="w-24 border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs uppercase">Lord</th>
                <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs uppercase">Planet</th>
                <th className="border-b border-[#d8e0e8] bg-[#f0f4f8] px-2.5 py-[9px] text-left text-xs uppercase">STL</th>
              </tr>
            </thead>
            <tbody>
              {significatorRows(house).map((row, index) => (
                <tr key={`${row.label}-${index}`}>
                  <td className="border-b border-[#d8e0e8] px-2.5 py-[11px] align-top font-semibold whitespace-nowrap">
                    {row.label}
                  </td>
                  <td className="border-b border-[#d8e0e8] px-2.5 py-[11px] align-top">
                    <SignificatorCell item={row.primary} />
                  </td>
                  <td className="border-b border-[#d8e0e8] px-2.5 py-[11px] align-top">
                    <SignificatorCell item={row.secondary} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ResultsTable({
  rows,
  onNameClick
}: {
  rows: PositionRow[];
  onNameClick?: (row: PositionRow, index: number) => void;
}) {
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
          {rows.map((row, index) => (
            <tr key={row.label}>
              <td className="border-b border-[#d8e0e8] px-2.5 py-[9px] text-left whitespace-nowrap">
                {onNameClick ? (
                  <button
                    className="cursor-pointer font-semibold text-[#214668] underline-offset-2 hover:underline"
                    type="button"
                    onClick={() => onNameClick(row, index)}
                  >
                    {row.label}
                  </button>
                ) : (
                  row.label
                )}
              </td>
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
  const [chartMode, setChartMode] = useState<ChartMode>("birth_chart");
  const [birthChartResult, setBirthChartResult] = useState<ChartResult | null>(
    null
  );
  const [instantPrashnaResult, setInstantPrashnaResult] =
    useState<ChartResult | null>(null);
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
  const [selectedSignificatorHouse, setSelectedSignificatorHouse] =
    useState<HouseSignificator | null>(null);
  const [isTransitEnabled, setIsTransitEnabled] = useState(false);
  const [isTransitLoading, setIsTransitLoading] = useState(false);
  const [transitChart, setTransitChart] = useState<D1ChartResponse | null>(null);
  const [transitError, setTransitError] = useState("");
  const [status, setStatus] = useState("");
  const [isSearchingPlaces, setIsSearchingPlaces] = useState(false);
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const latestPlaceSearchId = useRef(0);
  const latestTransitRequestId = useRef(0);
  const activeResult =
    chartMode === "instant_prashna" ? instantPrashnaResult : birthChartResult;
  const chart = activeResult?.chart ?? null;
  const d1Chart = activeResult?.d1Chart ?? null;
  const bhavaChalitChart = activeResult?.bhavaChalitChart ?? null;
  const houseSignificators = activeResult?.houseSignificators ?? null;
  const instantPrashnaDateTime =
    activeResult?.instantPrashnaDateTime ?? null;

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

  function buildSettings() {
    return {
      ayanamsa_mode: "KP",
      house_cusp_method: 3,
      use_true_nodes: false,
      include_western_planets: includeWesternPlanets
    };
  }

  function buildChartPayload(): KpChartRequest {
    return {
      name,
      birth_datetime: parseDateTime(date, time),
      location: getRequestLocation(),
      settings: buildSettings()
    };
  }

  function buildTransitPayload(): KpChartRequest {
    const location = getRequestLocation();

    return {
      name: "Today's Transit",
      birth_datetime: currentDateTimeForTimezone(location.timezone),
      location,
      settings: buildSettings()
    };
  }

  function buildInstantPrashnaPayload() {
    return {
      location: getRequestLocation(),
      settings: buildSettings()
    };
  }

  function resetTransitOverlay() {
    latestTransitRequestId.current += 1;
    setIsTransitEnabled(false);
    setTransitChart(null);
    setTransitError("");
    setIsTransitLoading(false);
  }

  function handleChartModeChange(nextMode: ChartMode) {
    setChartMode(nextMode);
    setSelectedSignificatorHouse(null);
    setStatus("");
    resetTransitOverlay();
  }

  function geolocationErrorMessage(error: GeolocationPositionError) {
    if (error.code === error.PERMISSION_DENIED) {
      return "Location permission denied.";
    }

    if (error.code === error.TIMEOUT) {
      return "Unable to detect location before timeout.";
    }

    return "Unable to detect location.";
  }

  function fillManualCoordinates(
    latitude: number,
    longitude: number,
    timezone: number
  ) {
    setManualLatitude(latitude.toFixed(6));
    setManualLongitude(longitude.toFixed(6));
    setManualTimezone(String(timezone));
  }

  async function applyDetectedLocation(position: GeolocationPosition) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    const browserTimezone = -new Date().getTimezoneOffset() / 60;

    fillManualCoordinates(latitude, longitude, browserTimezone);

    if (locationMode === "coordinates") {
      setStatus("Current location filled.");
      return;
    }

    try {
      const response = await reversePlace(latitude, longitude);
      if (!response.result) {
        setSelectedPlace(null);
        setPlaceResults([]);
        setStatus("Current coordinates detected, but no nearby place was found.");
        return;
      }

      setSelectedPlace(response.result);
      setPlaceQuery(response.result.display_name);
      setPlaceResults([]);

      const distanceText =
        response.distance_km === null
          ? ""
          : ` (${response.distance_km.toFixed(1)} km away)`;
      setStatus(`Nearest place selected: ${response.result.display_name}${distanceText}.`);
    } catch (error) {
      setSelectedPlace(null);
      setPlaceResults([]);
      setStatus(
        error instanceof Error
          ? `Current coordinates detected, but nearest place lookup failed: ${error.message}`
          : "Current coordinates detected, but nearest place lookup failed."
      );
    }
  }

  function handleUseCurrentLocation() {
    if (!navigator.geolocation) {
      setStatus("Browser location is not available.");
      return;
    }

    setIsDetectingLocation(true);
    setStatus("Detecting current location...");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        void applyDetectedLocation(position).finally(() => {
          setIsDetectingLocation(false);
        });
      },
      (error) => {
        setStatus(geolocationErrorMessage(error));
        setIsDetectingLocation(false);
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 10000
      }
    );
  }

  async function loadTransitChart() {
    latestTransitRequestId.current += 1;
    const requestId = latestTransitRequestId.current;
    setIsTransitLoading(true);
    setTransitError("");

    try {
      const response = await calculateTransitChart(buildTransitPayload());
      if (latestTransitRequestId.current !== requestId) {
        return;
      }

      setTransitChart(response);
    } catch (error) {
      if (latestTransitRequestId.current !== requestId) {
        return;
      }

      setTransitChart(null);
      setIsTransitEnabled(false);
      setTransitError(error instanceof Error ? error.message : "Transit calculation failed.");
    } finally {
      if (latestTransitRequestId.current === requestId) {
        setIsTransitLoading(false);
      }
    }
  }

  function handleTransitToggle(checked: boolean) {
    setIsTransitEnabled(checked);

    if (!checked) {
      latestTransitRequestId.current += 1;
      setTransitChart(null);
      setTransitError("");
      setIsTransitLoading(false);
      return;
    }

    void loadTransitChart();
  }

  const transitPlanetsByHouse = useMemo(() => {
    if (!d1Chart || !transitChart) {
      return undefined;
    }

    const natalHouseBySign = new Map(
      d1Chart.houses.map((house) => [house.sign_number, house.house_number])
    );
    const byHouse: Record<number, D1ChartPlanet[]> = {};

    transitChart.houses.forEach((house) => {
      house.planets.forEach((planet) => {
        if (planet.short_name === "Asc") {
          return;
        }

        const natalHouseNumber = natalHouseBySign.get(planet.sign_number);
        if (!natalHouseNumber) {
          return;
        }

        byHouse[natalHouseNumber] = [
          ...(byHouse[natalHouseNumber] ?? []),
          planet
        ];
      });
    });

    return byHouse;
  }, [d1Chart, transitChart]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus(
      chartMode === "instant_prashna"
        ? "Calculating Instant Prashna..."
        : "Calculating chart..."
    );
    setIsCalculating(true);
    resetTransitOverlay();

    try {
      if (chartMode === "instant_prashna") {
        const instantPrashnaResponse = await calculateInstantPrashna(
          buildInstantPrashnaPayload()
        );

        setInstantPrashnaResult({
          chart: instantPrashnaResponse.kp_chart,
          d1Chart: instantPrashnaResponse.d1_chart,
          bhavaChalitChart: instantPrashnaResponse.bhava_chalit_chart,
          houseSignificators: instantPrashnaResponse.house_significators,
          instantPrashnaDateTime: instantPrashnaResponse.calculated_datetime
        });
        setSelectedSignificatorHouse(null);
        setStatus("Instant Prashna calculated.");
        return;
      }

      const payload = buildChartPayload();
      const [
        kpResponse,
        d1Response,
        bhavaChalitResponse,
        houseSignificatorsResponse
      ] = await Promise.all([
        calculateKpChart(payload),
        calculateD1Chart(payload),
        calculateBhavaChalitChart(payload),
        calculateHouseSignificators(payload)
      ]);

      setBirthChartResult({
        chart: kpResponse,
        d1Chart: d1Response,
        bhavaChalitChart: bhavaChalitResponse,
        houseSignificators: houseSignificatorsResponse,
        instantPrashnaDateTime: null
      });
      setSelectedSignificatorHouse(null);
      setStatus("Chart calculated.");
    } catch (error) {
      if (chartMode === "instant_prashna") {
        setInstantPrashnaResult(null);
      } else {
        setBirthChartResult(null);
      }
      setSelectedSignificatorHouse(null);
      setTransitChart(null);
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
          <div
            className="inline-grid w-full grid-cols-2 rounded-lg border border-[#cbd5df] bg-[#eef3f7] p-[3px] sm:w-[380px]"
            role="tablist"
            aria-label="Chart calculation mode"
          >
            <button
              aria-selected={chartMode === "birth_chart"}
              className={`min-h-[34px] cursor-pointer rounded-md px-3.5 text-[#314154] ${
                chartMode === "birth_chart"
                  ? "border border-[#b9c4cf] bg-white text-[#18202b]"
                  : "border border-transparent bg-transparent"
              }`}
              type="button"
              onClick={() => handleChartModeChange("birth_chart")}
            >
              Birth Chart
            </button>
            <button
              aria-selected={chartMode === "instant_prashna"}
              className={`min-h-[34px] cursor-pointer rounded-md px-3.5 text-[#314154] ${
                chartMode === "instant_prashna"
                  ? "border border-[#b9c4cf] bg-white text-[#18202b]"
                  : "border border-transparent bg-transparent"
              }`}
              type="button"
              onClick={() => handleChartModeChange("instant_prashna")}
            >
              Instant Prashna
            </button>
          </div>

          {chartMode === "birth_chart" && (
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
          )}

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
                  <span className="flex gap-2">
                    <span className="relative grow">
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
                    <CurrentLocationButton
                      isLoading={isDetectingLocation}
                      onClick={handleUseCurrentLocation}
                    />
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
              <div className="grid gap-3.5">
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
                    <span className="flex gap-2">
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
                      <CurrentLocationButton
                        isLoading={isDetectingLocation}
                        onClick={handleUseCurrentLocation}
                      />
                    </span>
                  </label>
                </div>
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
            {chartMode === "instant_prashna"
              ? "Calculate Instant Prashna"
              : "Calculate"}
          </button>
        </form>

        {status && <div className="text-sm text-[#5d6876]">{status}</div>}
      </section>

      {(chart || d1Chart || bhavaChalitChart) && (
        <section className="grid gap-6 rounded-lg border border-[#d8e0e8] bg-white p-5">
          {chartMode === "instant_prashna" && instantPrashnaDateTime && chart && (
            <div className="rounded-md border border-[#d8e0e8] bg-[#f5f7fa] px-3 py-2 text-sm text-[#5d6876]">
              Instant Prashna calculated for:{" "}
              {formatCalculatedDateTime(
                instantPrashnaDateTime,
                chart.location.timezone
              )}
            </div>
          )}

          {(d1Chart || bhavaChalitChart) && (
            <div className="grid gap-6 lg:grid-cols-2">
              {d1Chart && (
                <div>
                  <div className="mb-2.5 flex flex-wrap items-center gap-3">
                    <h2 className="m-0 text-lg">Rashi Chart</h2>
                    <label className="flex items-center gap-2 text-[13px] font-semibold text-[#314154]">
                      <input
                        checked={isTransitEnabled}
                        className="h-4 w-4 accent-[#b42318]"
                        disabled={isTransitLoading}
                        type="checkbox"
                        onChange={(event) => handleTransitToggle(event.target.checked)}
                      />
                      Today's Transit
                      {isTransitLoading && (
                        <span
                          aria-label="Loading transit"
                          className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-[#f3c2bd] border-t-[#b42318]"
                        />
                      )}
                    </label>
                  </div>
                  <NorthIndianChart
                    houses={d1Chart.houses}
                    transitPlanetsByHouse={
                      isTransitEnabled ? transitPlanetsByHouse : undefined
                    }
                  />
                  {transitError && (
                    <div className="mt-2 text-sm text-[#b42318]">{transitError}</div>
                  )}
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
                <ResultsTable
                  rows={chart.cusps}
                  onNameClick={(_, index) => {
                    const house = houseSignificators?.houses[index];
                    if (house) {
                      setSelectedSignificatorHouse(house);
                    }
                  }}
                />
              </div>

              <div>
                <h2 className="mb-2.5 text-lg">Planetary Positions</h2>
                <ResultsTable rows={chart.planets} />
              </div>
            </>
          )}
        </section>
      )}
      {selectedSignificatorHouse && (
        <HouseSignificatorModal
          house={selectedSignificatorHouse}
          onClose={() => setSelectedSignificatorHouse(null)}
        />
      )}
      </div>
    </main>
  );
}
