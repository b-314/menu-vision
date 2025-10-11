from pydantic import BaseModel
from typing import Optional, List

# ---------- Food Model ----------
class Food(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    dietary_group: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

    # --- Getters ---
    def get_name(self): return self.name
    def get_description(self): return self.description
    def get_price(self): return self.price
    def get_dietary_group(self): return self.dietary_group
    def get_nutrition_info(self): 
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat
        }

    # --- Setters ---
    def set_description(self, desc: str): self.description = desc
    def set_price(self, price: float): self.price = price
    def set_dietary_group(self, group: str): self.dietary_group = group
    def set_nutrition_info(self, calories=None, protein=None, carbs=None, fat=None):
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat

    # --- Placeholder: determine dietary group (you’ll integrate real logic later) ---
    def determine_dietary_group(self):
        if "chicken" in self.name.lower() or "beef" in self.name.lower():
            self.dietary_group = "Protein"
        elif "salad" in self.name.lower():
            self.dietary_group = "Vegetable"
        else:
            self.dietary_group = "Other"
        return self.dietary_group

    # --- Placeholder for external nutrition API call ---
    def fetch_nutrition_info(self):
        # TODO: connect to real API later
        self.calories = 200
        self.protein = 10
        self.carbs = 20
        self.fat = 5
        return self.get_nutrition_info()


# ---------- Category Model ----------
class Category(BaseModel):
    name: str
    foods: List[Food] = []

    def add_food(self, food: Food):
        self.foods.append(food)