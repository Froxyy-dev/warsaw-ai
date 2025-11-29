from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Generator, List
import os
import asyncio
load_dotenv()

class LLMClient:
    def __init__(self, model: str = "gemini-2.5-flash", system_instruction: str = None):
        """
        Initialize the Gemini Client with a chat session.
        
        Args:
            model: The model to use. Default is gemini-2.5-flash.
            system_instruction: Optional system instruction for the model.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.system_instruction = system_instruction

        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Create config with or without system instruction
        if self.system_instruction:
            self.config = types.GenerateContentConfig(
                tools=[grounding_tool],
                system_instruction=self.system_instruction
            )
        else:
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
    
    def send(self, message: str) -> str:
        """
        Sends a message and returns the complete response as a single string.
        
        Args:
            message: The message/prompt to send
            
        Returns:
            Complete response string
        """
        response_chunks = []
        
        for chunk in self.send_message(message):
            response_chunks.append(chunk)
        
        return ''.join(response_chunks)
    
    async def send_async(self, message: str) -> str:
        """
        Async version of send() - runs in thread pool to avoid blocking event loop.
        
        Args:
            message: The message/prompt to send
            
        Returns:
            Complete response string
        """
        # Run the blocking send() in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send, message)

    def get_history(self):
        """
        Retrieves the conversation history.
        """
        return self.chat_session.get_history()

    def clear_chat(self):
        """
        Resets the conversation history by creating a new chat session.
        """
        self.chat_session = self.client.chats.create(model=self.model, config=self.config)

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