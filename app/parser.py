
from dotenv import load_dotenv
load_dotenv()

import os
import json
from typing import List
from google import genai

from app.models import Category, FoodItem

# ---------- Gemini Config ----------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Create a client with the API key
client = genai.Client(api_key=GEMINI_API_KEY)


# ---------- Gemini Helper ----------

def call_gemini(prompt: str) -> str:
    """
    Calls Gemini using the google-genai client and returns raw text.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


# ---------- Menu Parser Class ----------

import re

class GeminiMenuParser:
    """
    Converts raw OCR text into structured categories and food items using Gemini.
    If Gemini output fails or is empty, falls back to a simple heuristic parser.
    """

    def __init__(self, raw_text: str):
        self.raw_text = raw_text.strip()

    def make_prompt(self) -> str:
        return f"""
You are a precise menu parser. The input below is text extracted from a restaurant menu using OCR.
Output ONLY a JSON array of categories. Each category must have:
- "category" (string)
- "items" (array of objects)
Each item must have:
- "name" (string, or "Unnamed Item" if missing)
- "description" (string or null)
- "price" (string or null)

Ignore unrelated text. Do not write explanations. Return valid JSON **only**.

### Input Menu Text:
\"\"\"
{self.raw_text}
\"\"\"
"""

    def parse(self) -> List[Category]:
        prompt = self.make_prompt()
        try:
            response_text = call_gemini(prompt)

            # Extract JSON array from response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]")
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON found in Gemini output")

            json_str = response_text[json_start:json_end + 1]
            parsed = json.loads(json_str)

            # Process categories and items
            final_categories: List[Category] = []
            for cat in parsed:
                cat_name = cat.get("category") or "Uncategorized"
                items_list = []
                for item in cat.get("items", []):
                    item_name = item.get("name") or "Unnamed Item"
                    item_desc = item.get("description")
                    item_price_raw = item.get("price")
                    item_price = None
                    if item_price_raw:
                        # Extract number from strings like "$5.99" or "USD 8"
                        match = re.search(r"\d+(?:\.\d{1,2})?", str(item_price_raw))
                        if match:
                            item_price = float(match.group())

                    items_list.append(FoodItem(
                        name=item_name,
                        description=item_desc,
                        price=item_price
                    ))
                if items_list:
                    final_categories.append(Category(category=cat_name, items=items_list))
            if not final_categories:
                raise ValueError("Gemini returned no items")
            return final_categories

        except (ValueError, json.JSONDecodeError, RuntimeError):
            # Fallback heuristic parser
            return self._heuristic_parse()

    def _heuristic_parse(self) -> List[Category]:
        """
        Simple fallback parser that extracts items and prices from raw text lines.
        """
        categories: List[Category] = [Category(category="Uncategorized", items=[])]
        price_pattern = re.compile(r"\$?\d+(?:\.\d{1,2})?")  # match prices like 5.95 or $5.95

        lines = self.raw_text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            price_match = price_pattern.search(line)
            if price_match:
                price = price_match.group()
                # Name is text before price, description is text after
                name_desc = line[:price_match.start()].strip()
                # Split name and description heuristically
                if "-" in name_desc:
                    name, description = map(str.strip, name_desc.split("-", 1))
                else:
                    name, description = name_desc, None
                try:
                    price_val = float(price.replace("$", ""))
                except ValueError:
                    price_val = None

                categories[0].items.append(
                    FoodItem(name=name or "Unnamed Item", description=description, price=price_val)
                )
        return categories