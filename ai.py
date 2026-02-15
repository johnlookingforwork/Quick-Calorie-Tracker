import json

import streamlit as st
from openai import OpenAI


def _get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def estimate_macros(description: str) -> dict:
    """Call GPT-4o-mini to estimate macros from a food description.

    Returns dict with keys: name, calories, protein, carbs, fat.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a nutrition expert. The user will describe a food or meal. "
                    "Estimate the macronutrients and return a JSON object with these exact keys: "
                    '"name" (string, a clean short name for the food), '
                    '"calories" (number, kcal), '
                    '"protein" (number, grams), '
                    '"carbs" (number, grams), '
                    '"fat" (number, grams). '
                    "Be reasonable and accurate. If the description is vague, assume a typical serving size."
                ),
            },
            {"role": "user", "content": description},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    result = json.loads(response.choices[0].message.content)
    return {
        "name": str(result.get("name", description)),
        "calories": float(result.get("calories", 0)),
        "protein": float(result.get("protein", 0)),
        "carbs": float(result.get("carbs", 0)),
        "fat": float(result.get("fat", 0)),
    }
