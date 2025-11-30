# 🐛 Przewodnik Debugowania

## Problem: Wiadomości się nie wyświetlają

### Krok 1: Sprawdź Backend

```bash
cd backend
source .venv/bin/activate  # lub venv/Scripts/activate na Windows
uvicorn main:app --reload
```

**Powinno się wyświetlić:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Krok 2: Test Backend API

W nowym terminalu:
```bash
python3 test_chat.py
```

**Jeśli działa**, zobaczysz:
```
✅ Created conversation: ...
✅ Got response: ...
✅ All tests passed!
```

**Jeśli nie działa**, sprawdź:
- Czy backend działa (krok 1)
- Czy masz GEMINI_API_KEY w .env
- Błędy w terminalu backendu

### Krok 3: Sprawdź Frontend

```bash
cd frontend
npm start
```

**Otwórz:** http://localhost:3000

### Krok 4: Sprawdź Console w Przeglądarce

1. Otwórz DevTools (F12)
2. Przejdź do zakładki **Console**
3. Wyślij wiadomość
4. Szukaj logów:

```
Conversation ID: ...
Sending message: ...
Got response: ...
Reloading conversation...
Updated conversation: ...
```

### Częste Problemy:

#### ❌ "Failed to send message: Network Error"
**Rozwiązanie:**
- Backend nie działa
- Sprawdź czy backend jest na http://localhost:8000
- Sprawdź CORS w backend/main.py

#### ❌ "Failed to send message: 500"
**Rozwiązanie:**
- Błąd w backendzie
- Sprawdź terminal backendu
- Prawdopodobnie brak GEMINI_API_KEY

#### ❌ "GEMINI_API_KEY not found"
**Rozwiązanie:**
1. Stwórz plik `backend/.env`
2. Dodaj: `GEMINI_API_KEY=twój_klucz_tutaj`
3. Restart backendu

#### ❌ Wiadomości nie się wyświetlają ale nie ma błędów
**Rozwiązanie:**
- Sprawdź czy `database/conversations/` istnieje
- Sprawdź uprawnienia do zapisu
- Zobacz console.log w przeglądarce

### Krok 5: Sprawdź Pliki JSON

```bash
ls -la database/conversations/
cat database/conversations/conversation_*.json
```

Powinny być pliki z konwersacjami.

### Quick Fix

Jeśli nic nie działa, spróbuj:

```bash
# Wyczyść wszystko
rm -rf database/conversations/*
rm -rf frontend/node_modules/.cache

# Backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (nowy terminal)
cd frontend
npm start
```

### Kontakt z Gemini API

Sprawdź czy Gemini API działa:

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Cześć!"
)
print(response.text)
```

Jeśli to działa, problem jest gdzie indziej.

