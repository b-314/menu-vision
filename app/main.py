from fastapi import FastAPI
from pydantic import BaseModel
from app.parser import GeminiMenuParser

app = FastAPI()

class MenuTextRequest(BaseModel):
    menu_text: str

@app.post("/process_menu_text/")
async def process_menu_text(request: MenuTextRequest):
    try:
        parser = GeminiMenuParser(request.menu_text)
        structured_menu = parser.parse()  # returns list of Category objects
        # For testing, return as dicts instead of models to make JSON readable
        return [cat.dict() for cat in structured_menu]
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}