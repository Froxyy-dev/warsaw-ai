"""
Chat Router - API endpoints for chat functionality
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging

from models import (
    Conversation, 
    Message, 
    MessageRequest, 
    ConversationMetadata,
    ConversationResponse,
    MessageResponse
)
from storage_manager import storage_manager
from chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "storage_ready": storage_manager.base_path.exists()
    }


@router.post("/conversations/", response_model=ConversationResponse)
async def create_conversation():
    """
    Create a new empty conversation.
    """
    try:
        # Create empty conversation
        conversation = chat_service.create_conversation(initial_message=None)
        
        return ConversationResponse(
            success=True,
            conversation=conversation,
            message="Conversation created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/", response_model=List[ConversationMetadata])
async def list_conversations():
    """
    Get list of all conversations with metadata (without full message history).
    """
    try:
        conversations = storage_manager.list_conversations()
        return conversations
        
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation with full message history.
    """
    try:
        conversation = storage_manager.load_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail=f"Conversation {conversation_id} not found"
            )
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def send_message(
    conversation_id: str,
    message_request: MessageRequest
):
    """
    Send a message to a conversation and get AI response.
    
    This endpoint:
    1. Saves the user message
    2. Generates AI response
    3. Saves the AI response
    4. Returns the AI response
    """
    logger.info(f"📥 Received message request for conversation {conversation_id}")
    logger.info(f"📝 Message content: {message_request.content[:50]}...")
    
    try:
        # Check if conversation exists
        logger.info(f"🔍 Checking if conversation {conversation_id} exists...")
        if not storage_manager.conversation_exists(conversation_id):
            logger.error(f"❌ Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        logger.info(f"✅ Conversation exists")
        
        # FIRST: Save user message IMMEDIATELY (before LLM processing)
        # This allows frontend to see the user message while waiting for response
        import uuid
        from datetime import datetime
        from models import MessageRole
        
        logger.info(f"💾 Creating user message...")
        user_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message_request.content,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"💾 Saving user message to storage...")
        success = storage_manager.add_message_to_conversation(
            conversation_id,
            user_message
        )
        if not success:
            logger.error(f"❌ Failed to save user message!")
            raise HTTPException(status_code=500, detail="Failed to save user message")
        logger.info(f"✅ User message saved to conversation {conversation_id}")
        
        # NOW: Process message and generate AI response (this takes time)
        logger.info(f"🤖 Starting AI processing for conversation {conversation_id}...")
        logger.info(f"   Message content: {message_request.content}")
        logger.info(f"   Calling chat_service.process_user_message()...")
        try:
            logger.info(f"   ⏳ Awaiting process_user_message()...")
            _, assistant_message = await chat_service.process_user_message(
                conversation_id,
                message_request.content
            )
            logger.info(f"✅ AI processing complete!")
            if assistant_message:
                logger.info(f"   Assistant message ID: {assistant_message.id}")
                logger.info(f"   Assistant message preview: {assistant_message.content[:50]}...")
            else:
                logger.info(f"   ⚠️ No assistant message (messages already saved directly)")
        except Exception as ai_error:
            logger.error(f"❌ AI processing failed: {ai_error}", exc_info=True)
            
            # ✅ DONT CRASH - save error message for user!
            error_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=f"❌ Przepraszam, wystąpił błąd podczas przetwarzania:\n\n`{str(ai_error)}`\n\nSpróbuj ponownie lub sformułuj zapytanie inaczej.",
                timestamp=datetime.utcnow(),
                metadata={
                    "error": True,
                    "should_continue_refresh": False  # ✅ Stop - wait for user
                }
            )
            storage_manager.add_message_to_conversation(conversation_id, error_message)
            logger.info(f"✅ Error message saved for user")
            
            # Return error message instead of crashing
            assistant_message = error_message
        
        # Save assistant message (if one was created)
        if assistant_message:
            logger.info(f"💾 Saving assistant message...")
            success = storage_manager.add_message_to_conversation(
                conversation_id,
                assistant_message
            )
            if not success:
                logger.error(f"❌ Failed to save assistant message!")
                raise HTTPException(status_code=500, detail="Failed to save assistant message")
            logger.info(f"✅ Assistant message saved to conversation {conversation_id}")
            
            # Return assistant message
            logger.info(f"📤 Returning assistant message")
            return assistant_message
        else:
            # Messages were already saved directly (e.g., during GATHERING->SEARCHING transition)
            # Return a dummy message for the API response (frontend won't see this, it polls for updates)
            logger.info(f"📤 No assistant message to return (messages saved directly)")
            return Message(
                id="processing",
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Processing...",
                timestamp=datetime.utcnow(),
                metadata={"should_continue_refresh": True}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in send_message: {e}", exc_info=True)
        
        # ✅ Last resort - save error and return it instead of 500
        try:
            error_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=f"❌ Wystąpił nieoczekiwany błąd:\n\n`{str(e)}`\n\nZapiszę to i naprawię. Spróbuj ponownie.",
                timestamp=datetime.utcnow(),
                metadata={"critical_error": True}
            )
            storage_manager.add_message_to_conversation(conversation_id, error_message)
            return error_message
        except:
            # If even saving fails, then raise 500
            raise HTTPException(status_code=500, detail=f"Critical error: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    """
    try:
        success = storage_manager.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(conversation_id: str, limit: int = 50, offset: int = 0):
    """
    Get messages from a conversation with pagination.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (default 50)
        offset: Number of messages to skip (default 0)
    """
    try:
        conversation = storage_manager.load_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Apply pagination
        messages = conversation.messages[offset:offset + limit]
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

