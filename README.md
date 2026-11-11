# SoHam

Monorepo layout:

```text
backend/   FastAPI API and KP calculation code
frontend/  Vite + React + TypeScript UI
```

## Backend

Run the API server:

```bash
cd backend
uv run python -m uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Search places:

```bash
curl "http://127.0.0.1:8000/api/places?q=chennai&limit=5"
```

Calculate a KP chart:

```bash
curl -X POST http://127.0.0.1:8000/api/kp-chart \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VJ",
    "birth_datetime": {
      "year": 1993,
      "month": 4,
      "day": 2,
      "hour": 1,
      "minute": 15,
      "second": 0
    },
    "location": {
      "name": "Pithoragarh",
      "latitude": 29.418,
      "longitude": 80.207,
      "timezone": 5.5
    },
    "settings": {
      "ayanamsa_mode": "KP",
      "house_cusp_method": 3,
      "use_true_nodes": false,
      "include_western_planets": false
    }
  }'
```

## Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Run the React app:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```
