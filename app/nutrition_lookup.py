import os
import requests
from typing import Dict, Any, Optional

# Load credentials from environment variables
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

if not NUTRITIONIX_APP_ID or not NUTRITIONIX_API_KEY:
    raise EnvironmentError(
        "Please set NUTRITIONIX_APP_ID and NUTRITIONIX_API_KEY as environment variables."
    )

BASE_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"


def get_nutrition_info(food_name: str) -> Optional[Dict[str, Any]]:
    """
    Queries the Nutritionix API to retrieve nutrition data for a given food item.

    Args:
        food_name (str): The name of the food item (e.g. "chicken sandwich").

    Returns:
        Dict[str, Any]: Parsed nutrition information or None if not found.
    """
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "query": food_name,
        "timezone": "US/Eastern"
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if not result.get("foods"):
            return None

        # Extract the first match
        food = result["foods"][0]

        return {
            "food_name": food.get("food_name"),
            "serving_qty": food.get("serving_qty"),
            "serving_unit": food.get("serving_unit"),
            "serving_weight_grams": food.get("serving_weight_grams"),
            "calories": food.get("nf_calories"),
            "total_fat": food.get("nf_total_fat"),
            "saturated_fat": food.get("nf_saturated_fat"),
            "cholesterol": food.get("nf_cholesterol"),
            "sodium": food.get("nf_sodium"),
            "total_carbohydrate": food.get("nf_total_carbohydrate"),
            "dietary_fiber": food.get("nf_dietary_fiber"),
            "sugars": food.get("nf_sugars"),
            "protein": food.get("nf_protein"),
        }

    except requests.exceptions.RequestException as e:
        print(f"[Nutrition Lookup Error] {e}")
        return None