from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from app.gemini import GeminiClient
from app.models import Category, FoodItem
from app.nutrition import get_nutrition # This file must also be async
from app.meal_value import meal_value_score



DIETARY_CATEGORIES = ["Vegan", "Vegetarian", "Egg-free", "Dairy-free", "Gluten-free", "Nut-free"]

class GeminiMenuParser:
    def __init__(self, gemini_client: GeminiClient, menu_text: str):
        self.gemini = gemini_client
        self.menu_text = menu_text.strip()

    async def parse(self) -> List[Category]:
        """Main parse method that ensures valid Category objects are returned."""
        # This first Gemini call gets the menu structure
        parsed_data = await self._parse_menu(self.menu_text)

        # This second part runs all nutrition/dietary lookups concurrently
        await self._attach_all_extra_info(parsed_data)

        # This part just converts the final dictionary data into your Pydantic models
        categories: List[Category] = []
        for cat in parsed_data:
            items: List[FoodItem] = []
            for item in cat.get("items", []):
                nutrition = item.get("nutrition", {}) 
                kcal = nutrition.get("calories") if nutrition else None
                protein = nutrition.get("protein_g")
                fat = nutrition.get("fat_g")
                sugar = nutrition.get("sugar_g")
                fiber = nutrition.get("fiber_g")

                try:
                    meal_value = meal_value_score(
                        price=item.get("price"),
                        kcal=kcal,
                        protein_g=protein,
                        fat_g=fat,
                        sugar_g=sugar,
                        fiber_g=fiber,
                        satiety_score=5.0  # can later be dynamic
                    )
                except Exception as e:
                    print(f"[Meal Value Error] {item.get('name')}: {e}")
                    meal_value = None  #assign to the correct variable
                item["meal_value_score"] = [meal_value] if meal_value is not None else []

                # create FoodItem after computing the score
                items.append(FoodItem(**item))
            categories.append(Category(category=cat.get("category", "Uncategorized"), items=items))
        return categories

    async def _parse_menu(self, menu_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
You are a menu parser that converts messy OCR text into structured JSON.
Your job is to identify logical food/drink items and their categories.
Infer reasonable categories if missing (e.g., 'Appetizers', 'Entrees').
For each item, include "name", "description" (if any), and "price" (as a float).
Do NOT hallucinate nonexistent items.

Return JSON ONLY, formatted as a list of objects like this:
[
  {{
    "category": "Appetizers",
    "items": [
      {{"name": "Caesar Salad", "description": "Romaine, parmesan, croutons", "price": 8.50}}
    ]
  }}
]

Menu text:
{menu_text}

Return only valid JSON. No commentary or markdown.
        """
        try:
            response_text = await self.gemini.call(prompt)
            text = response_text.strip()

            if text.startswith("```"):
                text = text.split("```")[1].strip()
                if text.startswith("json"):
                    text = text[len("json"):].strip()
            
            parsed = json.loads(text)
        except Exception as e:
            print(f"[Gemini Parsing Error] {e}")
            parsed = None
        
        if not isinstance(parsed, list):
            # The heuristic fallback no longer needs to be async
            parsed = self._heuristic_parse(menu_text)

        return parsed

    async def _attach_all_extra_info(self, parsed_data: List[Dict]):
        tasks = []
        async with aiohttp.ClientSession() as session:
            # 1. Create a list of all the tasks we need to run
            for cat in parsed_data:
                for item in cat.get("items", []):
                    if name := item.get("name"):
                        tasks.append(get_nutrition(session, name))
                        tasks.append(self._get_dietary_restrictions_gemini(name, item.get("description")))

            # 2. Run all tasks at the same time and wait for them all to finish
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Map the results back to the correct items
        task_index = 0
        for cat in parsed_data:
            for item in cat.get("items", []):
                if item.get("name"):
                    # The nutrition result is the first of the pair
                    nutrition_result = results[task_index]
                    item["nutrition"] = nutrition_result if not isinstance(nutrition_result, Exception) else None
                    task_index += 1
                    
                    # The dietary restriction result is the second of the pair
                    dietary_result = results[task_index]
                    item["dietary_restrictions"] = dietary_result if not isinstance(dietary_result, Exception) else []
                    task_index += 1

    def _heuristic_parse(self, menu_text: str) -> List[Dict[str, Any]]:
        """Fallback parser: extracts items and prices from raw text lines. Does NOT make network calls."""
        items = []
        price_pattern = re.compile(r"\$?(\d+\.\d{2})$")

        for line in menu_text.splitlines():
            line = line.strip()
            if not line: continue

            price_match = price_pattern.search(line)
            if price_match:
                price_val = float(price_match.group(1))
                name_desc = line[:price_match.start()].strip()
                items.append({"name": name_desc, "price": price_val})
        
        return [{"category": "Uncategorized", "items": items}]

    async def _get_dietary_restrictions_gemini(self, name: str, description: Optional[str]) -> List[str]:
        prompt = f"""
Determine which of these dietary restrictions apply: {", ".join(DIETARY_CATEGORIES)}.
Return a JSON list of strings. Do NOT include anything else.

Example: ["Vegetarian", "Gluten-free"]

Item name: "{name}"
Description: "{description or 'N/A'}"
        """
        try:
            response_text = await self.gemini.call(prompt)
            text = response_text.strip()

            if text.startswith("```"):
                text = text.split("```")[1].strip()
                if text.startswith("json"):
                    text = text[len("json"):].strip()
            
            restrictions = json.loads(text)
        except Exception as e:
            print(f"[Dietary Classification Error] {e}")
            restrictions = []
        
        return [r for r in restrictions if r in DIETARY_CATEGORIES]