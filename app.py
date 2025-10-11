from fastapi import FastAPI
from pydantic import BaseModel
from parser import parse_menu
from utils import summarize_categories

app = FastAPI()

class MenuRequest(BaseModel):
    menu_text: str

@app.post("/parse_menu/")
async def parse_menu_endpoint(request: MenuRequest):
    categories = parse_menu(request.menu_text)
    summary = summarize_categories(categories)
    return {"categories": summary, "raw_data": categories}

@app.get("/")
async def root():
    return {"message": "Menu Parser API is running!"}