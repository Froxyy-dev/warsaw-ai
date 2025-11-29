"""
Test analizy transkryptu przez LLM
"""
from voice_agent import analyze_call_with_llm
from task import Task, Place

# Test transkrypt z prawdziwego call
TEST_TRANSCRIPT = """
============================================================
TRANSKRYPT ROZMOWY
============================================================

🤖 AGENT: Dzień dobry, czy dodzwoniłem się do Test Phone?  
Z tej strony Michał, asystent Mateusza z Call AI. Mam krótką sprawę do załatwienia w jego imieniu.

👤 USER: Dzień dobry, tak jako sprawa.

🤖 AGENT: Świetnie. Dzwonię, żeby przekazać, że test jest udany. Dziękuję bardzo za pomoc i życzę miłego dnia.

👤 USER: Dziękuję, do widzenia.

🤖 AGENT: Do widzenia.

============================================================
"""

TEST_TASK = Task(
    task_id="test-analysis",
    notes_for_agent="To jest test. Powiedz 'Test udany' i zakończ rozmowę.",
    places=[Place(name="Test Phone", phone="+48886859039")]
)

TEST_PLACE = Place(name="Test Phone", phone="+48886859039")

def main():
    print("\n" + "="*80)
    print("TEST ANALIZY TRANSKRYPTU PRZEZ LLM")
    print("="*80 + "\n")
    
    print("📝 Test transkrypt:")
    print(TEST_TRANSCRIPT)
    
    print("\n" + "="*80)
    print("🤖 Wywołuję analyze_call_with_llm()...")
    print("="*80 + "\n")
    
    try:
        analysis = analyze_call_with_llm(TEST_TASK, TEST_PLACE, TEST_TRANSCRIPT)
        
        print("\n" + "="*80)
        print("📊 WYNIK ANALIZY:")
        print("="*80)
        print(f"✓ Success: {analysis.get('success')}")
        print(f"✓ Should continue: {analysis.get('should_continue')}")
        print(f"✓ Confidence: {analysis.get('confidence', 0.0):.2f}")
        print(f"✓ Reason: {analysis.get('reason')}")
        print(f"✓ Appointment details: {analysis.get('appointment_details')}")
        
        if analysis.get('llm_raw_response'):
            print(f"\n📨 Raw LLM response (first 300 chars):")
            print(analysis.get('llm_raw_response')[:300])
        
        print("\n" + "="*80)
        
        if analysis.get('success') is not None:
            print("✅ ANALIZA DZIAŁA POPRAWNIE!")
            return True
        else:
            print("⚠️  ANALIZA ZWRÓCIŁA NIEKOMPLETNY WYNIK")
            return False
            
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

