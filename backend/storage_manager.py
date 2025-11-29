"""
Storage Manager for handling JSON-based conversation persistence.
Thread-safe operations for reading/writing conversation data.
"""
import json
import os
import threading
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging

from models import Conversation, Message, ConversationMetadata, ConversationStatus, MessageRole

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages JSON file storage for conversations"""
    
    def __init__(self, base_path: str = "database/conversations"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._locks = {}  # conversation_id -> Lock
        self._global_lock = threading.Lock()
        
    def _get_lock(self, conversation_id: str) -> threading.Lock:
        """Get or create a lock for a specific conversation"""
        with self._global_lock:
            if conversation_id not in self._locks:
                self._locks[conversation_id] = threading.Lock()
            return self._locks[conversation_id]
    
    def _get_file_path(self, conversation_id: str) -> Path:
        """Get the file path for a conversation"""
        return self.base_path / f"conversation_{conversation_id}.json"
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """
        Save a conversation to disk.
        Returns True on success, False on failure.
        """
        lock = self._get_lock(conversation.id)
        file_path = self._get_file_path(conversation.id)
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with lock:
                # Convert to dict for JSON serialization
                data = conversation.model_dump(mode='json')
                
                # Write to temp file first (atomic operation)
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                # Rename temp file to actual file (atomic on POSIX systems)
                temp_path.replace(file_path)
                
                logger.info(f"Saved conversation {conversation.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save conversation {conversation.id}: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Load a conversation from disk.
        Returns None if not found or error occurs.
        """
        lock = self._get_lock(conversation_id)
        file_path = self._get_file_path(conversation_id)
        
        try:
            with lock:
                if not file_path.exists():
                    logger.warning(f"Conversation {conversation_id} not found")
                    return None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                conversation = Conversation(**data)
                logger.info(f"Loaded conversation {conversation_id}")
                return conversation
                
        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return None
    
    def list_conversations(self) -> List[ConversationMetadata]:
        """
        List all conversations with metadata (without full message history).
        Returns list sorted by updated_at (newest first).
        """
        conversations = []
        
        try:
            # Find all conversation files
            for file_path in self.base_path.glob("conversation_*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract metadata without loading all messages
                    messages = data.get('messages', [])
                    last_message = messages[-1] if messages else None
                    
                    metadata = ConversationMetadata(
                        id=data['id'],
                        title=data.get('title'),
                        created_at=data['created_at'],
                        updated_at=data['updated_at'],
                        status=data.get('status', 'active'),
                        message_count=len(messages),
                        last_message_preview=last_message['content'][:100] if last_message else None
                    )
                    conversations.append(metadata)
                    
                except Exception as e:
                    logger.error(f"Failed to load metadata from {file_path}: {e}")
                    continue
            
            # Sort by updated_at (newest first)
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            logger.info(f"Listed {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from disk.
        Returns True on success, False on failure.
        """
        lock = self._get_lock(conversation_id)
        file_path = self._get_file_path(conversation_id)
        
        try:
            with lock:
                if not file_path.exists():
                    logger.warning(f"Conversation {conversation_id} not found for deletion")
                    return False
                
                file_path.unlink()
                logger.info(f"Deleted conversation {conversation_id}")
                
                # Clean up lock
                with self._global_lock:
                    if conversation_id in self._locks:
                        del self._locks[conversation_id]
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
    
    def add_message_to_conversation(self, conversation_id: str, message: Message) -> bool:
        """
        Add a message to an existing conversation.
        Returns True on success, False on failure.
        """
        try:
            # Load conversation
            conversation = self.load_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return False
            
            # Add message
            conversation.messages.append(message)
            conversation.updated_at = datetime.now()
            
            # Update title if it's the first user message and no title set
            if not conversation.title and message.role == MessageRole.USER and len(conversation.messages) <= 2:
                # Use first user message as title (truncated)
                conversation.title = message.content[:50] + ("..." if len(message.content) > 50 else "")
            
            # Save conversation
            success = self.save_conversation(conversation)
            if success:
                logger.info(f"Added message {message.id} to conversation {conversation_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            return False
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        file_path = self._get_file_path(conversation_id)
        return file_path.exists()
    
    # ===== Party Plan Storage Methods =====
    
    def _get_plan_file_path(self, plan_id: str) -> Path:
        """Get the file path for a party plan"""
        plans_path = self.base_path.parent / "plans"
        plans_path.mkdir(parents=True, exist_ok=True)
        return plans_path / f"plan_{plan_id}.json"
    
    def save_plan(self, plan) -> bool:
        """
        Save a party plan to disk
        
        Args:
            plan: PartyPlan object
            
        Returns:
            True on success, False on failure
        """
        lock = self._get_lock(f"plan_{plan.id}")
        file_path = self._get_plan_file_path(plan.id)
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with lock:
                # Convert to dict for JSON serialization
                data = plan.model_dump(mode='json')
                
                # Write to temp file first
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                # Rename temp file to actual file (atomic)
                temp_path.replace(file_path)
                
                logger.info(f"Saved plan {plan.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save plan {plan.id}: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def load_plan(self, plan_id: str):
        """
        Load a party plan from disk
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            PartyPlan object or None if not found
        """
        from models import PartyPlan  # Import here to avoid circular import
        
        lock = self._get_lock(f"plan_{plan_id}")
        file_path = self._get_plan_file_path(plan_id)
        
        try:
            with lock:
                if not file_path.exists():
                    logger.warning(f"Plan {plan_id} not found")
                    return None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                plan = PartyPlan(**data)
                logger.info(f"Loaded plan {plan_id}")
                return plan
                
        except Exception as e:
            logger.error(f"Failed to load plan {plan_id}: {e}")
            return None
    
    def get_plan_by_conversation(self, conversation_id: str):
        """
        Get party plan associated with a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            PartyPlan object or None if not found
        """
        from models import PartyPlan  # Import here to avoid circular import
        
        try:
            plans_path = self.base_path.parent / "plans"
            if not plans_path.exists():
                return None
            
            # Find plan file with matching conversation_id
            for file_path in plans_path.glob("plan_*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get('conversation_id') == conversation_id:
                        plan = PartyPlan(**data)
                        logger.info(f"Found plan for conversation {conversation_id}")
                        return plan
                        
                except Exception as e:
                    logger.error(f"Failed to read plan from {file_path}: {e}")
                    continue
            
            logger.info(f"No plan found for conversation {conversation_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get plan by conversation {conversation_id}: {e}")
            return None
    
    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a party plan from disk
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            True on success, False on failure
        """
        lock = self._get_lock(f"plan_{plan_id}")
        file_path = self._get_plan_file_path(plan_id)
        
        try:
            with lock:
                if not file_path.exists():
                    logger.warning(f"Plan {plan_id} not found for deletion")
                    return False
                
                file_path.unlink()
                logger.info(f"Deleted plan {plan_id}")
                
                # Clean up lock
                with self._global_lock:
                    lock_key = f"plan_{plan_id}"
                    if lock_key in self._locks:
                        del self._locks[lock_key]
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete plan {plan_id}: {e}")
            return False


# Global instance
storage_manager = StorageManager()

