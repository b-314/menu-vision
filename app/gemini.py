import os
from google import genai

class GeminiClient:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def call(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the raw text response.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text