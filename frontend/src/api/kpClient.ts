const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type PlaceSearchResult = {
  display_name: string;
  city: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: number;
  elevation: number;
  source: string;
};

export type PlaceSearchResponse = {
  query: string;
  count: number;
  results: PlaceSearchResult[];
};

export type BirthDateTimeRequest = {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
};

export type LocationRequest = {
  name: string;
  latitude: number;
  longitude: number;
  timezone: number;
  elevation?: number;
};

export type KpChartRequest = {
  name: string;
  birth_datetime: BirthDateTimeRequest;
  location: LocationRequest;
  settings: {
    ayanamsa_mode: string;
    house_cusp_method: number | string;
    use_true_nodes: boolean;
    include_western_planets: boolean;
  };
};

export type PositionRow = {
  label: string;
  sign: string;
  sign_index: number;
  dms: string;
  absolute_longitude: number;
  kp: {
    kp_number: number;
    rasi_lord: string;
    star_lord: string;
    sub_lord: string;
    sub_sub_lord: string;
    sookshma_lord: string;
    praana_lord: string;
    deha_lord: string;
  };
};

export type KpChartResponse = {
  name: string;
  birth_datetime: BirthDateTimeRequest;
  location: Required<LocationRequest>;
  settings: KpChartRequest["settings"];
  cusps: PositionRow[];
  planets: PositionRow[];
};

export type PlanetStateFlags = {
  retrograde: boolean;
  combust: boolean;
  exalted: boolean;
  debilitated: boolean;
};

export type D1ChartPlanet = {
  name: string;
  short_name: string;
  sign: string;
  sign_index: number;
  sign_number: number;
  degree: string;
  degree_decimal: number;
  absolute_longitude: number;
  state_flags: PlanetStateFlags;
};

export type D1Ascendant = {
  sign: string;
  sign_index: number;
  sign_number: number;
  degree: string;
  degree_decimal: number;
  absolute_longitude: number;
};

export type D1House = {
  house_number: number;
  sign: string;
  sign_index: number;
  sign_number: number;
  planets: D1ChartPlanet[];
};

export type D1ChartResponse = {
  chart: "D-1" | "Transit";
  chart_style: "north_indian";
  name: string;
  birth_datetime: BirthDateTimeRequest;
  location: Required<LocationRequest>;
  settings: KpChartRequest["settings"];
  ascendant: D1Ascendant;
  houses: D1House[];
};

export type ChartPoint = {
  sign: string;
  sign_index: number;
  sign_number: number;
  degree: string;
  degree_decimal: number;
  absolute_longitude: number;
};

export type BhavaChalitPlanet = {
  name: string;
  short_name: string;
  rashi_sign: string;
  rashi_sign_index: number;
  rashi_sign_number: number;
  degree: string;
  degree_decimal: number;
  absolute_longitude: number;
  bhava_house_number: number;
  state_flags: PlanetStateFlags;
};

export type BhavaChalitHouse = {
  house_number: number;
  display_number: number;
  start: ChartPoint;
  cusp: ChartPoint;
  end: ChartPoint;
  planets: BhavaChalitPlanet[];
};

export type BhavaChalitChartResponse = {
  chart: "Bhava Chalit";
  chart_style: "north_indian";
  name: string;
  birth_datetime: BirthDateTimeRequest;
  location: Required<LocationRequest>;
  settings: KpChartRequest["settings"];
  ascendant: ChartPoint;
  houses: BhavaChalitHouse[];
};

export type RelatedSignificatorPlanet = {
  planet: string;
  short_name: string;
  occupied_house: number | null;
  rashi_lord_houses: number[];
  significations: number[];
};

export type SignificatorPlanet = {
  role: string;
  planet: string;
  short_name: string;
  occupied_house: number | null;
  rashi_lord_houses: number[];
  significations: number[];
  original_planet: string | null;
  original_short_name: string | null;
  is_duplicate_replacement: boolean;
  node_rashi_lord: RelatedSignificatorPlanet | null;
};

export type HouseSignificatorLevel = {
  level: number;
  items: SignificatorPlanet[];
};

export type HouseSignificator = {
  house_number: number;
  source_sub_lord: string;
  source_sub_lord_short_name: string;
  levels: HouseSignificatorLevel[];
};

export type HouseSignificatorsChartResponse = {
  name: string;
  birth_datetime: BirthDateTimeRequest;
  location: Required<LocationRequest>;
  settings: KpChartRequest["settings"];
  houses: HouseSignificator[];
};

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function searchPlaces(query: string, limit = 8): Promise<PlaceSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit)
  });

  return requestJson<PlaceSearchResponse>(`/api/places?${params.toString()}`);
}

export function calculateKpChart(payload: KpChartRequest): Promise<KpChartResponse> {
  return requestJson<KpChartResponse>("/api/kp-chart", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function calculateD1Chart(payload: KpChartRequest): Promise<D1ChartResponse> {
  return requestJson<D1ChartResponse>("/api/chart/d-1", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function calculateTransitChart(
  payload: KpChartRequest
): Promise<D1ChartResponse> {
  return requestJson<D1ChartResponse>("/api/chart/transit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function calculateBhavaChalitChart(
  payload: KpChartRequest
): Promise<BhavaChalitChartResponse> {
  return requestJson<BhavaChalitChartResponse>("/api/chart/bhava-chalit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function calculateHouseSignificators(
  payload: KpChartRequest
): Promise<HouseSignificatorsChartResponse> {
  return requestJson<HouseSignificatorsChartResponse>("/api/kp/house-significators", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
