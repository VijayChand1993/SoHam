from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    BhavaChalitChartResponse,
    D1ChartResponse,
    HealthResponse,
    HouseSignificatorsChartResponse,
    KpChartRequest,
    KpChartResponse,
    PlaceSearchResponse,
)
from app.services.kp_calculator import (
    calculate_bhava_chalit_chart_response,
    calculate_chart_response,
    calculate_d1_chart_response,
    calculate_house_significators_response,
    calculate_transit_chart_response,
)
from app.services.places import search_places

app = FastAPI(title="SoHam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/places", response_model=PlaceSearchResponse)
def places(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=25),
) -> PlaceSearchResponse:
    try:
        results = search_places(q, limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PlaceSearchResponse(query=q, count=len(results), results=results)


@app.post("/api/kp-chart", response_model=KpChartResponse)
def kp_chart(request: KpChartRequest) -> KpChartResponse:
    try:
        return calculate_chart_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chart/d-1", response_model=D1ChartResponse)
def d1_chart(request: KpChartRequest) -> D1ChartResponse:
    try:
        return calculate_d1_chart_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chart/transit", response_model=D1ChartResponse)
def transit_chart(request: KpChartRequest) -> D1ChartResponse:
    try:
        return calculate_transit_chart_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chart/bhava-chalit", response_model=BhavaChalitChartResponse)
def bhava_chalit_chart(request: KpChartRequest) -> BhavaChalitChartResponse:
    try:
        return calculate_bhava_chalit_chart_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/kp/house-significators", response_model=HouseSignificatorsChartResponse)
def house_significators(request: KpChartRequest) -> HouseSignificatorsChartResponse:
    try:
        return calculate_house_significators_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
