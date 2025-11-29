# Analiza błędu 500 Internal Server Error

## 🔴 Problem

Frontend dostaje **500 Internal Server Error** podczas wysyłania wiadomości:

```
POST http://localhost:3001/api/chat/conversations/{id}/messages
Status: 500 Internal Server Error
Response: "Internal Server Error" (HTML, nie JSON!)
Error: XML Parsing Error: syntax error
```

## 🔍 Objawy

1. **Auto-refresh DZIAŁA** - widać "Auto-refresh #14" w logach
2. **GET requests działają** - odczytywanie konwersacji działa
3. **POST request failuje** - wysyłanie wiadomości crashuje backend
4. **Backend zwraca HTML zamiast JSON** - "XML Parsing Error" oznacza że axios dostał HTML error page

## ✅ Co DZIAŁA

Test backendu bezpośrednio (port 8000) pokazuje że:
- ✅ Tworzenie konwersacji: OK
- ✅ Wysyłanie wiadomości: OK  
- ✅ Generowanie odpowiedzi AI: OK
- ✅ Zapisywanie do pliku: OK

**Backend SAM W SOBIE działa poprawnie!**

## ❌ Co NIE DZIAŁA

Problem jest w **komunikacji Frontend → Next.js Proxy → Backend**:

```
Frontend (3001) → Next.js Proxy → Backend (8000)
                      ↓
                   500 ERROR
```

## 🎯 Prawdopodobne Przyczyny

### 1. **Race Condition w Backend Storage**

Podczas gdy backend przetwarza jedną wiadomość (LLM call, venue search, voice agent), 
frontend wysyła auto-refresh requesty co 2 sekundy.

```
Timeline:
T+0s:  Frontend: POST /messages (wysyła "test")
T+0s:  Backend:  Zaczyna przetwarzać (chat_service.py)
T+2s:  Frontend: GET /conversations/{id} (auto-refresh #1)
T+2s:  Backend:  ❌ CRASH - próbuje czytać plik podczas gdy inny wątek zapisuje
T+4s:  Frontend: GET /conversations/{id} (auto-refresh #2)  
T+4s:  Backend:  ❌ CRASH - backend już nie odpowiada
```

**Kod problematyczny:**

`backend/routers/chat.py` linia ~114-129:
```python
# Process message and generate AI response
_, assistant_message = await chat_service.process_user_message(
    conversation_id,
    message_request.content
)

# Save assistant message
storage_manager.add_message_to_conversation(
    conversation_id,
    assistant_message
)
```

`backend/storage_manager.py` - brak lockowania podczas I/O:
- Wątek 1: Pisze do pliku (POST /messages)
- Wątek 2: Czyta z pliku (GET /conversations/{id}) - auto-refresh
- ❌ File lock conflict!

### 2. **Backend Crashuje ale Uvicorn Nie Pokazuje Traceback**

Możliwe że:
- Exception jest łapany gdzieś wyżej i zwracany jako 500 bez logu
- Uvicorn w trybie reload nie pokazuje wszystkich errorów
- Problem jest w async code i exception ginie

### 3. **Next.js Proxy Timeout**

Next.js proxy może mieć timeout na długie requesty (LLM może trwać 10-30s).

## 🔧 Rozwiązania

### Rozwiązanie 1: Dodaj File Locking (NAJLEPSZE)

```python
# backend/storage_manager.py

import fcntl  # POSIX file locking

def save_conversation(self, conversation: Conversation) -> bool:
    lock = self._get_lock(conversation.id)
    file_path = self._get_file_path(conversation.id)
    
    try:
        with lock:
            # Otwórz plik z lockiem
            with open(file_path, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                json.dump(conversation.model_dump(mode='json'), f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock
        return True
    except Exception as e:
        logger.error(f"Failed to save: {e}")
        return False
```

### Rozwiązanie 2: Wyłącz Auto-Refresh Podczas POST

```typescript
// frontend/src/components/ChatWindow.tsx

const handleSendMessage = async (e: React.FormEvent) => {
    // ...
    
    // Wyłącz auto-refresh PRZED wysłaniem
    setIsSearching(false);
    
    try {
        await sendMessageApi(convId, messageContent);
        
        // Poczekaj trochę przed włączeniem auto-refresh
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Teraz włącz auto-refresh
        setIsSearching(true);
    } catch (err) {
        // ...
    }
};
```

### Rozwiązanie 3: Lepsze Error Handling w Backend

```python
# backend/routers/chat.py

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def send_message(conversation_id: str, message_request: MessageRequest):
    try:
        # ... existing code ...
    except Exception as e:
        logger.error(f"CRITICAL ERROR in send_message: {e}", exc_info=True)
        # Zwróć szczegóły błędu dla debugowania
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "type": type(e).__name__}
        )
```

### Rozwiązanie 4: Zwiększ Timeout Next.js Proxy

```javascript
// frontend/next.config.js

const nextConfig = {
  async rewrites() {
    return [{
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    }];
  },
  // Zwiększ timeout dla długich requestów
  serverRuntimeConfig: {
    timeout: 300000  // 5 minut
  }
};
```

### Rozwiązanie 5: Użyj Queue dla Długich Zadań (PRODUKCYJNE)

Zamiast czekać na LLM w request:

```
1. Frontend: POST /messages → Backend: Zwraca 202 Accepted (natychmiast)
2. Backend: Przetwarza w tle (worker/queue)
3. Frontend: Auto-refresh sprawdza czy już gotowe
```

## 🎯 Rekomendacja: Co Zrobić TERAZ

**Dla POC (quickest fix):**

1. **Dodaj więcej logów w backend:**
```bash
cd backend
# Edytuj chat.py, dodaj try-except z logowaniem
```

2. **Uruchom backend w verbose mode:**
```bash
uvicorn main:app --reload --log-level debug
```

3. **Sprawdź logi podczas wysyłania wiadomości** - powinny pojawić się czerwone tracebacki

4. **Wyłącz auto-refresh podczas POST** (tymczasowo):
```typescript
// W ChatWindow.tsx - ustaw dłuższy interval
}, 5000); // 5 sekund zamiast 2
```

## 📊 Debug Checklist

Gdy wyślesz wiadomość, sprawdź:

- [ ] Terminal z backendem (uvicorn) - czy są czerwone errory?
- [ ] Terminal z frontendem (npm run dev) - czy są errory?
- [ ] DevTools → Network → kliknij failed request → Preview - co dokładnie jest w response?
- [ ] Sprawdź plik JSON konwersacji - czy jest uszkodzony?

## 🔬 Test Izolowany

Zrób to aby potwierdzić teorię:

```bash
# Terminal 1: Wyślij wiadomość (będzie trwać 5-10s)
curl -X POST http://localhost:8000/api/chat/conversations/{ID}/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"test"}' &

# Terminal 2: Podczas gdy backend przetwarza, spróbuj odczytać
sleep 2
curl http://localhost:8000/api/chat/conversations/{ID}

# Czy dostaniesz 500?
```

Jeśli TAK → to race condition w storage!
Jeśli NIE → problem jest gdzie indziej.

## 📝 Next Steps

1. Przeczytaj ten dokument
2. Zbierz logi z backendu (terminal gdzie uvicorn)
3. Zastosuj Rozwiązanie 2 (wyłącz auto-refresh podczas POST)
4. Jeśli problem persist → zastosuj Rozwiązanie 1 (file locking)

---

**Data analizy:** 29.11.2025  
**Status:** Backend działa, problem w race condition podczas concurrent requests  
**Priorytet:** HIGH - blokuje podstawową funkcjonalność

