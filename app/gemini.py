import os
import asyncio
import google.generativeai as genai


class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    async def call(self, prompt: str) -> str:
        """
        Async-safe Gemini call: runs blocking generate_content in a thread executor.
        """
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
        return response.text
