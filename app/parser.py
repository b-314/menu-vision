# app/parser.py
import re
from typing import List, Dict

class TextMenuParser:
    def __init__(self, text: str):
        self.text = text

    def parse_lines(self) -> List[Dict[str, str]]:
        """
        Parse each line and label it as:
        - category
        - food
        - description
        - price
        Returns a list of dictionaries for testing.
        """
        lines = self.text.splitlines()
        parsed = []
        current_category = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Heuristic: all uppercase = category
            if line.isupper():
                current_category = line
                parsed.append({"type": "category", "text": line})
                continue

            # Try to detect price
            price_match = re.search(r"\$?(\d+(?:\.\d{2})?)", line)
            price = price_match.group(1) if price_match else None

            # Split name and description
            name_desc = re.sub(r"\$?\d+(?:\.\d{2})?", "", line).strip()
            if " - " in name_desc:
                name, description = name_desc.split(" - ", 1)
            else:
                name, description = name_desc, ""

            parsed.append({
                "type": "food",
                "category": current_category or "Uncategorized",
                "name": name.strip(),
                "description": description.strip(),
                "price": price
            })

        return parsed