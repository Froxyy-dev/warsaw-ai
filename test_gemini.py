#!/usr/bin/env python3
"""Test Gemini API connection and quota"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("🔑 Testing Gemini API")
    print("=" * 50)
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print()
    
    # Test different models
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-2.0-flash-exp"
    ]
    
    for model in models:
        print(f"Testing model: {model}")
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents="Say hello in one word"
            )
            print(f"✅ {model} works!")
            print(f"   Response: {response.text}")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ {model} - Quota exceeded (limit reached)")
            elif "404" in error_msg:
                print(f"⚠️  {model} - Model not found")
            else:
                print(f"❌ {model} - Error: {error_msg[:100]}")
        print()
    
    print("=" * 50)
    print("Recommendation:")
    print("If all models show quota exceeded, you need to:")
    print("1. Wait for quota to reset (usually per minute/hour)")
    print("2. Get a new API key from https://aistudio.google.com/apikey")
    print("3. Or upgrade to paid tier")

if __name__ == "__main__":
    test_gemini()

