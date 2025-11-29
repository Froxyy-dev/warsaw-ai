import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from llm_client import LLMClient

load_dotenv()

class InformationGatherer:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.system_prompt = """Jesteś asystentem zbierającym dane. Pytaj KRÓTKO - max 5 słów.

Zbierz: Imię i nazwisko, Datę, Godzinę oraz inne szczegóły.
Pytaj o każdą informację PO KOLEI.
NIE zakładaj szczegółów.

WAŻNE:
- Pytaj ULTRA KRÓTKO (max 5 słów)
- BEZ "Dziękuję", "Proszę", "Świetnie"
- TYLKO pytanie

Przykłady:
✓ "Imię i nazwisko?"
✓ "Data spotkania?"
✗ "Dziękuję! Teraz potrzebuję daty spotkania."

Gdy zebrano WSZYSTKO, zwróć JSON:
```json
{
    "full_name": "...",
    "date": "...",
    "time": "...",
    ...
}
```
"""

        self.llm_client = LLMClient(model=model, system_instruction=self.system_prompt)

    def process_message(self, message: str):
        """Sync version - for backwards compatibility"""
        response = self.llm_client.send(message)
        return self._parse_response(response)
    
    async def process_message_async(self, message: str):
        """Async version - non-blocking"""
        response = await self.llm_client.send_async(message)
        return self._parse_response(response)
    
    def _parse_response(self, text: str):
        """Parse LLM response to extract structured data"""
        # Check for JSON
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return {"type": "complete", "text": "Spotkanie umówione!", "data": data}
            except:
                pass
                
        # Return normal text response
        # We strip the JSON block if it exists but failed parsing, or just return text
        clean_text = re.sub(r"```json.*?```", "", text, flags=re.DOTALL).strip()
        return {"type": "chat", "text": clean_text if clean_text else text}

if __name__ == "__main__":
    scheduler = InformationGatherer()
    print("Jestem Twoim asystentem ds. umawiania spotkań. W czym mogę pomóc?")
    while True:
        user_input = input("Użytkownik: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Zamykanie harmonogramu spotkań.")
            break
        response = scheduler.process_message(user_input)
        print("Asystent:", response["text"])
        if response["type"] == "complete":
            print("Wyodrębnione dane:", response["data"])
            break
        