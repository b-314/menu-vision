from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from typing import List, Optional, Dict, Any
from app.gemini import GeminiClient
from app.models import Category, FoodItem
from app.nutrition import get_nutrition

DIETARY_CATEGORIES = ["Vegan", "Vegetarian", "Egg-free", "Dairy-free", "Gluten-free", "Nut-free"]

class GeminiMenuParser:
    """
    Parses OCR menu text into structured categories and items using Gemini.
    Falls back to heuristic parsing if Gemini output fails.
    """

    def __init__(self, gemini_client: GeminiClient, menu_text: str):
        self.gemini = gemini_client
        self.menu_text = menu_text.strip()

    def parse(self) -> List[Category]:
        """Main parse method that ensures valid Category objects are returned."""
        parsed_data = self._parse_menu(self.menu_text)

        categories: List[Category] = []
        for cat in parsed_data:
            items: List[FoodItem] = []
            for item in cat.get("items", []):
                items.append(
                    FoodItem(
                        name=item.get("name", "Unnamed Item"),
                        description=item.get("description"),
                        price=item.get("price"),
                        nutrition=item.get("nutrition"),
                        dietary_restrictions=item.get("dietary_restrictions", []),
                    )
                )
            categories.append(Category(category=cat.get("category", "Uncategorized"), items=items))

        return categories

    def _parse_menu(self, menu_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
You are a menu parser that converts messy OCR text into structured JSON.

The input is raw menu text extracted from OCR. 
Each line may contain item names, prices, and sometimes short descriptions.

Your job:
1. Identify logical food/drink items and categories.
2. Infer reasonable categories if missing (e.g., 'Beverages', 'Appetizers', 'Entrees', 'Desserts').
3. Estimate missing prices as None (not 0).
4. For each item, include name, description (if any), and price (as a float, e.g., 9.99).
5. Do NOT hallucinate nonexistent items.

Return JSON ONLY, formatted as a list of objects like this:
[
  {{
    "category": "Appetizers",
    "items": [
      {{"name": "Caesar Salad", "description": "Romaine, parmesan, croutons", "price": 8.50}},
      {{"name": "Garlic Bread", "description": "Buttery baguette with herbs", "price": 4.25}}
    ]
  }},
  {{
    "category": "Beverages",
    "items": [
      {{"name": "Latte", "description": "Espresso with milk", "price": 3.95}}
    ]
  }}
]

Menu text:
{menu_text}

Return only valid JSON. No commentary or markdown.
        """

        try:
            response = self.gemini.call(prompt)
            text = response.strip()

            # Strip Markdown/JSON fences if present
            if text.startswith("```"):
                text = text.split("```")[1].strip()
                if text.startswith("json"):
                    text = text[len("json"):].strip()

            parsed = json.loads(text)

        except Exception as e:
            print(f"[Gemini Parsing Error] {e}")
            parsed = None

        # Ensure parsed is always a list
        if not isinstance(parsed, list):
            parsed = self._heuristic_parse(menu_text)

        # Attach nutrition and dietary restriction info
        for cat in parsed:
            for item in cat.get("items", []):
                name = item.get("name")
                if name:
                    item["nutrition"] = get_nutrition(name)
                    item["dietary_restrictions"] = self._get_dietary_restrictions_gemini(
                        name, item.get("description")
                    )

        return parsed

    def _heuristic_parse(self, menu_text: str) -> List[Dict[str, Any]]:
        """
        Fallback parser: extracts items and prices from raw text lines.
        """
        categories = [{"category": "Uncategorized", "items": []}]
        price_pattern = re.compile(r"\$?\d+(?:\.\d{1,2})?")  # matches prices like 5.95 or $5.95

        for line in menu_text.splitlines():
            line = line.strip()
            if not line:
                continue

            price_match = price_pattern.search(line)
            if price_match:
                price = price_match.group()
                name_desc = line[:price_match.start()].strip()

                if "-" in name_desc:
                    name, description = map(str.strip, name_desc.split("-", 1))
                else:
                    name, description = name_desc, None

                try:
                    price_val = float(price.replace("$", ""))
                except ValueError:
                    price_val = None

                categories[0]["items"].append(
                    {
                        "name": name or "Unnamed Item",
                        "description": description,
                        "price": price_val,
                        "nutrition": get_nutrition(name),
                        "dietary_restrictions": self._get_dietary_restrictions_gemini(name, description),
                    }
                )

        return categories

    def _get_dietary_restrictions_gemini(self, name: str, description: Optional[str]) -> List[str]:
        """
        Ask Gemini to classify dietary restrictions based on the dish name and description.
        """
        prompt = f"""
Determine which of the following dietary restrictions apply to this food item.
You must only choose from:
{", ".join(DIETARY_CATEGORIES)}.

Return a JSON list of strings. Do NOT include anything else.

Example: ["Vegetarian", "Gluten-free"]

Item name: "{name}"
Description: "{description or 'N/A'}"
        """

        try:
            response = self.gemini.call(prompt)
            text = response.strip()
            if text.startswith("```"):
                text = text.split("```")[1].strip()
                if text.startswith("json"):
                    text = text[len("json"):].strip()
            restrictions = json.loads(text)
        except Exception as e:
            print(f"[Dietary Classification Error] {e}")
            restrictions = []

        # Validate output — only allow valid categories
        valid_restrictions = [r for r in restrictions if r in DIETARY_CATEGORIES]
        return valid_restrictions