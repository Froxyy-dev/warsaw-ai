# 📞 AI Call Agent - Backend

System automatycznych połączeń telefonicznych z analizą LLM.

## 🚀 Szybki Test

```bash
# 1. Aktywuj venv
cd backend
source .venv/bin/activate

# 2. Zainstaluj zależności (jeśli jeszcze nie)
pip install -r requirements.txt

# 3. Skonfiguruj .env
cp .env.example .env
# Edytuj .env i dodaj swoje klucze

# 4. Uruchom test
python3 voice_agent.py
```

## 📁 Struktura Plików

```
backend/
├── voice_agent.py          # 🎯 Voice calling orchestration (ElevenLabs + LLM)
├── llm_client.py           # 🤖 Pure LLM interface (OpenAI/Anthropic)
├── task.py                 # 📋 Task & Place definitions
├── models.py               # 🗄️  FastAPI models (Call, Appointment)
├── main.py                 # 🚀 FastAPI server
├── routers/
│   ├── calls.py           # 📞 Endpoints for calls
│   └── appointments.py    # 📅 Endpoints for appointments
├── USAGE.md               # 📖 Detailed usage guide
└── ELEVENLABS_INTEGRATION.md  # 🔧 ElevenLabs integration docs
```

## 🔑 Wymagane Klucze API

### 1. ElevenLabs (wymagane)
- `ELEVEN_API_KEY` - Klucz API
- `ELEVEN_AGENT_ID` - ID agenta conversational AI
- `ELEVEN_AGENT_PHONE_NUMBER` - ID numeru telefonu (format: `phnum_xxxxx`)

Gdzie je znaleźć: https://elevenlabs.io/app/conversational-ai

### 2. OpenAI (opcjonalne, ale zalecane)
- `OPENAI_API_KEY` - Klucz API OpenAI

Do analizy transkryptów. Bez tego działa fallback (prosta heurystyka).

## 🎯 Główne Funkcje

### `voice_agent.execute_task(task: Task)`
**Główna funkcja** - dzwoni po kolei do miejsc aż się uda.

**Proces:**
1. Dzwoni do pierwszego miejsca
2. Czeka na zakończenie rozmowy (max 120s)
3. Pobiera i wyświetla transkrypt
4. Analizuje przez LLM
5. Jeśli sukces → STOP
6. Jeśli nie → Kolejne miejsce
7. Powtarza aż się uda lub skończą miejsca

### `voice_agent.initiate_call(task, place)`
Inicjuje pojedyncze połączenie przez ElevenLabs.

**Zwraca:**
```python
{
    "success": True,
    "conversation_id": "conv_xxxx",
    "callSid": "CAxxxx"
}
```

### `voice_agent.wait_for_conversation_completion(conversation_id)`
Czeka na zakończenie rozmowy i pobiera pełne dane + transkrypt.

### `voice_agent.analyze_call_with_llm(task, place, transcript)`
Analizuje transkrypt używając LLM (przez `llm_client`).

**Zwraca:**
```python
{
    "success": bool,
    "should_continue": bool,
    "reason": str,
    "confidence": 0.95,
    "appointment_details": {
        "date": "2025-12-01",
        "time": "18:30",
        "price": "50 PLN",
        ...
    }
}
```

### `llm_client.call_llm(prompt, system_message, ...)`
Pure LLM interface - użyj do dowolnych wywołań LLM.

## 📊 Przykład Użycia

```python
from task import Task, Place
from voice_agent import execute_task

# Stwórz task
task = Task(
    task_id="test-001",
    notes_for_agent="Umów wizytę u fryzjera na jutro 18:00",
    places=[
        Place(name="Salon A", phone="+48111222333"),
        Place(name="Salon B", phone="+48222333444"),
    ]
)

# Wykonaj
result = execute_task(task)

# Sprawdź wynik
if result['success']:
    print("✅ Wizyta umówiona!")
    for call in result['calls']:
        if call['success']:
            print(f"Miejsce: {call['place']}")
            print(f"Info: {call['analysis']['appointment_details']}")
```

## 🔧 Konfiguracja Agenta w ElevenLabs

**WAŻNE:** Dynamic variables muszą się zgadzać!

W dashboardzie agenta użyj:
- `{{_notes_for_agent_}}` - instrukcje/cel
- `{{_place_name_}}` - nazwa miejsca

## 🐛 Troubleshooting

### Agent się rozłącza
✅ Sprawdź czy dynamic variables się zgadzają (`_notes_for_agent_`, `_place_name_`)

### 404 Not Found
✅ Upewnij się że endpoint to `/v1/convai/twilio/outbound-call`

### Brak transkryptu
✅ Poczekaj dłużej - rozmowa może trwać
✅ Sprawdź w dashboardzie czy call się zakończył

### LLM nie działa
✅ Sprawdź `OPENAI_API_KEY` w `.env`
✅ Zainstaluj: `pip install openai`
✅ System użyje fallback jeśli LLM niedostępny

## 📚 Więcej Info

Zobacz `USAGE.md` dla szczegółowej dokumentacji i przykładów.

