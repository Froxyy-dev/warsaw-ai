"""
Quick test script to verify transcript parsing from ElevenLabs API
Run with: python test_transcript_parsing.py
"""
import os
import requests
from dotenv import load_dotenv
from voice_agent import format_transcript, debug_conversation_structure

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

def test_conversation_fetch(conversation_id: str):
    """
    Fetch a conversation from ElevenLabs API and test parsing
    
    Args:
        conversation_id: ID of a completed conversation
    """
    print(f"\n{'='*80}")
    print(f"Testing transcript parsing for conversation: {conversation_id}")
    print(f"{'='*80}\n")
    
    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"
    headers = {"xi-api-key": ELEVEN_API_KEY}
    
    try:
        print("📞 Fetching conversation from ElevenLabs API...")
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        
        conversation_data = resp.json()
        print(f"✅ Successfully fetched conversation data")
        print(f"   Status: {conversation_data.get('status')}")
        
        # Show debug structure
        debug_conversation_structure(conversation_data)
        
        # Test formatting
        print("\n" + "="*80)
        print("TESTING FORMAT_TRANSCRIPT()")
        print("="*80 + "\n")
        
        transcript = format_transcript(conversation_data)
        print(transcript)
        
        # Check if parsing was successful
        if "Failed to parse transcript" in transcript:
            print("\n❌ PARSING FAILED!")
            print("   Check the debug structure above to understand the format")
            return False
        elif "Transcript is empty" in transcript:
            print("\n⚠️  TRANSCRIPT IS EMPTY")
            print("   Call may have failed or was very short")
            return False
        else:
            print("\n✅ PARSING SUCCESSFUL!")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Failed to fetch conversation: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status code: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ELEVENLABS TRANSCRIPT PARSING TEST")
    print("="*80)
    
    # Check if API key is set
    if not ELEVEN_API_KEY:
        print("\n❌ ERROR: ELEVEN_API_KEY not found in .env file")
        exit(1)
    
    print("\nEnter a conversation ID to test (or press Enter to skip):")
    conversation_id = input("> ").strip()
    
    if conversation_id:
        test_conversation_fetch(conversation_id)
    else:
        print("\n📋 To use this script:")
        print("   1. Make a test call using voice_agent.py")
        print("   2. Copy the conversation_id from the output")
        print("   3. Run this script and paste the ID")
        print("\nExample conversation IDs look like: 'conv_abc123def456'")

