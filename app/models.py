from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

class FoodItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    nutrition: Optional[Dict[str, Any]] = None
    dietary_restrictions: Optional[List[str]] = None

class Category(BaseModel):
    category: str
    items: List[FoodItem]