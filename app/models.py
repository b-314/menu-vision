from pydantic import BaseModel
from typing import List, Optional

class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

class FoodItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    nutrition: Optional[NutritionInfo] = None

class Category(BaseModel):
    category: str
    items: List[FoodItem]

class MenuTextRequest(BaseModel):
    text: str