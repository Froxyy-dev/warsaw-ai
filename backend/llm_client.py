"""
LLM Client - Pure interface for LLM interactions
This module will be provided/maintained separately
"""
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

# Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_llm(
    prompt: str, 
    system_message: str = "You are a helpful assistant.",
    model: str = "gpt-4o-mini",
    response_format: str = "json",
    temperature: float = 0.1
) -> Optional[Dict[str, Any]]:
    """
    Generic LLM call interface.
    
    Args:
        prompt: User prompt
        system_message: System message
        model: Model to use
        response_format: "json" or "text"
        temperature: 0.0-2.0
        
    Returns:
        Dict with response or None if error
    """
    
    if LLM_PROVIDER == "openai":
        return _call_openai(prompt, system_message, model, response_format, temperature)
    elif LLM_PROVIDER == "anthropic":
        return _call_anthropic(prompt, system_message, model, response_format, temperature)
    else:
        print(f"⚠️  Unknown LLM provider: {LLM_PROVIDER}")
        return None


def _call_openai(
    prompt: str,
    system_message: str,
    model: str,
    response_format: str,
    temperature: float
) -> Optional[Dict[str, Any]]:
    """
    OpenAI API implementation.
    """
    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not set")
        return None
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
        }
        
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = client.chat.completions.create(**kwargs)
        
        content = response.choices[0].message.content
        
        if response_format == "json":
            result = json.loads(content)
        else:
            result = {"text": content}
        
        result["_meta"] = {
            "model": model,
            "tokens": response.usage.total_tokens,
            "provider": "openai"
        }
        
        return result
        
    except ImportError:
        print("⚠️  OpenAI library not installed. Run: pip install openai")
        return None
    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        return None


def _call_anthropic(
    prompt: str,
    system_message: str,
    model: str,
    response_format: str,
    temperature: float
) -> Optional[Dict[str, Any]]:
    """
    Anthropic Claude API implementation.
    """
    # TODO: Implementation
    print("⚠️  Anthropic not implemented yet")
    return None


# Convenience function for backwards compatibility
def analyze_transcript_with_llm(prompt: str, model: str = "gpt-4o-mini") -> Optional[Dict[str, Any]]:
    """
    Convenience wrapper for transcript analysis.
    """
    system_msg = "Jesteś ekspertem od analizy rozmów telefonicznych. Zawsze odpowiadasz w formacie JSON zgodnym z instrukcjami."
    return call_llm(prompt, system_msg, model, response_format="json")


# Test
if __name__ == "__main__":
    test_prompt = "Analyze this: User says hello. Return JSON with sentiment."
    result = call_llm(test_prompt)
    
    if result:
        print("✅ LLM Client working!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ LLM Client not configured")

