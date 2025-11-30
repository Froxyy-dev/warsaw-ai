# ElevenLabs Integration - Dokumentacja

## ✅ Działająca Konfiguracja

### Endpoint
```python
OUTBOUND_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
```

### Struktura Payloadu
```python
payload = {
    "agent_id": ELEVEN_AGENT_ID,
    "agent_phone_number_id": ELEVEN_AGENT_PHONE_NUMBER_ID,  # Format: phnum_xxxxx
    "to_number": "+48123456789",  # Numer odbiorcy
    "conversation_initiation_client_data": {
        "type": "conversation_initiation_client_data",
        "dynamic_variables": {
            "notes_for_agent": "Twoje instrukcje dla agenta...",
            "custom_var": "Dowolne dodatkowe zmienne"
        }
    }
}
```

## 🔑 Konfiguracja .env

```env
# ElevenLabs
ELEVEN_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxx
ELEVEN_AGENT_ID=agent_xxxxxxxxxxxxxxxxxxxxxx
ELEVEN_AGENT_PHONE_NUMBER=phnum_xxxxxxxxxxxxxxxxxxxxxx

# LLM for transcript analysis
LLM_PROVIDER=openai  # openai, anthropic, etc.
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
```

### Jak znaleźć te wartości:

1. **ELEVEN_API_KEY**
   - Dashboard → Profile → API Keys
   - https://elevenlabs.io/app/settings/api-keys

2. **ELEVEN_AGENT_ID**
   - Dashboard → Conversational AI → wybierz agenta
   - ID jest w URL: `...conversational-ai/agent_xxxxx`

3. **ELEVEN_AGENT_PHONE_NUMBER** (WAŻNE: to ID, nie numer!)
   - Dashboard → Phone Numbers
   - Skopiuj **Phone Number ID** (format: `phnum_xxxxx`)
   - https://elevenlabs.io/app/conversational-ai/phone-numbers

## 📞 Użycie

```python
from eleven_client import start_call_for_task
from task import Task, Place

# Stwórz task
task = Task(
    task_id="test-001",
    notes_for_agent="Umów wizytę u fryzjera na jutro 18:00",
    places=[
        Place(name="Salon XYZ", phone="+48123456789")
    ]
)

# Zainicjuj połączenie
response = start_call_for_task(task)

# Odpowiedź zawiera:
# - conversation_id: Użyj do śledzenia rozmowy
# - callSid: Twilio Call SID
```

## 📊 Monitoring

Po zainicjowaniu połączenia możesz:

1. **Sprawdzić status** w dashboardzie:
   https://elevenlabs.io/app/conversational-ai/calls

2. **Pobrać transkrypcję** (API):
   ```python
   GET https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}
   ```

3. **Webhook events** (opcjonalne):
   Skonfiguruj webhook w dashboardzie aby otrzymywać eventy o statusie połączenia

## 🎯 Dynamic Variables

**WAŻNE:** Nazwy zmiennych MUSZĄ się zgadzać z placeholderami w agencie!

Sprawdź w dashboardzie jakie placeholders ma Twój agent i używaj DOKŁADNIE tych samych nazw.

Przykład - jeśli agent ma:
```
{{_notes_for_agent_}} i {{_place_name_}}
```

To wysyłaj:
```python
dynamic_variables = {
    "_notes_for_agent_": "Instrukcje dla AI",  # z podkreślnikami!
    "_place_name_": "Nazwa miejsca",           # z podkreślnikami!
}
```

Możesz dodawać własne zmienne:
```python
dynamic_variables = {
    "_notes_for_agent_": "Instrukcje dla AI",
    "_place_name_": "Studio XYZ",
    "_customer_phone_": "+48123456789",  # własna zmienna
    "_preferred_date_": "2025-12-01",     # własna zmienna
    # ...dowolne inne (pamietaj o dodaniu ich do promptu agenta!)
}
```

Agent może używać tych zmiennych w trakcie rozmowy przez `{{_nazwa_zmiennej_}}`.

## 🚨 Częste Błędy

### 400 Bad Request - "phone number id required"
❌ Używasz numeru telefonu zamiast ID
✅ Użyj `phnum_xxxxx` z dashboardu

### 401 Unauthorized
❌ Nieprawidłowy API key
✅ Sprawdź `ELEVEN_API_KEY` w `.env`

### 404 Not Found
❌ Zły endpoint lub agent_id
✅ Upewnij się że endpoint to `/v1/convai/twilio/outbound-call`

### 403 Forbidden - "Terms & Conditions"
✅ Używaj `/twilio/outbound-call` zamiast `/batch-calling/submit`

## 📚 Więcej Informacji

- Dashboard: https://elevenlabs.io/app/conversational-ai
- Dokumentacja: https://elevenlabs.io/docs/agents-platform
- API Reference: https://elevenlabs.io/docs/api-reference/conversational-ai

