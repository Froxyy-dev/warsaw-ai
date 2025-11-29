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

