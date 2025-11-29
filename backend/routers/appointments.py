from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from models import Appointment, AppointmentResponse, AppointmentStatus

router = APIRouter()

# In-memory storage (replace with database later)
appointments_db = []

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    call_id: str = None,
    customer_name: str = None,
    phone_number: str = None,
    scheduled_date: str = None,
    notes: str = None
):
    """
    Create a new appointment (usually after successful call)
    """
    appointment = Appointment(
        id=str(uuid.uuid4()),
        call_id=call_id,
        customer_name=customer_name,
        phone_number=phone_number,
        scheduled_date=scheduled_date,
        status=AppointmentStatus.SCHEDULED,
        notes=notes,
        created_at=datetime.now()
    )
    
    appointments_db.append(appointment)
    
    return AppointmentResponse(
        success=True,
        appointment=appointment,
        message="Appointment created successfully"
    )

@router.get("/", response_model=List[Appointment])
async def get_appointments(status: AppointmentStatus = None):
    """
    Get all appointments, optionally filtered by status
    """
    if status:
        return [apt for apt in appointments_db if apt.status == status]
    return appointments_db

@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """
    Get a specific appointment by ID
    """
    for apt in appointments_db:
        if apt.id == appointment_id:
            return apt
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.patch("/{appointment_id}/status")
async def update_appointment_status(appointment_id: str, status: AppointmentStatus):
    """
    Update appointment status
    """
    for apt in appointments_db:
        if apt.id == appointment_id:
            apt.status = status
            return {"success": True, "appointment": apt}
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """
    Delete an appointment
    """
    global appointments_db
    appointments_db = [apt for apt in appointments_db if apt.id != appointment_id]
    return {"success": True, "message": "Appointment deleted"}

