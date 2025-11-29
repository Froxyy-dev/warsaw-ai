# AI Call Agent - Instrukcja Użycia

## 🚀 Szybki Start

### 1. Konfiguracja

Upewnij się że masz plik `.env` z wymaganymi kluczami:

```env
# ElevenLabs API
ELEVEN_API_KEY=sk_your_key_here
ELEVEN_AGENT_ID=agent_your_id_here
ELEVEN_AGENT_PHONE_NUMBER=phnum_your_id_here

# OpenAI (opcjonalne - dla analizy LLM)
OPENAI_API_KEY=sk-your_openai_key
LLM_PROVIDER=openai
```

### 2. Podstawowe Użycie

```python
from task import Task, Place
from voice_agent import execute_task

# Stwórz task
task = Task(
    task_id="appointment-001",
    notes_for_agent="""
    Umów wizytę dla Mateusza u fryzjera na jutro o 18:00.
    Numer telefonu Mateusza: +48 123 456 789.
    Jeśli 18:00 nie jest dostępne, spróbuj 18:30 lub 17:30.
    """,
    places=[
        Place(name="Salon Alpha", phone="+48111222333"),
        Place(name="Barber Beta", phone="+48222333444"),
        Place(name="Fryzjer Gamma", phone="+48333444555"),
    ]
)

# Wykonaj task - dzwoni po kolei aż się uda
result = execute_task(task)

print(f"Success: {result['success']}")
print(f"Wykonano {result['total_calls']} połączeń")
```

## 📋 Jak to działa

### Flow wykonania:

1. **Inicjacja połączenia** → ElevenLabs dzwoni do pierwszego miejsca
2. **Czekanie** → System czeka na zakończenie rozmowy (max 120s)
3. **Pobieranie transkryptu** → Otrzymujemy pełny transkrypt
4. **Analiza LLM** → GPT-4 analizuje czy cel został osiągnięty
5. **Decyzja** → 
   - Jeśli sukces → KONIEC
   - Jeśli nie → Dzwoni do kolejnego miejsca
6. **Powtórz** → Aż się uda lub skończą miejsca

## 🎯 Tworzenie Task

```python
from task import Task, Place

task = Task(
    task_id="unique-id-123",
    notes_for_agent="""
    WAŻNE: Te notatki są wysyłane do agenta jako {{_notes_for_agent_}}
    
    Powinny zawierać:
    - Kim jest klient
    - Jaki jest cel połączenia
    - Preferowane terminy/opcje
    - Numer telefonu klienta (jeśli potrzebny)
    - Co robić jeśli pierwsza opcja nie jest dostępna
    - Inne ważne szczegóły
    """,
    places=[
        Place(
            name="Nazwa firmy 1",  # Wysyłane jako {{_place_name_}}
            phone="+48123456789"
        ),
        Place(
            name="Nazwa firmy 2",
            phone="+48987654321"
        ),
        # ... więcej miejsc
    ]
)
```

## 📊 Analiza Wyników

```python
result = execute_task(task)

# Sprawdź ogólny sukces
if result['success']:
    print("✅ Task wykonany pomyślnie!")
else:
    print("❌ Nie udało się wykonać taska")

# Szczegóły każdego połączenia
for call in result['calls']:
    print(f"\n📞 {call['place']}")
    print(f"   Tel: {call['phone']}")
    
    if call.get('success'):
        print("   ✅ Sukces!")
        
        # Wydobyte informacje
        analysis = call.get('analysis', {})
        info = analysis.get('extracted_info', {})
        
        if info.get('date'):
            print(f"   📅 Data: {info['date']}")
        if info.get('time'):
            print(f"   🕐 Godzina: {info['time']}")
        if info.get('price'):
            print(f"   💰 Cena: {info['price']}")
    else:
        print(f"   ❌ Niepowodzenie: {call.get('error', 'Unknown')}")
    
    # Transkrypt
    if call.get('transcript'):
        print(f"\n   Transkrypt:")
        print(call['transcript'])
```

## 🤖 Analiza LLM

System używa OpenAI GPT-4 do analizy transkryptów. LLM:

1. **Czyta cel** z `notes_for_agent`
2. **Analizuje transkrypt** rozmowy
3. **Określa czy cel osiągnięty**
4. **Wydobywa informacje** (data, godzina, cena)
5. **Decyduje czy kontynuować** dzwonienie

### Struktura odpowiedzi LLM:

```json
{
  "success": true,
  "should_continue": false,
  "reason": "Umówiono wizytę na 2025-12-01 o 18:30",
  "confidence": 0.95,
  "appointment_details": {
    "date": "2025-12-01",
    "time": "18:30",
    "service": "Strzyżenie męskie",
    "price": "50 PLN",
    "additional_info": "Fryzjer: Ania"
  },
  "call_quality": {
    "agent_performance": "Professional and clear",
    "customer_response": "positive",
    "technical_issues": null
  }
}
```

## 🔧 Konfiguracja LLM

### Używanie LLM Client

```python
from llm_client import call_llm

# Podstawowe wywołanie
result = call_llm(
    prompt="Your prompt here",
    system_message="You are helpful assistant",
    model="gpt-4o-mini",
    response_format="json"
)

# Wynik zawiera:
# - Odpowiedź od LLM
# - _meta z informacjami (model, tokens, provider)
```

### Voice Agent automatycznie używa LLM

`voice_agent.py` automatycznie wywołuje LLM do analizy transkryptów.

### Bez LLM (fallback):

Jeśli nie masz klucza OpenAI, `voice_agent` użyje prostej heurystyki:
- Szuka słów jak "umówiony", "zarezerwowany", "potwierdzam"
- Podstawowa analiza, ale działa bez kosztów API

## 📝 Przykłady Tasków

### Przykład 1: Fryzjer

```python
task = Task(
    task_id="haircut-001",
    notes_for_agent="""
    Umów wizytę dla Mateusza na strzyżenie męskie.
    Preferowany termin: jutro 18:00
    Alternatywy: 18:30, 17:30
    Tel. Mateusza: +48 123 456 789
    Preferuje krótkie, proste strzyżenie.
    """,
    places=[
        Place(name="Barber Shop A", phone="+48111222333"),
        Place(name="Hair Studio B", phone="+48222333444"),
    ]
)
```

### Przykład 2: Restauracja

```python
task = Task(
    task_id="restaurant-001",
    notes_for_agent="""
    Zarezerwuj stolik na 4 osoby na piątek wieczór.
    Preferowana godzina: 19:00
    Jeśli nie ma: 19:30 lub 20:00
    Imię na rezerwację: Kowalski
    """,
    places=[
        Place(name="Restauracja Roma", phone="+48111222333"),
        Place(name="Trattoria Bella", phone="+48222333444"),
    ]
)
```

### Przykład 3: Lekarz

```python
task = Task(
    task_id="doctor-001",
    notes_for_agent="""
    Umów wizytę u lekarza rodzinnego dla pani Anny Nowak.
    Preferowany termin: najbliższy dostępny
    PESEL: 12345678901
    Tel. pacjentki: +48 123 456 789
    Powód wizyty: kontrola okresowa
    """,
    places=[
        Place(name="Przychodnia Medica", phone="+48111222333"),
        Place(name="Centrum Zdrowia", phone="+48222333444"),
    ]
)
```

## 🐛 Debugging

### Włącz szczegółowe logi:

System automatycznie wyświetla:
- Status każdego połączenia
- Pełny transkrypt rozmowy
- Analizę LLM z uzasadnieniem
- Podsumowanie wykonania

### Sprawdź w ElevenLabs dashboard:

https://elevenlabs.io/app/conversational-ai/calls

Tam zobaczysz:
- Nagrania audio połączeń
- Szczegółowe metryki
- Status każdego calla

## ⚠️ Ważne Uwagi

1. **Dynamic Variables**: Nazwy zmiennych MUSZĄ się zgadzać z placeholderami w agencie!
   - Domyślnie: `_notes_for_agent_` i `_place_name_`

2. **Timeout**: Rozmowa ma 120s na zakończenie, potem timeout

3. **Koszty**: 
   - ElevenLabs: Per minuta rozmowy
   - OpenAI: Per token (~$0.001-0.01 na analizę)

4. **Rate Limits**: Pauza 5s między połączeniami

5. **Język**: Agent mówi po polsku (konfiguracja w dashboardzie)

## 🔄 Integracja z FastAPI

```python
# W routes/calls.py
from voice_agent import execute_task
from task import Task, Place

@router.post("/execute-task")
async def run_voice_task(task_data: dict):
    task = Task(
        task_id=task_data['task_id'],
        notes_for_agent=task_data['notes'],
        places=[Place(**p) for p in task_data['places']]
    )
    
    result = execute_task(task)
    return result
```

## 📚 Więcej Informacji

- [ElevenLabs Docs](https://elevenlabs.io/docs/agents-platform)
- [OpenAI API Docs](https://platform.openai.com/docs)
- `ELEVENLABS_INTEGRATION.md` - Szczegóły integracji

