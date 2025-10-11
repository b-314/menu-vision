from pydantic import BaseModel
from typing import List, Optional

class Food(BaseModel):
    name: str
    price: Optional[float] = None
    description: Optional[str] = None

class Category(BaseModel):
    name: str
    items: List[Food] = []

    def add_food(self, food: Food):
        self.items.append(food)