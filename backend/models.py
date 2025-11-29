from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CallStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class CallRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to call")
    purpose: str = Field(..., description="Purpose of the call")
    customer_name: Optional[str] = Field(None, description="Customer name")
    preferred_date: Optional[str] = Field(None, description="Preferred appointment date")
    notes: Optional[str] = Field(None, description="Additional notes")

class Call(BaseModel):
    id: str
    phone_number: str
    purpose: str
    customer_name: Optional[str]
    status: CallStatus
    transcript: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class Appointment(BaseModel):
    id: str
    call_id: Optional[str]
    customer_name: str
    phone_number: str
    scheduled_date: str
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime

class CallResponse(BaseModel):
    success: bool
    call: Call
    message: str

class AppointmentResponse(BaseModel):
    success: bool
    appointment: Appointment
    message: str

# Chat models
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Conversation(BaseModel):
    id: str
    title: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime
    status: ConversationStatus = ConversationStatus.ACTIVE

class MessageRequest(BaseModel):
    content: str = Field(..., description="Message content")

class ConversationMetadata(BaseModel):
    """Lightweight conversation info without full message history"""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: ConversationStatus
    message_count: int
    last_message_preview: Optional[str] = None

class ConversationResponse(BaseModel):
    success: bool
    conversation: Conversation
    message: str

class MessageResponse(BaseModel):
    success: bool
    message: Message
    assistant_message: str

# Party Planner models
class PlanStateEnum(str, Enum):
    INITIAL = "initial"
    PLANNING = "planning"
    REFINEMENT = "refinement"
    CONFIRMED = "confirmed"
    GATHERING = "gathering"
    SEARCHING = "searching"  # NEW: Web search for venues
    TASK_GENERATION = "task_generation"  # NEW: Creating voice agent tasks
    EXECUTING = "executing"
    COMPLETE = "complete"

# Alias for backward compatibility
PlanState = PlanStateEnum

class PlanItem(BaseModel):
    id: str
    type: str  # "reservation", "order", "call", "task"
    description: str
    venue: Optional[str] = None
    contact_needed: bool = True
    status: str = "pending"  # "pending", "in_progress", "done"
    required_info: List[str] = []  # ["phone", "name", "date"]

class PartyPlan(BaseModel):
    id: str
    conversation_id: str
    user_request: str
    current_plan: Optional[str] = None  # Full plan text
    plan_items: List[PlanItem] = []
    state: PlanState
    gathered_info: dict = {}
    feedback_history: List[str] = []
    created_at: datetime
    updated_at: datetime

# Venue Search models
class Venue(BaseModel):
    name: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    venue_type: str  # "restaurant", "bakery", "venue"

class VenueSearchResult(BaseModel):
    venues: List[Venue]
    location: str
    query_type: str  # "lokale", "cukiernie"
    searched_at: datetime

# Task List Storage model
class TaskListStorage(BaseModel):
    """Model for storing task list in JSON"""
    plan_id: str
    conversation_id: str
    created_at: datetime
    tasks: List[dict]  # List of Task objects (serialized)
    status: str = "pending"  # "pending", "in_progress", "completed"

