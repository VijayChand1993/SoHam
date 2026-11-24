import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    RulingPlanetPlacementRequest,
    TodayPredictionRequest,
    TodayPredictionResponse,
)


DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
TODAY_PREDICTION_DISCLAIMER = (
    "Do not claim certainty. Present this as interpretive guidance, not a "
    "guaranteed outcome."
)

load_dotenv()


def format_rp_context(placement: RulingPlanetPlacementRequest) -> str:
    return f"{placement.planet}, {placement.house} house, {placement.rashi}"


def format_optional_rp_context(placement: RulingPlanetPlacementRequest | None) -> str:
    if placement is None:
        return "Not provided"
    return format_rp_context(placement)


def build_today_prediction_prompt(request: TodayPredictionRequest) -> str:
    moon_placement = request.moon_placement

    return f"""Act as an expert KP (Krishnamurti Paddhati) Astrologer. I will give you the details of the Moon from my instant Prashna (Horary) chart for a daily prediction.

Your task is to analyze these placements step-by-step using strict KP rules:
1. The Planet (Moon) indicates the inquirer's current state of mind and immediate focus.
2. The Star Lord (STL) indicates the source, nature, and the actual houses that want to manifest (the seed of the event).
3. The Rashi Lord (RL) indicates the execution environment and how the energy will feel (smooth, stressful, delayed, etc.).

Please analyze the following details for today's prediction:
- Moon House Placement: {moon_placement.house} house, {moon_placement.rashi}
- Moon Star Lord (STL) & its House: {format_rp_context(request.moon_star_lord)}
- Moon Rashi Lord (RL) & its House: {format_rp_context(request.moon_rashi_lord)}
- Core Question/Focus of the Day: General daily vibe

Additional RP context accepted by the API for future expansion:
- Asc Rashi Lord: {format_rp_context(request.asc_rashi_lord)}
- Day Lord: {format_rp_context(request.day_lord)}
- Transit Node Ke in Base RP Sign: {format_optional_rp_context(request.transit_node_ke_in_base_rp_sign)}
- Transit Node Ra in Base RP Sign: {format_optional_rp_context(request.transit_node_ra_in_base_rp_sign)}

Provide the interpretation in 3 clear sections:
1. **The Mindset & Focus:** What am I thinking about or prioritizing today based on the Moon's house?
2. **The Manifestation (The STL Effect):** What specific house energies are being activated today? (Remember the KP rule: A planet gives the results of its Star Lord's residential house first).
3. **The Experience & Outcome (The RL Effect):** Will the day feel smooth, delayed, or stressful? What should I watch out for?

{TODAY_PREDICTION_DISCLAIMER}

Keep the explanation direct, mathematical, and actionable without conversational fluff."""


def calculate_today_prediction_response(
    request: TodayPredictionRequest,
) -> TodayPredictionResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        input=build_today_prediction_prompt(request),
        temperature=0.4,
    )

    prediction = response.output_text.strip()
    if not prediction:
        raise RuntimeError("OpenAI returned an empty prediction")

    return TodayPredictionResponse(prediction=prediction)
