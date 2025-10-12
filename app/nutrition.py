import os
import json
import aiohttp
import asyncio
from typing import Any, Dict, Optional
from app.gemini import GeminiClient

# =============== CONFIG ===============
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")
NUTRITIONIX_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# =============== NUTRITIONIX LOGIC ===============

async def get_nutritionix_info(session, food_name: str) -> Optional[Dict[str, Any]]:
    if not NUTRITIONIX_APP_ID or not NUTRITIONIX_API_KEY:
        print("[Nutritionix] Missing credentials — skipping.")
        return None

    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    body = {"query": food_name}

    try:
        async with session.post(NUTRITIONIX_URL, headers=headers, json=body) as res:
            if res.status != 200:
                print(f"[Nutritionix] {food_name} → API returned {res.status}")
                return None

            data = await res.json()
            if not data.get("foods"):
                return None

            f = data["foods"][0]
            return {
                "food_name": f.get("food_name"),
                "serving_size": f"{f.get('serving_qty', '')} {f.get('serving_unit', '')}".strip(),
                "calories": f.get("nf_calories"),
                "protein_g": f.get("nf_protein"),
                "carbs_g": f.get("nf_total_carbohydrate"),
                "fat_g": f.get("nf_total_fat"),
                "fiber_g": f.get("nf_dietary_fiber"),
                "sugar_g": f.get("nf_sugars"),
            }
    except Exception as e:
        print(f"[Nutritionix Error] {food_name}: {e}")
        return None

# =============== GEMINI FALLBACK ===============

def make_gemini_prompt(food_name: str) -> str:
    return f"""
You are a nutrition expert estimating realistic calorie and macronutrient values.

Given the food name below, estimate its typical nutrition facts based on
standard portion sizes and common restaurant servings.

### Rules
- Use realistic ranges; avoid extremes.
- Assume one average serving (plate, bowl, sandwich, etc.).
- Output a valid JSON object in this format only:

{{
"food_name": "...",
"serving_size": "...",
"calories": float,
"protein_g": float,
"carbs_g": float,
"fat_g": float, 
"fiber_g": float,
"sugar_g": float
}}

Estimate for: "{food_name}"
Return **only the JSON object**.
"""

async def get_gemini_estimate(food_name: str) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini to generate estimated nutrition data if Nutritionix fails.
    """
    gemini_client = GeminiClient()
    prompt = make_gemini_prompt(food_name)
    try:
        response = await gemini_client.call(prompt)

        # Extract the JSON part from the Gemini response
        json_start = response.find("{")
        json_end = response.rfind("}")
        if json_start == -1 or json_end == -1:
            print(f"[Gemini Nutrition] No JSON found for {food_name}: {response}")
            return None

        json_str = response[json_start:json_end + 1]
        return json.loads(json_str)
    except Exception as e:
        print(f"[Gemini Nutrition Error] {food_name}: {e}")
        return None
        
async def get_nutrition(session, food_name: str) -> Optional[Dict[str, Any]]:
    """
    Main entry point — tries Nutritionix first, falls back to Gemini.
    """
    nutrition = await get_nutritionix_info(session, food_name)
    if nutrition:
        print(f"[Nutritionix] Found: {food_name}")
        return nutrition

    print(f"[Nutritionix] Not found, falling back to Gemini for: {food_name}")
    return await get_gemini_estimate(food_name)