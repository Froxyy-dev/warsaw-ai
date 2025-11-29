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
from llm_client import call_llm

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
    max_wait_seconds: int = 120,
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
    
    transcript_items = conversation_data.get('transcript', [])
    
    if not transcript_items:
        return "Transcript is empty (call may have failed or was very short)"
    
    lines = []
    lines.append("=" * 60)
    lines.append("TRANSKRYPT ROZMOWY")
    lines.append("=" * 60)
    
    for item in transcript_items:
        role = item.get('role', 'unknown')
        message = item.get('message', '')
        
        if role == 'agent':
            lines.append(f"\n🤖 AGENT: {message}")
        elif role == 'user':
            lines.append(f"\n👤 USER: {message}")
        else:
            lines.append(f"\n❓ {role.upper()}: {message}")
    
    lines.append("\n" + "=" * 60)
    
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
    
    # Wywołaj LLM
    llm_result = call_llm(
        prompt=prompt,
        system_message="Jesteś ekspertem od analizy rozmów. Zawsze zwracasz JSON.",
        model="gpt-4o-mini",
        response_format="json",
        temperature=0.1
    )
    
    if llm_result:
        # LLM zwrócił wynik
        print(f"✅ Analysis complete!")
        if '_meta' in llm_result:
            print(f"   Model: {llm_result['_meta'].get('model')}")
            print(f"   Tokens: {llm_result['_meta'].get('tokens')}\n")
        
        return {
            "success": llm_result.get("success", False),
            "should_continue": llm_result.get("should_continue", True),
            "reason": llm_result.get("reason", "No reason provided"),
            "confidence": llm_result.get("confidence", 0.0),
            "appointment_details": llm_result.get("appointment_details", {}),
            "llm_meta": llm_result.get("_meta", {})
        }
    else:
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

