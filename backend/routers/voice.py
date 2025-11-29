from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from fastapi.responses import StreamingResponse
from elevenlabs.client import ElevenLabs
import os
from llm_client import LLMClient

router = APIRouter()

llm_client = LLMClient()
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        
        # Use the content_type from the UploadFile object
        transcription = llm_client.transcribe(audio_bytes, file.content_type)
        
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
