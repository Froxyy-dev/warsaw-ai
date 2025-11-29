"""
Test pojedynczego połączenia - sprawdza czy transkrypt się pobiera
"""
import os
import time
from dotenv import load_dotenv
from voice_agent import initiate_call, wait_for_conversation_completion, format_transcript, debug_conversation_structure
from task import Task, Place

load_dotenv()

# Test configuration
TEST_PLACE = Place(
    name="Test Phone",
    phone="+48886859039"  # POC hardcoded number
)

TEST_TASK = Task(
    task_id="test-single-call",
    notes_for_agent="To jest test. Powiedz 'Test udany' i zakończ rozmowę.",
    places=[TEST_PLACE]
)

def main():
    print("\n" + "="*80)
    print("TEST POJEDYNCZEGO POŁĄCZENIA - SPRAWDZANIE TRANSKRYPTU")
    print("="*80 + "\n")
    
    # Step 1: Initiate call
    print("📞 KROK 1: Inicjuję połączenie...")
    print(f"   Miejsce: {TEST_PLACE.name}")
    print(f"   Telefon: {TEST_PLACE.phone}")
    print(f"   Notatki: {TEST_TASK.notes_for_agent}\n")
    
    call_result = initiate_call(TEST_TASK, TEST_PLACE)
    
    if not call_result:
        print("❌ BŁĄD: Nie udało się zainicjować połączenia")
        return False
    
    if not call_result.get('conversation_id'):
        print("❌ BŁĄD: Brak conversation_id w odpowiedzi")
        print(f"   Otrzymane dane: {call_result}")
        return False
    
    conversation_id = call_result['conversation_id']
    print(f"✅ Połączenie zainicjowane!")
    print(f"   Conversation ID: {conversation_id}")
    print(f"   Call SID: {call_result.get('callSid', 'N/A')}\n")
    
    # Step 2: Wait for completion
    print("📞 KROK 2: Czekam na zakończenie rozmowy...")
    print("   (Maksymalnie 120 sekund)\n")
    
    conversation_data = wait_for_conversation_completion(conversation_id, max_wait_seconds=120)
    
    if not conversation_data:
        print("❌ BŁĄD: Nie udało się pobrać danych rozmowy")
        return False
    
    print(f"✅ Rozmowa zakończona!")
    print(f"   Status: {conversation_data.get('status', 'unknown')}\n")
    
    # Step 3: Debug structure
    print("📞 KROK 3: Analiza struktury danych...")
    debug_conversation_structure(conversation_data)
    
    # Step 4: Try to format transcript
    print("\n📞 KROK 4: Próba wyciągnięcia transkryptu...")
    print("="*80 + "\n")
    
    transcript = format_transcript(conversation_data)
    print(transcript)
    print("\n" + "="*80)
    
    # Step 5: Analysis
    print("\n📊 ANALIZA WYNIKU:\n")
    
    if "Failed to parse transcript" in transcript:
        print("❌ PARSOWANIE NIE UDAŁO SIĘ")
        print("   Transkrypt nie mógł być sparsowany")
        print("   Sprawdź debug structure powyżej")
        return False
    
    if "Transcript is empty" in transcript:
        print("⚠️  TRANSKRYPT PUSTY")
        print("   Rozmowa mogła być zbyt krótka lub nie udana")
        print(f"   Status rozmowy: {conversation_data.get('status')}")
        
        # Check if there's any data at all
        if conversation_data.get('transcript'):
            print(f"   ⚠️  Ale klucz 'transcript' ISTNIEJE: {type(conversation_data.get('transcript'))}")
            print(f"   Długość: {len(conversation_data.get('transcript', []))}")
        else:
            print("   ❌ Klucz 'transcript' NIE ISTNIEJE w danych")
        
        return False
    
    print("✅ TRANSKRYPT ZOSTAŁ POPRAWNIE SPARSOWANY!")
    print(f"   Długość transkryptu: {len(transcript)} znaków")
    
    # Count items
    lines = transcript.split('\n')
    agent_lines = [l for l in lines if '🤖 AGENT:' in l]
    user_lines = [l for l in lines if '👤 USER:' in l]
    
    print(f"   Wypowiedzi agenta: {len(agent_lines)}")
    print(f"   Wypowiedzi użytkownika: {len(user_lines)}")
    
    return True


if __name__ == "__main__":
    # Check env variables
    required_vars = ['ELEVEN_API_KEY', 'ELEVEN_AGENT_ID', 'ELEVEN_AGENT_PHONE_NUMBER']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"\n❌ BŁĄD: Brakujące zmienne środowiskowe: {', '.join(missing)}")
        print("   Sprawdź plik .env\n")
        exit(1)
    
    try:
        success = main()
        
        print("\n" + "="*80)
        if success:
            print("🎉 TEST ZAKOŃCZONY SUKCESEM!")
            print("   Transkrypt działa poprawnie")
            print("   Możesz teraz testować end-to-end workflow")
        else:
            print("❌ TEST NIE POWIÓDŁ SIĘ")
            print("   Sprawdź logi powyżej")
            print("   Napraw problemy przed testowaniem end-to-end")
        print("="*80 + "\n")
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test przerwany przez użytkownika")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ NIEOCZEKIWANY BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

