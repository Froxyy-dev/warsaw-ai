
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI, ChatCompletion 
import dotenv 
dotenv.load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# client = OpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# res = client.chat.completions.create(
#     model="gemini-2.5-flash",
#     tools=[{"type": "websearch"}],
#     messages=[
#         {"role": "user", "content": "What time is it?"}
#     ]
# )

from google import genai
from google.genai import types

client = genai.Client()

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

res = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What time is it in Warsaw?",
    config=config,
)

print(res.text)