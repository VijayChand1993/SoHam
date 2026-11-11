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
