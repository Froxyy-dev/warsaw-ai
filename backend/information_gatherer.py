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
        self.system_prompt = """
        Jesteś asystentem ds. umawiania spotkań.
        Zbierz: Imię i nazwisko, Datę, Godzinę oraz WSZYSTKIE INNE istotne szczegóły potrzebne do umówienia spotkania.
        Musisz pytać użytkownika o wszelkie brakujące informacje krok po kroku.
        NIE wolno Ci zakładać żadnych szczegółów.
        Rozmowa powinna wyglądać następująco
        PROTOKÓŁ:
        Gdy WSZYSTKIE szczegóły zostaną zebrane, zwróć TYLKO ten blok JSON:
        ```json
        {
            "full_name": "...",
            "date": "...",
            "time": "...",
            "reason": "...",
            ... inne szczegóły ...
        }
        ```
        """

        self.llm_client = LLMClient(model=model, system_instruction=self.system_prompt)

    def process_message(self, message: str):
        response = self.llm_client.send(message)
        text = response
        
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
        