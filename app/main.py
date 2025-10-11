from fastapi import FastAPI, File, UploadFile
from app.parser import MenuParser
from app.models import Category
from PIL import Image
import io

app = FastAPI(
    title="Menu Parsing API",
    description="Upload a menu image and receive structured categories and foods",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Menu Parsing API is running!"}

@app.post("/upload_menu/", response_model=list[Category])
async def upload_menu(file: UploadFile = File(...)):
    """
    Upload a menu image (JPEG/PNG) and receive structured categories and food items.
    """
    try:
        # Read uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Parse menu
        parser = MenuParser(image)
        categories = parser.parse()

        return categories
    except Exception as e:
        return {"error": str(e)}