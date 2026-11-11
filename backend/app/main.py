from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    HealthResponse,
    KpChartRequest,
    KpChartResponse,
    PlaceSearchResponse,
)
from app.services.kp_calculator import calculate_chart_response
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
