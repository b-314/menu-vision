# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.parser import TextMenuParser

class MenuTextRequest(BaseModel):
    text: str

app = FastAPI(title="Menu Text Parsing API")

@app.post("/parse_menu_text/")
async def parse_menu_text(request: MenuTextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")
    
    parser = TextMenuParser(request.text)
    parsed_lines = parser.parse_lines()
    return {"parsed": parsed_lines}