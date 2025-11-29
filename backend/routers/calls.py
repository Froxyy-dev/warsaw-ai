from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from models import Call, CallRequest, CallResponse, CallStatus

router = APIRouter()

# In-memory storage (replace with database later)
calls_db = []

@router.post("/", response_model=CallResponse)
async def create_call(call_request: CallRequest):
    """
    Initiate a new AI call to schedule an appointment
    """
    call = Call(
        id=str(uuid.uuid4()),
        phone_number=call_request.phone_number,
        purpose=call_request.purpose,
        customer_name=call_request.customer_name,
        status=CallStatus.PENDING,
        created_at=datetime.now()
    )
    
    calls_db.append(call)
    
    # TODO: Integrate with actual AI call service (e.g., Twilio + OpenAI)
    # For now, we'll simulate the call
    
    return CallResponse(
        success=True,
        call=call,
        message=f"Call initiated to {call_request.phone_number}"
    )

@router.get("/", response_model=List[Call])
async def get_calls(status: CallStatus = None):
    """
    Get all calls, optionally filtered by status
    """
    if status:
        return [call for call in calls_db if call.status == status]
    return calls_db

@router.get("/{call_id}", response_model=Call)
async def get_call(call_id: str):
    """
    Get a specific call by ID
    """
    for call in calls_db:
        if call.id == call_id:
            return call
    raise HTTPException(status_code=404, detail="Call not found")

@router.patch("/{call_id}/status")
async def update_call_status(call_id: str, status: CallStatus):
    """
    Update call status (for simulation/testing)
    """
    for call in calls_db:
        if call.id == call_id:
            call.status = status
            if status == CallStatus.COMPLETED:
                call.completed_at = datetime.now()
                call.transcript = "Sample transcript: Customer agreed to appointment on specified date."
            return {"success": True, "call": call}
    raise HTTPException(status_code=404, detail="Call not found")

@router.delete("/{call_id}")
async def delete_call(call_id: str):
    """
    Delete a call record
    """
    global calls_db
    calls_db = [call for call in calls_db if call.id != call_id]
    return {"success": True, "message": "Call deleted"}

