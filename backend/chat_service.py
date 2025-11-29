"""
Chat Service for handling chat conversations with LLM integration.
Manages context, processes messages, and generates AI responses.
"""
import logging
from datetime import datetime
from typing import List, Optional
import uuid

from llm_client import LLMClient
from models import Message, MessageRole, Conversation
from storage_manager import storage_manager

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat conversations with AI"""
    
    def __init__(self, max_context_messages: int = 20):
        """
        Initialize chat service.
        
        Args:
            max_context_messages: Maximum number of messages to include in context window
        """
        self.max_context_messages = max_context_messages
        self.system_prompt = """Jesteś pomocnym asystentem AI dla systemu umawiania wizyt i połączeń telefonicznych.
Możesz pomóc użytkownikom w:
- Umawianiu wizyt
- Sprawdzaniu statusu połączeń
- Zarządzaniu terminarzem
- Odpowiadaniu na pytania o system

Odpowiadaj w sposób profesjonalny, przyjazny i konkretny."""
    
    def _create_llm_client(self, conversation_history: List[Message]) -> LLMClient:
        """
        Create a new LLM client with conversation context.
        
        Args:
            conversation_history: List of previous messages for context
        """
        # Create new LLM client
        client = LLMClient()
        
        # Build context from conversation history
        # Take only the last N messages to stay within context window
        context_messages = conversation_history[-self.max_context_messages:]
        
        # If there's history, send it to establish context
        if context_messages:
            # Build context string
            context = "Poprzednia konwersacja:\n\n"
            for msg in context_messages:
                role = "Użytkownik" if msg.role == MessageRole.USER else "Asystent"
                context += f"{role}: {msg.content}\n\n"
            
            # Send system prompt with context
            try:
                client.send(f"{self.system_prompt}\n\n{context}")
            except Exception as e:
                logger.error(f"Failed to set context: {e}")
        else:
            # Just send system prompt for new conversations
            try:
                client.send(self.system_prompt)
            except Exception as e:
                logger.error(f"Failed to send system prompt: {e}")
        
        return client
    
    async def process_user_message(
        self, 
        conversation_id: str, 
        content: str
    ) -> tuple[Message, Message]:
        """
        Process a user message and generate AI response.
        
        Args:
            conversation_id: ID of the conversation
            content: User message content
            
        Returns:
            Tuple of (user_message, assistant_message)
        """
        try:
            # Load conversation to get history
            conversation = storage_manager.load_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            # Create user message
            user_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=content,
                timestamp=datetime.now(),
                metadata={}
            )
            
            # Generate AI response
            ai_content = await self.generate_ai_response(
                conversation.messages,
                content
            )
            
            # Create assistant message
            assistant_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                timestamp=datetime.now(),
                metadata={
                    "model": "gemini-2.5-flash"
                }
            )
            
            logger.info(f"Processed message for conversation {conversation_id}")
            return user_message, assistant_message
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise
    
    async def generate_ai_response(
        self, 
        conversation_history: List[Message],
        user_message: str
    ) -> str:
        """
        Generate AI response based on conversation history and new message.
        
        Args:
            conversation_history: Previous messages in the conversation
            user_message: New user message
            
        Returns:
            AI generated response
        """
        try:
            # Create LLM client with context
            client = self._create_llm_client(conversation_history)
            
            # Generate response
            start_time = datetime.now()
            response = client.send(user_message)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Generated AI response in {processing_time:.2f}s")
            
            # Clean up response
            response = response.strip()
            
            if not response:
                response = "Przepraszam, nie mogłem wygenerować odpowiedzi. Spróbuj ponownie."
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate AI response: {error_msg}")
            
            # Check for specific errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return "Przepraszam, API osiągnęło limit zapytań. Spróbuj ponownie za chwilę lub sprawdź ustawienia API key."
            elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                return "Błąd autoryzacji API. Sprawdź czy GEMINI_API_KEY jest poprawnie ustawiony."
            elif "INVALID_ARGUMENT" in error_msg:
                return "Nieprawidłowe zapytanie do API. Sprawdź konfigurację."
            else:
                return f"Przepraszam, wystąpił błąd: {error_msg[:100]}"
    
    def create_conversation(self, initial_message: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            initial_message: Optional initial user message
            
        Returns:
            New conversation object
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        messages = []
        if initial_message:
            messages.append(Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=initial_message,
                timestamp=now,
                metadata={}
            ))
        
        conversation = Conversation(
            id=conversation_id,
            title=initial_message[:50] + "..." if initial_message and len(initial_message) > 50 else initial_message,
            messages=messages,
            created_at=now,
            updated_at=now
        )
        
        # Save to disk
        storage_manager.save_conversation(conversation)
        
        logger.info(f"Created new conversation {conversation_id}")
        return conversation


# Global instance
chat_service = ChatService()

