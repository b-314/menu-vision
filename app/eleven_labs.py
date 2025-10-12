
# %%

import os, requests
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "MEJe6hPrI48Kt2lFuVe3"  

app = FastAPI()

NUTRIENT_EXPLANATIONS = {
    # macros
    "Calories": "Calories provide the energy your body needs to function, move, and stay alive.",
    "Protein": "Protein helps build and repair tissues, supports muscles, and keeps you feeling full longer.",
    "Carbohydrates": "Carbohydrates are your body’s main source of quick energy for the brain and muscles.",
    "Fiber": "Fiber supports digestion, helps control blood sugar, and keeps you feeling satisfied after eating.",
    "Sugars": "Sugars give quick energy, but too much can spike blood sugar and cause energy crashes.",
    "Added Sugars": "Added sugars are those put into foods during processing. Too much can impact heart and metabolic health.",
    "Fat": "Fat provides long-term energy and helps absorb vitamins A, D, E, and K.",
    "Saturated Fat": "Saturated fat is found in animal and some plant foods; too much may raise cholesterol.",
    "Unsaturated Fat": "Unsaturated fats are healthy fats that support heart and brain function.",
    "Monounsaturated Fat": "Monounsaturated fats support heart health and reduce bad cholesterol levels.",
    "Polyunsaturated Fat": "Polyunsaturated fats, including omega-3 and omega-6, help maintain healthy cells and brain function.",
    "Trans Fat": "Trans fats are artificial fats that raise bad cholesterol and lower good cholesterol — best to avoid.",
    "Cholesterol": "Cholesterol helps make hormones and cell membranes, but too much can raise heart disease risk.",
    "Omega-3 Fatty Acids": "Omega-3s support heart, brain, and joint health and help reduce inflammation.",
    "Omega-6 Fatty Acids": "Omega-6s are essential fats that support brain and muscle function, but balance with omega-3s is important.",
    "Water": "Water keeps you hydrated, regulates body temperature, and supports every body function.",

    # vitamins
    "Vitamin A": "Vitamin A supports vision, skin health, and the immune system.",
    "Vitamin B1": "Vitamin B1, or thiamine, helps convert food into energy and supports the nervous system.",
    "Vitamin B2": "Vitamin B2, or riboflavin, helps release energy from food and supports healthy skin and eyes.",
    "Vitamin B3": "Vitamin B3, or niacin, helps convert food to energy and supports skin and nerve health.",
    "Vitamin B5": "Vitamin B5, or pantothenic acid, helps your body make hormones and metabolize fats and carbs.",
    "Vitamin B6": "Vitamin B6 helps make neurotransmitters and supports brain development and immune health.",
    "Vitamin B7": "Vitamin B7, or biotin, helps your body use fats and proteins and supports healthy hair, skin, and nails.",
    "Vitamin B9": "Vitamin B9, or folate, supports cell growth and is especially important during pregnancy.",
    "Vitamin B12": "Vitamin B12 supports nerve function, makes red blood cells, and helps with DNA production.",
    "Vitamin C": "Vitamin C boosts immunity, supports collagen production, and helps your body absorb iron.",
    "Vitamin D": "Vitamin D strengthens bones, supports immune function, and helps your body absorb calcium.",
    "Vitamin E": "Vitamin E acts as an antioxidant that protects cells from damage and supports immune health.",
    "Vitamin K": "Vitamin K helps your blood clot properly and supports bone health.",

    # minerals
    "Calcium": "Calcium builds strong bones and teeth and supports muscle and nerve function.",
    "Iron": "Iron helps carry oxygen in your blood and prevents tiredness and weakness.",
    "Magnesium": "Magnesium supports muscle relaxation, nerve function, and energy production.",
    "Phosphorus": "Phosphorus helps build bones and teeth and supports energy metabolism.",
    "Potassium": "Potassium helps balance fluids, supports muscle function, and maintains healthy blood pressure.",
    "Sodium": "Sodium helps balance fluids, but too much can raise blood pressure.",
    "Zinc": "Zinc supports immune function, wound healing, and DNA production.",
    "Copper": "Copper helps form red blood cells and supports your nervous and immune systems.",
    "Manganese": "Manganese supports metabolism and helps protect cells from oxidative stress.",
    "Selenium": "Selenium supports your immune system and acts as an antioxidant.",
    "Iodine": "Iodine is needed for making thyroid hormones, which control metabolism.",
    "Chromium": "Chromium helps your body regulate blood sugar by improving insulin action.",
    "Molybdenum": "Molybdenum helps your body process proteins and detoxify certain compounds.",
    "Chloride": "Chloride helps maintain fluid balance and is a component of stomach acid.",
    "Fluoride": "Fluoride strengthens teeth and helps prevent cavities.",

    # amino acids 
    "Leucine": "Leucine is an essential amino acid that stimulates muscle repair and growth.",
    "Isoleucine": "Isoleucine helps regulate blood sugar and supports muscle metabolism.",
    "Valine": "Valine supports energy production and muscle recovery.",
    "Lysine": "Lysine helps your body make proteins and supports calcium absorption.",
    "Methionine": "Methionine supports detoxification and helps produce important molecules in your body.",
    "Phenylalanine": "Phenylalanine is used to make neurotransmitters like dopamine and norepinephrine.",
    "Threonine": "Threonine supports collagen and elastin production for healthy skin and joints.",
    "Tryptophan": "Tryptophan helps produce serotonin, which supports mood and sleep.",
    "Histidine": "Histidine helps protect nerve cells and is used to make histamine for immune response.",

    # miscellaneous nutrients
    "Caffeine": "Caffeine is a stimulant that boosts alertness but can cause jitters in high amounts.",
    "Alcohol": "Alcohol provides empty calories and can affect hydration and metabolism.",
    "Beta-Carotene": "Beta-carotene is converted into vitamin A and acts as an antioxidant.",
    "Choline": "Choline supports brain function, metabolism, and liver health.",
    "Retinol": "Retinol is an active form of vitamin A that supports vision and cell growth.",
    "Niacin": "Niacin, or vitamin B3, helps your body turn food into energy and supports skin and nerves.",
    "Pantothenic Acid": "Pantothenic acid helps make and break down fats for energy and supports hormone production.",
}


@app.get("/explain/{nutrient}")
def explain_nutrient(nutrient: str):
    nutrient = nutrient.strip().title()
    text = NUTRIENT_EXPLANATIONS.get(
        nutrient,
        f"{nutrient} is an important nutrient that supports your body's overall health."
    )

    # ElevenLabs TTS API call
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        return JSONResponse({"error": "TTS failed", "text": text}, status_code=500)

    return StreamingResponse(
        iter([resp.content]),
        media_type="audio/mpeg"
    )
# %%
