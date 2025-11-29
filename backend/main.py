from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import calls, appointments
import dotenv 
dotenv.load_dotenv()

app = FastAPI(
    title="AI Call Agent API",
    description="API for AI-powered call agent that schedules appointments",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calls.router, prefix="/api/calls", tags=["calls"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])

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

