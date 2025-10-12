from fastapi import FastAPI
from pydantic import BaseModel
from app.gemini import GeminiClient
from app.parser import GeminiMenuParser

app = FastAPI()

# Make sure to instantiate your Gemini client once
gemini_client = GeminiClient()

class MenuTextRequest(BaseModel):
    menu_text: str

@app.post("/process_menu_text/")
async def process_menu_text(request: MenuTextRequest):
    """
    Accepts raw OCR menu text, parses it with GeminiMenuParser, 
    and returns structured menu data with nutrition info.
    """
    try:
        parser = GeminiMenuParser(gemini_client, request.menu_text)
        structured_menu = parser.parse()  # returns list of dicts with categories and items
        return [cat.dict() for cat in structured_menu]
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}