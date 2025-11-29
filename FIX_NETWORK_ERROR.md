# 🔧 Fix: Network Error / Bad Request

## Szybka diagnoza

### Krok 1: Sprawdź czy backend działa

```bash
curl http://localhost:8000/api/health
```

**Jeśli działa**, zobaczysz:
```json
{"status":"healthy"}
```

**Jeśli nie działa**:
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### Krok 2: Sprawdź chat service

```bash
curl http://localhost:8000/api/chat/health
```

**Powinno zwrócić:**
```json
{
  "status": "healthy",
  "service": "chat",
  "storage_ready": true
}
```

### Krok 3: Test tworzenia konwersacji

```bash
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Jeśli działa**, zobaczysz:
```json
{
  "success": true,
  "conversation": {
    "id": "...",
    "messages": [],
    ...
  }
}
```

**Jeśli zwraca błąd**, sprawdź terminal backendu - tam będą szczegóły.

### Krok 4: Pełny test

```bash
chmod +x quick_test.sh
./quick_test.sh
```

## Możliwe problemy i rozwiązania

### Problem 1: "Connection refused"
**Przyczyna:** Backend nie działa  
**Rozwiązanie:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### Problem 2: "404 Not Found"
**Przyczyna:** Złe URL lub backend nie ma routera  
**Rozwiązanie:** 
- Sprawdź czy backend pokazuje: `Including router /api/chat`
- URL powinno być: `http://localhost:8000/api/chat/conversations/`

### Problem 3: "500 Internal Server Error"
**Przyczyna:** Błąd w backendzie  
**Rozwiązanie:**
1. Zobacz terminal backendu - tam będzie stack trace
2. Prawdopodobnie brak GEMINI_API_KEY
3. Stwórz `backend/.env`:
   ```
   GEMINI_API_KEY=twoj_klucz
   ```

### Problem 4: "CORS Error"
**Przyczyna:** Frontend nie może połączyć się z backendem  
**Rozwiązanie:** Sprawdź `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problem 5: "Network Error" w przeglądarce
**Przyczyna:** Backend nie odpowiada lub złe URL  
**Rozwiązanie:**
1. Sprawdź `frontend/src/api/axios.js`:
   ```javascript
   baseURL: 'http://localhost:8000/api'
   ```
2. Sprawdź czy backend działa: `curl http://localhost:8000/api/health`

## Quick Fix - Restart wszystkiego

```bash
# 1. Zatrzymaj wszystko (Ctrl+C w terminalach)

# 2. Wyczyść cache
rm -rf database/conversations/*

# 3. Backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. Frontend (nowy terminal)
cd frontend
npm start

# 5. Test (nowy terminal)
./quick_test.sh
```

## Sprawdzenie logów

### Backend logs:
Patrz w terminal gdzie uruchomiłeś uvicorn. Szukaj:
- `ERROR` - błędy
- `WARNING` - ostrzeżenia
- Stack traces

### Frontend logs:
1. Otwórz DevTools (F12)
2. Console tab
3. Network tab - zobacz failed requests
4. Kliknij na failed request → Preview/Response

## Najczęstszy problem

**90% przypadków to brak GEMINI_API_KEY**

Rozwiązanie:
```bash
cd backend
echo "GEMINI_API_KEY=twoj_klucz_tutaj" > .env
```

Restart backendu:
```bash
uvicorn main:app --reload
```

## Weryfikacja że wszystko działa

```bash
# Test 1: Backend
curl http://localhost:8000/api/health
# Powinno zwrócić: {"status":"healthy"}

# Test 2: Chat service  
curl http://localhost:8000/api/chat/health
# Powinno zwrócić: {"status":"healthy","service":"chat",...}

# Test 3: Utwórz konwersację
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" -d '{}'
# Powinno zwrócić: {"success":true,"conversation":{...}}
```

Jeśli wszystkie 3 testy przechodzą → backend działa OK.  
Jeśli frontend dalej nie działa → problem w froncie lub CORS.

