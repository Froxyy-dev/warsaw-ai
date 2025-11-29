import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables once when the module is imported
load_dotenv()
import os
from typing import Generator, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Gemini Client with a chat session.
        
        Args:
            model: The model to use. 
                   (Note: 'gemini-2.5-flash' in your snippet may be a future/private 
                   version. I've defaulted to '2.0-flash-exp' for public compatibility,
                   but you can pass 'gemini-2.5-flash' if you have access).
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
        self.client = genai.Client(api_key=api_key)
        self.model = model

        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        self.config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        
        # Initialize the chat session immediately
        self.chat_session = self.client.chats.create(model=self.model, config=self.config)
    def send_message(self, message: str) -> Generator[str, None, None]:
        """
        Sends a message to the active chat session and streams the response.
        
        Yields:
            String chunks of the generated response.
        """
        try:
            response_stream = self.chat_session.send_message_stream(message)
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    def get_history(self):
        """
        Retrieves the conversation history.
        """
        return self.chat_session.get_history()

    def clear_chat(self):
        """
        Resets the conversation history by creating a new chat session.
        """
        self.chat_session = self.client.chats.create(model=self.model)

if __name__ == "__main__":
    llm_client = LLMClient(model="gemini-2.5-flash")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        response_generator = llm_client.send_message(user_input)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print()