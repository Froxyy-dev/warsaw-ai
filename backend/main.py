from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import calls, appointments, chat
import dotenv 
dotenv.load_dotenv()

app = FastAPI(
    title="AI Call Agent API",
    description="API for AI-powered call agent that schedules appointments",
    version="1.0.0"
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(calls.router, prefix="/api/calls", tags=["calls"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "RESPONSE",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

