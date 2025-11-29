"""
Voice Agent - Complete voice calling orchestration with ElevenLabs
Handles: call initiation, transcript fetching, LLM analysis, multi-place orchestration
"""
import os
import requests
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from task import Task, Place
from llm_client import LLMClient

load_dotenv()

# ElevenLabs Configuration
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_AGENT_ID = os.getenv("ELEVEN_AGENT_ID")
ELEVEN_AGENT_PHONE_NUMBER_ID = os.getenv("ELEVEN_AGENT_PHONE_NUMBER")

# API Endpoints
OUTBOUND_CALL_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
CONVERSATION_URL_TEMPLATE = "https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"


def initiate_call(task: Task, place: Place) -> Optional[Dict[str, Any]]:
    """
    Inicjuje połączenie głosowe do wybranego miejsca.
    
    Args:
        task: Task z instrukcjami dla agenta
        place: Miejsce do którego dzwonimy
        
    Returns:
        Dict z conversation_id i callSid lub None
    """
    payload = {
        "agent_id": ELEVEN_AGENT_ID,
        "agent_phone_number_id": ELEVEN_AGENT_PHONE_NUMBER_ID,
        "to_number": place.phone,
        "conversation_initiation_client_data": {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {
                "_notes_for_agent_": task.notes_for_agent,
                "_place_name_": place.name,
            }
        }
    }

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
    }

    print(f"\n{'='*60}")
    print(f"📞 Initiating call to: {place.name} ({place.phone})")
    print(f"{'='*60}\n")
    
    try:
        resp = requests.post(OUTBOUND_CALL_URL, headers=headers, json=payload)
        resp.raise_for_status()
        
        result = resp.json()
        
        print(f"✅ Call initiated successfully!")
        print(f"   Conversation ID: {result.get('conversation_id', 'N/A')}")
        print(f"   Call SID: {result.get('callSid', 'N/A')}\n")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to initiate call: {e}")
        return None


def wait_for_conversation_completion(
    conversation_id: str, 
    max_wait_seconds: int = 240,
    check_interval: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Czeka aż rozmowa się zakończy i zwraca pełne dane konwersacji.
    
    Args:
        conversation_id: ID konwersacji z ElevenLabs
        max_wait_seconds: Maksymalny czas oczekiwania
        check_interval: Co ile sekund sprawdzać status
        
    Returns:
        Dict z danymi konwersacji (zawiera transcript) lub None
    """
    headers = {"xi-api-key": ELEVEN_API_KEY}
    url = CONVERSATION_URL_TEMPLATE.format(conversation_id=conversation_id)
    
    print(f"⏳ Waiting for conversation to complete (max {max_wait_seconds}s)...")
    
    start_time = time.time()
    elapsed = 0
    
    while elapsed < max_wait_seconds:
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get('status', 'unknown')
                
                # Show progress
                print(f"   Status: {status} ({int(elapsed)}s)", end='\r')
                
                if status == 'done':
                    print(f"\n✅ Conversation completed! ({int(elapsed)}s)\n")
                    return data
                elif status in ['failed', 'error']:
                    print(f"\n❌ Conversation failed: {status}\n")
                    return data
                    
            elif resp.status_code == 404:
                print(f"\n❌ Conversation not found\n")
                return None
            
            time.sleep(check_interval)
            elapsed = time.time() - start_time
            
        except Exception as e:
            print(f"\n❌ Error fetching conversation: {e}\n")
            return None
    
    print(f"\n⏱️  Timeout: Conversation didn't complete in {max_wait_seconds}s\n")
    return None


def debug_conversation_structure(conversation_data: Dict[str, Any]) -> None:
    """
    Debug helper - prints the structure of conversation data from ElevenLabs API
    
    Args:
        conversation_data: Data from ElevenLabs API
    """
    import json
    
    print("\n" + "=" * 80)
    print("DEBUG: ELEVENLABS CONVERSATION DATA STRUCTURE")
    print("=" * 80)
    
    if not conversation_data:
        print("❌ No conversation data!")
        return
    
    print(f"\n📋 Top-level keys: {list(conversation_data.keys())}")
    
    for key, value in conversation_data.items():
        if isinstance(value, dict):
            print(f"\n📂 {key} (dict): {list(value.keys())}")
        elif isinstance(value, list):
            print(f"\n📂 {key} (list): length={len(value)}")
            if value and len(value) > 0:
                print(f"   First item type: {type(value[0])}")
                if isinstance(value[0], dict):
                    print(f"   First item keys: {list(value[0].keys())}")
                    if len(value[0]) > 0:
                        first_key = list(value[0].keys())[0]
                        print(f"   Sample: {first_key} = {value[0][first_key]}")
        else:
            print(f"\n📄 {key}: {value}")
    
    print("\n" + "=" * 80)
    print("Full JSON (first 500 chars):")
    print("=" * 80)
    print(json.dumps(conversation_data, indent=2)[:500])
    print("=" * 80 + "\n")


def format_transcript(conversation_data: Dict[str, Any]) -> str:
    """
    Formatuje transkrypt do czytelnej formy.
    
    Args:
        conversation_data: Dane konwersacji z API
        
    Returns:
        Sformatowany transkrypt jako string
    """
    if not conversation_data:
        return "No conversation data"
    
    # Try to get transcript from different possible locations
    transcript_items = conversation_data.get('transcript', [])
    
    # If no transcript, try analysis field (ElevenLabs sometimes puts it here)
    if not transcript_items and 'analysis' in conversation_data:
        transcript_items = conversation_data['analysis'].get('transcript', [])
    
    # Debug: log the structure if transcript is missing
    if not transcript_items:
        print(f"⚠️  No transcript found. Available keys: {list(conversation_data.keys())}")
        if 'analysis' in conversation_data:
            print(f"   Analysis keys: {list(conversation_data['analysis'].keys())}")
        return "Transcript is empty (call may have failed or was very short)\nStatus: " + conversation_data.get('status', 'unknown')
    
    lines = []
    lines.append("=" * 60)
    lines.append("TRANSKRYPT ROZMOWY")
    lines.append("=" * 60)
    
    # Handle different transcript formats
    for idx, item in enumerate(transcript_items):
        try:
            # Format 1: {role: "agent", message: "text"}
            if isinstance(item, dict) and 'role' in item:
                role = item.get('role', 'unknown')
                message = item.get('message', item.get('text', item.get('content', '')))
            # Format 2: {speaker: "agent", text: "text"}
            elif isinstance(item, dict) and 'speaker' in item:
                role = item.get('speaker', 'unknown')
                message = item.get('text', item.get('message', item.get('content', '')))
            # Format 3: String (fallback)
            elif isinstance(item, str):
                role = 'unknown'
                message = item
            else:
                print(f"⚠️  Unknown transcript item format at index {idx}: {item}")
                continue
            
            if role == 'agent':
                lines.append(f"\n🤖 AGENT: {message}")
            elif role == 'user':
                lines.append(f"\n👤 USER: {message}")
            else:
                lines.append(f"\n❓ {role.upper()}: {message}")
                
        except Exception as e:
            print(f"⚠️  Error parsing transcript item {idx}: {e}")
            continue
    
    lines.append("\n" + "=" * 60)
    
    # If no lines were added (all parsing failed), return error message
    if len(lines) <= 4:  # Just headers and footer
        return "Failed to parse transcript. Raw data logged to console."
    
    return "\n".join(lines)


def create_analysis_prompt(task: Task, place: Place, transcript: str) -> str:
    """
    Tworzy prompt dla LLM do analizy transkryptu.
    
    Args:
        task: Zadanie z celem rozmowy
        place: Miejsce do którego dzwoniono
        transcript: Sformatowany transkrypt
        
    Returns:
        Prompt dla LLM
    """
    return f"""
Jesteś ekspertem od analizy rozmów telefonicznych AI. Oceń czy rozmowa osiągnęła cel.

## CEL ROZMOWY:
{task.notes_for_agent}

## MIEJSCE:
Nazwa: {place.name}
Telefon: {place.phone}

## TRANSKRYPT:
{transcript}

## ZADANIE:
Przeanalizuj transkrypt i zwróć JSON:

1. **success** (bool): Czy cel został osiągnięty? (np. umówiono wizytę)
2. **should_continue** (bool): Czy dzwonić do kolejnych miejsc?
   - false jeśli cel osiągnięty
   - true jeśli nie udało się (spróbuj gdzie indziej)
3. **reason** (str): Krótkie wyjaśnienie (1-2 zdania)
4. **confidence** (float): Pewność oceny 0.0-1.0
5. **appointment_details** (dict): Wydobyte szczegóły:
   - date: YYYY-MM-DD lub null
   - time: HH:MM lub null
   - service: Rodzaj usługi lub null
   - price: Kwota lub null
   - additional_info: Inne informacje lub null

## FORMAT (JSON):
{{
    "success": true/false,
    "should_continue": false/true,
    "reason": "Wyjaśnienie",
    "confidence": 0.95,
    "appointment_details": {{
        "date": "2025-12-01",
        "time": "18:30",
        "service": "Strzyżenie",
        "price": "50 PLN",
        "additional_info": null
    }}
}}

WAŻNE:
- success=true TYLKO jeśli konkretnie ustalono wizytę/rezerwację
- Jeśli niepewność, lepiej should_continue=true (spróbuj gdzie indziej)
- Analizuj faktyczny przebieg, nie tylko cel

Zwróć TYLKO JSON.
"""


def analyze_call_with_llm(task: Task, place: Place, transcript: str) -> Dict[str, Any]:
    """
    Analizuje transkrypt używając LLM.
    
    Args:
        task: Zadanie
        place: Miejsce
        transcript: Transkrypt rozmowy
        
    Returns:
        Dict z analizą
    """
    print(f"\n{'='*60}")
    print("🤖 Analyzing transcript with LLM...")
    print(f"{'='*60}\n")
    
    prompt = create_analysis_prompt(task, place, transcript)
    
    # 🔍 VERBOSE: Show prompt summary
    print(f"📝 Prompt summary:")
    print(f"   Place: {place.name}")
    print(f"   Goal: {task.notes_for_agent[:100]}...")
    print(f"   Transcript length: {len(transcript)} characters")
    print(f"   Prompt length: {len(prompt)} characters\n")
    
    # Wywołaj LLM
    try:
        print(f"🔄 Sending to LLM (gemini-2.5-flash)...")
        llm_client = LLMClient(model="gemini-2.5-flash")
        response = llm_client.send(prompt)
        
        # 🔍 VERBOSE: Show raw response
        print(f"\n📨 Raw LLM response:")
        print(f"{'='*60}")
        print(response[:500])  # First 500 chars
        if len(response) > 500:
            print(f"... (total {len(response)} chars)")
        print(f"{'='*60}\n")
        
        # Parse JSON response - try code block first (LLM often wraps in markdown)
        import json
        import re
        
        llm_result = None
        
        # Try 1: Extract from markdown code block (most common)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            print(f"✅ Extracting JSON from markdown code block...")
            try:
                llm_result = json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse JSON from code block: {e}")
        
        # Try 2: Parse entire response as JSON (if not wrapped)
        if not llm_result:
            try:
                llm_result = json.loads(response)
                print(f"✅ Parsed response as raw JSON")
            except json.JSONDecodeError:
                pass
        
        # Try 3: Find any JSON object in response
        if not llm_result:
            json_match = re.search(r'(\{[^{]*"success"[^}]*\})', response, re.DOTALL)
            if json_match:
                print(f"✅ Extracting JSON object from text...")
                try:
                    llm_result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
        
        if not llm_result:
            raise ValueError("Could not extract valid JSON from LLM response")
        
        # 🔍 VERBOSE: Show parsed result
        print(f"✅ Analysis complete!")
        print(f"   Model: gemini-2.5-flash")
        print(f"\n📊 Parsed result:")
        print(f"   ✓ Success: {llm_result.get('success', False)}")
        print(f"   ✓ Should continue: {llm_result.get('should_continue', True)}")
        print(f"   ✓ Confidence: {llm_result.get('confidence', 0.0):.2f}")
        print(f"   ✓ Reason: {llm_result.get('reason', 'N/A')[:100]}")
        if llm_result.get('appointment_details'):
            print(f"   ✓ Details: {llm_result.get('appointment_details')}")
        print()
        
        return {
            "success": llm_result.get("success", False),
            "should_continue": llm_result.get("should_continue", True),
            "reason": llm_result.get("reason", "No reason provided"),
            "confidence": llm_result.get("confidence", 0.0),
            "appointment_details": llm_result.get("appointment_details", {}),
            "llm_response": llm_result,
            "llm_raw_response": response  # Keep raw for debugging
        }
    except ValueError as e:
        print(f"❌ Failed to extract JSON: {e}")
        print(f"   Raw response (first 300 chars): {response[:300]}...")
        llm_result = None
    except Exception as e:
        print(f"❌ LLM error: {e}")
        import traceback
        print(f"   Traceback:")
        traceback.print_exc()
        print(f"   Raw response (first 300 chars): {response[:300] if 'response' in locals() else 'N/A'}...")
        llm_result = None
    
    if not llm_result:
        # Fallback - prosta heurystyka
        print("⚠️  LLM unavailable, using fallback heuristics\n")
        
        transcript_lower = transcript.lower()
        
        # Heurystyka
        success_keywords = ['umówiony', 'umówiona', 'zarezerwowany', 'potwierdzam', 'zapisuję']
        failure_keywords = ['nie ma', 'brak', 'zamknięte', 'niestety', 'zajęte']
        
        success = any(kw in transcript_lower for kw in success_keywords)
        
        if success:
            should_continue = False
            reason = "Wykryto potwierdzenie wizyty (heurystyka)"
        elif any(kw in transcript_lower for kw in failure_keywords):
            should_continue = True
            reason = "Nie udało się - próbujemy kolejne miejsce (heurystyka)"
        else:
            should_continue = True
            reason = "Niejednoznaczny wynik - kontynuujemy (heurystyka)"
        
        return {
            "success": success,
            "should_continue": should_continue,
            "reason": reason,
            "confidence": 0.5,
            "appointment_details": {},
            "llm_meta": {"fallback": True}
        }


def execute_task(task: Task, max_attempts: Optional[int] = None) -> Dict[str, Any]:
    """
    Główna funkcja - wykonuje task dzwoniąc po kolei do miejsc aż się uda.
    
    Args:
        task: Task z listą miejsc i instrukcjami
        max_attempts: Maksymalna liczba prób (None = wszystkie miejsca)
        
    Returns:
        Dict z pełnym raportem wykonania
    """
    if not task.places:
        return {
            "success": False,
            "error": "No places to call",
            "calls": []
        }
    
    max_attempts = max_attempts or len(task.places)
    calls_log = []
    
    print(f"\n{'#'*70}")
    print(f"# TASK EXECUTION: {task.task_id}")
    print(f"# Places to call: {len(task.places)}")
    print(f"# Max attempts: {max_attempts}")
    print(f"{'#'*70}\n")
    
    for idx, place in enumerate(task.places[:max_attempts]):
        attempt_num = idx + 1
        
        print(f"\n{'='*70}")
        print(f"ATTEMPT {attempt_num}/{min(max_attempts, len(task.places))}: {place.name}")
        print(f"{'='*70}\n")
        
        try:
            # 1. Initiate call
            call_result = initiate_call(task, place)
            
            if not call_result or not call_result.get('conversation_id'):
                print("❌ Failed to initiate call\n")
                calls_log.append({
                    "place": place.name,
                    "phone": place.phone,
                    "success": False,
                    "error": "Call initiation failed"
                })
                continue
            
            conversation_id = call_result['conversation_id']
            
            # 2. Wait for completion and get transcript
            conversation_data = wait_for_conversation_completion(conversation_id)
            
            if not conversation_data:
                print("❌ Failed to get conversation data\n")
                calls_log.append({
                    "place": place.name,
                    "phone": place.phone,
                    "conversation_id": conversation_id,
                    "success": False,
                    "error": "Failed to fetch conversation"
                })
                continue
            
            # 3. Format and display transcript
            transcript = format_transcript(conversation_data)
            print(f"\n{transcript}\n")
            
            # 4. Analyze with LLM
            analysis = analyze_call_with_llm(task, place, transcript)
            
            # 5. Display analysis results
            print(f"{'='*60}")
            print("📊 ANALYSIS RESULTS:")
            print(f"{'='*60}")
            print(f"✅ Success: {analysis['success']}")
            print(f"🔄 Continue: {analysis['should_continue']}")
            print(f"📊 Confidence: {analysis.get('confidence', 0.0):.2f}")
            print(f"💬 Reason: {analysis['reason']}")
            
            details = analysis.get('appointment_details', {})
            if any(details.values()):
                print(f"\n📋 Appointment Details:")
                for key, value in details.items():
                    if value:
                        print(f"   {key}: {value}")
            print(f"{'='*60}\n")
            
            # 6. Log call
            calls_log.append({
                "place": place.name,
                "phone": place.phone,
                "conversation_id": conversation_id,
                "transcript": transcript,
                "analysis": analysis,
                "success": analysis['success']
            })
            
            # 7. Decision: continue or stop?
            if analysis['success'] and not analysis['should_continue']:
                print(f"{'='*70}")
                print(f"🎉 SUCCESS! Goal achieved at: {place.name}")
                print(f"{'='*70}\n")
                break
            
            print(f"{'='*70}")
            print(f"⏭️  Moving to next place...")
            print(f"{'='*70}\n")
            
            # Short pause before next call
            if idx < len(task.places) - 1:
                time.sleep(5)
                
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            calls_log.append({
                "place": place.name,
                "phone": place.phone,
                "success": False,
                "error": str(e)
            })
    
    # Final summary
    successful = [c for c in calls_log if c.get('success')]
    
    print(f"\n{'#'*70}")
    print(f"# TASK SUMMARY")
    print(f"{'#'*70}")
    print(f"Task ID: {task.task_id}")
    print(f"Total calls: {len(calls_log)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(calls_log) - len(successful)}")
    print(f"{'#'*70}\n")
    
    return {
        "success": len(successful) > 0,
        "task_id": task.task_id,
        "total_calls": len(calls_log),
        "successful_calls": len(successful),
        "calls": calls_log
    }


if __name__ == "__main__":
    # Test with example task
    from task import test_task
    
    print("Starting voice agent test...")
    result = execute_task(test_task)
    
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Total calls: {result['total_calls']}")
    print(f"Successful: {result['successful_calls']}")
    print("="*70)

