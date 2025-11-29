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
    try:
        # Check if conversation exists
        if not storage_manager.conversation_exists(conversation_id):
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Process message and generate AI response
        user_message, assistant_message = await chat_service.process_user_message(
            conversation_id,
            message_request.content
        )
        
        # Save user message (synchronously)
        storage_manager.add_message_to_conversation(
            conversation_id,
            user_message
        )
        
        # Save assistant message (synchronously)
        storage_manager.add_message_to_conversation(
            conversation_id,
            assistant_message
        )
        
        logger.info(f"Sent message to conversation {conversation_id}")
        
        # Return assistant message
        return assistant_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message to conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

