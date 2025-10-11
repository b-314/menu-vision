import re
from models import Food, Category

def parse_menu(menu_text: str):
    """
    Example menu format expected:
    Appetizers
    - Spring Rolls: Crispy rolls with veggies - $5.99
    - Soup: Tomato soup - $4.50

    Entrees
    - Grilled Chicken: Served with rice - $12.99
    - Pasta: Creamy Alfredo - $11.50

    Desserts
    - Cheesecake: New York style - $6.00
    """

    lines = [line.strip() for line in menu_text.split("\n") if line.strip()]
    categories = []
    current_category = None

    for line in lines:
        # Category line (e.g. "Appetizers", "Entrees", "Desserts")
        if not line.startswith("-") and not re.search(r"\$", line):
            current_category = Category(name=line, foods=[])
            categories.append(current_category)

        # Food line
        elif line.startswith("-") and current_category:
            # Example line: "- Spring Rolls: Crispy rolls with veggies - $5.99"
            match = re.match(r"-\s*(.*?):\s*(.*?)\s*-\s*\$(\d+\.?\d*)", line)
            if match:
                name, desc, price = match.groups()
                food = Food(name=name.strip(), description=desc.strip(), price=float(price))
                food.determine_dietary_group()
                current_category.add_food(food)

    return categories