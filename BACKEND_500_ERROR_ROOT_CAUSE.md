# Analiza: Dlaczego Backend Zwraca 500 i Nie Przyjmuje Wiadomości?

## 🔴 Objawy

### Timeline z Logów Frontendu:
```
21:04:17.907 📤 Sending message to backend: 886859039
21:04:17.907 🔄 Starting auto-refresh...
21:04:22.919 🔄 Auto-refresh #1
21:04:27.919 🔄 Auto-refresh #2
21:04:32.920 🔄 Auto-refresh #3
21:04:37.920 🔄 Auto-refresh #4
21:04:42.920 🔄 Auto-refresh #5
21:04:47.920 🔄 Auto-refresh #6
21:04:47.926 ❌ Failed to send message: 500 Internal Server Error
```

### Kluczowe Obserwacje:
1. **POST /messages trwa ~30 sekund** (21:04:17 → 21:04:47)
2. **Podczas tych 30 sekund**: auto-refresh co 5s próbuje GET /conversations/{id}
3. **Po 30 sekundach**: POST zwraca 500 error
4. **Response**: "Internal Server Error" (HTML, nie JSON!)
5. **Wszystkie późniejsze GET też failują** z 500

## 🎯 Diagnoza

### Problem #1: Backend Nie Odpowiada na Port 8000

Wcześniejsze testy pokazały:
```bash
$ curl http://localhost:8000/
Connection refused
```

**Backend nie działa!** Albo:
- Się wyłączył (crash)
- Nie uruchomił się po zmianach
- Ma błąd podczas startu

### Problem #2: Zawiesza się na `sendMessageApi()`

Frontend:
```typescript
// ChatWindow.tsx line ~166
await sendMessageApi(convId, messageContent);  // ← TUTAJ SIĘ ZAWIESZA
```

To wywołanie:
```typescript
// chatApi.ts
export const sendMessage = async (conversationId, content) => {
  const response = await api.post(
    `/chat/conversations/${conversationId}/messages`,
    { content }
  );
  return response.data;
};
```

**Axios czeka 30 sekund** na odpowiedź, potem dostaje 500.

### Problem #3: Backend Prawdopodobnie Crashuje PODCZAS Przetwarzania

Możliwe scenariusze:

#### Scenariusz A: Backend Crashuje na Start (Syntax Error)
```
Nasze zmiany w chat.py lub storage_manager.py
    ↓
Backend próbuje się zrestartować
    ↓
Python syntax error / import error
    ↓
Uvicorn nie może uruchomić aplikacji
    ↓
Connection refused
```

**Sprawdź:** Terminal gdzie `make run-backend` - powinien być czerwony traceback!

#### Scenariusz B: Backend Crashuje PODCZAS Requestu
```
Frontend: POST /messages
    ↓
Backend: Przyjmuje request
    ↓
Backend: Próbuje process_user_message()
    ↓
❌ Exception w chat_service.py / party_planner.py
    ↓
Backend: Zwraca 500 (ale uvicorn dalej działa)
```

**Sprawdź:** Terminal backendu - logi `📥 Received message...` i potem błąd

#### Scenariusz C: Backend "Zawiesi się" na Długiej Operacji
```
Frontend: POST /messages
    ↓
Backend: process_user_message() - wywołuje LLM
    ↓
LLM Request timeout / API error
    ↓
Backend "wisi" 30+ sekund
    ↓
Timeout i zwraca 500
```

## 🔍 Jak Zdiagnozować DOKŁADNIE?

### Krok 1: Sprawdź czy Backend w Ogóle Działa
```bash
ps aux | grep uvicorn
# Jeśli nic nie pokazuje → backend NIE działa!
```

### Krok 2: Sprawdź Logi Startu Backendu

Terminal gdzie `make run-backend` powinien pokazać:
```
INFO: Started server process [XXX]
INFO: Application startup complete.
```

**Jeśli NIE MA tego** → backend się nie uruchomił! Będzie traceback Pythona.

### Krok 3: Sprawdź Logi Request

Jeśli backend działa, przy wysłaniu wiadomości powinny być logi:
```
📥 Received message request for conversation XXX
🔍 Checking if conversation XXX exists...
✅ Conversation exists
💾 Creating user message...
💾 Saving user message to storage...
✅ User message saved
🤖 Starting AI processing...
```

**Gdzie to się przerywa?** Tam jest błąd!

### Krok 4: Test Bezpośrednio Backendu

```bash
# Test czy backend odpowiada
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/api/chat/health

# Jeśli oba failują → backend nie działa
```

## 🎯 Możliwe Przyczyny (Ranked)

### 1. **Backend się nie uruchomił po zmianach** (90% pewności)

**Przyczyna:** Moje zmiany w `chat.py` lub `storage_manager.py` mają błąd składniowy lub import error.

**Sprawdź:**
```bash
cd backend
python3 -c "import routers.chat"
# Jeśli error → to jest problem!
```

**Objawy:**
- `ps aux | grep uvicorn` → nic nie pokazuje
- `curl http://localhost:8000/` → Connection refused
- Terminal backendu → czerwony traceback Pythona

**Fix:** Cofnij ostatnie zmiany lub napraw błąd importu.

### 2. **Backend Crashuje na `process_user_message()`** (60% pewności)

**Przyczyna:** Błąd w `chat_service.py` podczas:
- Tworzenia duplicate user message (zapisaliśmy raz w chat.py, drugi raz w chat_service.py?)
- Przetwarzania przez party_planner
- Wywołania LLM

**Objawy:**
- Backend się uruchamia OK
- Logi pokazują: "📥 Received..." → "🤖 Starting AI processing..." → ❌ CRASH
- 500 error dopiero po 30s

**Fix:** Dodaj try-except w `process_user_message()` z logowaniem.

### 3. **Duplicate Message Creation** (80% pewności) ⭐ NAJPRAWDOPODOBNIEJSZE

**Przyczyna:** W `chat.py` teraz:
```python
# Linia ~113: Tworzymy user_message i zapisujemy
user_message = Message(...)
storage_manager.add_message_to_conversation(conversation_id, user_message)

# Linia ~126: Wywołujemy chat_service
_, assistant_message = await chat_service.process_user_message(
    conversation_id,
    message_request.content  # ← Przekazujemy content, NIE message!
)
```

W `chat_service.py`:
```python
async def process_user_message(self, conversation_id, content):
    # chat_service prawdopodobnie ZNOWU tworzy user_message!
    # I próbuje go zapisać!
    # → Conflict lub duplicate!
```

**Problem:** 
- chat.py: Tworzy user_message → zapisuje
- chat_service.py: ZNOWU tworzy user_message → próbuje zapisać
- ❌ Duplicate ID? ❌ Race condition? ❌ Validation error?

### 4. **Timeout w LLM Call** (30% pewności)

LLM może nie odpowiadać i request wisi.

## 🔧 Jak To Naprawić?

### Fix #1: Najpierw Sprawdź Czy Backend Działa

```bash
# Terminal 1
ps aux | grep uvicorn

# Jeśli nie ma procesu:
cd backend
make run-backend

# Sprawdź czy są błędy w terminalu!
```

### Fix #2: Usuń Duplicate Message Creation

**Problem:** `chat.py` tworzy user_message, ale `chat_service.py` prawdopodobnie też!

**Rozwiązanie A:** Przekaż już utworzony message do chat_service:
```python
# chat.py
user_message = Message(...)
storage_manager.add_message_to_conversation(conversation_id, user_message)

# Przekaż message, nie content!
assistant_message = await chat_service.process_user_message(
    conversation_id,
    user_message  # ← Cały message!
)
```

**Rozwiązanie B:** Usuń tworzenie message z chat.py, zostaw tylko w chat_service:
```python
# chat.py
# Wywołaj chat_service - on stworzy i zapisze WSZYSTKO
user_message, assistant_message = await chat_service.process_user_message(
    conversation_id,
    message_request.content
)
# Nie zapisuj nic tutaj - chat_service to już zrobił
```

### Fix #3: Dodaj Error Handling

```python
# chat.py
try:
    _, assistant_message = await chat_service.process_user_message(...)
except Exception as e:
    logger.error(f"❌ CRASH: {e}", exc_info=True)
    # Zapisz error message dla użytkownika
    error_msg = Message(...)
    storage_manager.add_message_to_conversation(conversation_id, error_msg)
    raise HTTPException(status_code=500, detail=str(e))
```

## 📊 Podsumowanie

### Co Wiemy NA PEWNO:
1. ✅ Frontend wysyła request poprawnie
2. ✅ Next.js proxy przekazuje do backendu
3. ❌ **Backend zwraca 500 po ~30 sekundach**
4. ❌ Response to HTML "Internal Server Error" zamiast JSON
5. ❌ Późniejsze requesty też failują

### Co Musimy Sprawdzić:
1. **Czy uvicorn działa?** → `ps aux | grep uvicorn`
2. **Czy backend się uruchomił?** → Terminal backendu - logi
3. **Gdzie crashuje?** → Logi z emoji 📥 🔍 💾 🤖
4. **Co jest w response?** → DevTools → Network → kliknij failed request → Response tab

### Najbardziej Prawdopodobna Przyczyna:
**Duplicate message creation** - chat.py i chat_service.py tworzą user_message 2 razy!

## 🚀 Action Items

1. **NIE róbmy żadnych zmian** (jak chciałeś)
2. **Sprawdź terminal backendu** - skopiuj logi
3. **Sprawdź czy uvicorn działa**: `ps aux | grep uvicorn`
4. **Jak backend działa** - wyślij wiadomość i pokaż logi z terminala backendu (tam gdzie emoji)

## 🎯 PROBLEM ZNALEZIONY! (UPDATE 21:08)

### ✅ Root Cause: Blocking Sync Call w Async Context

**User zgłosił:** Backend psuje się podczas przejścia do fazy venue search (po zebraniu danych użytkownika).

### 🔍 Co się dzieje krok po kroku:

```
1. Użytkownik wysyła ostatnią informację: "886859039" (telefon)
   ↓
2. information_gatherer.py → zwraca {"type": "complete"}
   ↓
3. party_planner.py → zmienia state na SEARCHING
   ↓
4. chat_service.py (linia 244) → wykrywa zmianę state
   ↓
5. chat_service.py (linia 249) → wywołuje party_planner.search_venues_only()
   ↓
6. party_planner.py (linia 340) → wywołuje venue_searcher.search_venues()
   ↓
7. venue_searcher.py (linia 79) → wywołuje llm_client.send(prompt)  ⚠️ TUTAJ!
   ↓
8. llm_client.send() to SYNC (nie async) call do Gemini API + Google Search
   ↓
9. ❌ BLOKUJE cały FastAPI event loop na 20-30 sekund!
   ↓
10. Frontend auto-refresh próbuje GET /conversations/{id} co 5s
    ↓
11. Backend nie może odpowiedzieć bo wisi na llm_client.send()
    ↓
12. Po 30s: timeout lub Gemini error → 500 Internal Server Error
```

### 🐛 Kod Źródłowy Problemu:

**venue_searcher.py:52-79**
```python
def search_venues(self, location: str, ...) -> VenueSearchResult:
    # ⚠️ To jest SYNC metoda (nie async)
    try:
        logger.info(f"Searching for {count} venues...")
        prompt = self.VENUE_SEARCH_PROMPT.format(...)
        
        # ⚠️ BLOCKING CALL - wisi 20-30 sekund!
        response = self.llm_client.send(prompt)  # ← TUTAJ SIĘ BLOKUJE
        
        venues = self._parse_search_results(response, ...)
        return VenueSearchResult(venues=venues[:count], ...)
    except Exception as e:
        logger.error(f"Failed to search venues: {e}")
        return VenueSearchResult(venues=[], ...)
```

**party_planner.py:330-344**
```python
async def search_venues_only(self) -> str:
    # To jest async metoda...
    location = self.gathered_info.get("location", "Warszawa")
    
    # ⚠️ Ale wywołuje SYNC venue_searcher.search_venues()
    venue_results = self.venue_searcher.search_venues(
        location=location,
        query_type="lokale z salami/restauracje",
        count=3
    )  # ← Brakuje 'await' i search_venues nie jest async!
```

### ❌ Dlaczego to powoduje 500 Error:

1. **Blocking I/O w Event Loop:**
   - `llm_client.send()` to sync call do zewnętrznego API (Gemini)
   - Trwa 20-30 sekund
   - **Blokuje cały FastAPI event loop** - żaden inny request nie może być obsłużony!

2. **Auto-refresh Colliduje:**
   - Frontend co 5s robi GET /conversations/{id}
   - Backend nie może odpowiedzieć bo jest zablokowany
   - Request timeout → 500 error

3. **LLM może też timeoutować:**
   - Jeśli Gemini API nie odpowiada w określonym czasie
   - `llm_client.send()` może rzucić exception
   - Exception propaguje do góry → 500 error

### 📊 Evidence z Logów:

```
21:04:17.907 📤 Sending message: 886859039     ← User wysyła ostatnią info
21:04:22.919 🔄 Auto-refresh #1               ← +5s - próba odczytu
21:04:27.919 🔄 Auto-refresh #2               ← +10s
21:04:32.920 🔄 Auto-refresh #3               ← +15s
21:04:37.920 🔄 Auto-refresh #4               ← +20s
21:04:42.920 🔄 Auto-refresh #5               ← +25s
21:04:47.920 🔄 Auto-refresh #6               ← +30s
21:04:47.926 ❌ Failed: 500 Internal Server Error  ← CRASH po 30s!
```

**Dokładnie 30 sekund** - typowy HTTP timeout lub Gemini API timeout.

---

## 🔧 Jak To Naprawić? (Propozycje)

### Fix #1: Zmień venue_searcher na Async (Recommended)

**venue_searcher.py:**
```python
async def search_venues(self, location: str, ...) -> VenueSearchResult:
    try:
        logger.info(f"Searching for {count} venues...")
        prompt = self.VENUE_SEARCH_PROMPT.format(...)
        
        # ✅ Async call - nie blokuje event loop!
        response = await self.llm_client.send_async(prompt)
        
        venues = self._parse_search_results(response, ...)
        return VenueSearchResult(venues=venues[:count], ...)
    except Exception as e:
        logger.error(f"Failed to search venues: {e}", exc_info=True)
        return VenueSearchResult(venues=[], ...)
```

**party_planner.py:**
```python
async def search_venues_only(self) -> str:
    location = self.gathered_info.get("location", "Warszawa")
    
    # ✅ Teraz z await!
    venue_results = await self.venue_searcher.search_venues(
        location=location,
        query_type="lokale z salami/restauracje",
        count=3
    )
```

**Wymaga:** Zaimplementować `llm_client.send_async()` albo zrobić istniejący `send()` async.

### Fix #2: Use run_in_executor (Alternatywa)

Jeśli nie możesz zmienić `llm_client.send()` na async:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def search_venues_only(self) -> str:
    location = self.gathered_info.get("location", "Warszawa")
    
    # ✅ Uruchom sync call w osobnym wątku
    loop = asyncio.get_event_loop()
    venue_results = await loop.run_in_executor(
        None,  # Uses default ThreadPoolExecutor
        self.venue_searcher.search_venues,
        location,
        "lokale z salami/restauracje",
        3
    )
```

### Fix #3: Increase Timeout + Better Error Handling

Jeśli async nie jest opcją, przynajmniej zwiększ timeout i popraw error handling:

**venue_searcher.py:**
```python
def search_venues(self, location: str, ...) -> VenueSearchResult:
    try:
        logger.info(f"🔍 Starting venue search in {location}...")
        prompt = self.VENUE_SEARCH_PROMPT.format(...)
        
        # Zwiększ timeout w LLMClient
        response = self.llm_client.send(prompt, timeout=60)  # 60s zamiast 30s
        
        logger.info(f"✅ LLM responded, parsing results...")
        venues = self._parse_search_results(response, ...)
        logger.info(f"✅ Found {len(venues)} venues")
        
        return VenueSearchResult(venues=venues[:count], ...)
        
    except TimeoutError as e:
        logger.error(f"❌ LLM timeout during venue search: {e}")
        return VenueSearchResult(venues=[], ...)
    except Exception as e:
        logger.error(f"❌ Venue search failed: {e}", exc_info=True)
        return VenueSearchResult(venues=[], ...)
```

### Fix #4: Save Progress Messages BEFORE Long Operations

**chat_service.py:**
```python
if state_before == PlanState.GATHERING and self.party_planner.state == PlanState.SEARCHING:
    logger.info("🔍 Gathering complete, executing search...")
    
    # ✅ Najpierw zapisz "starting" message
    starting_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content="🔍 Zaczynam wyszukiwanie lokali...",
        timestamp=datetime.now()
    )
    storage_manager.add_message_to_conversation(conversation_id, starting_msg)
    logger.info("✅ Starting message saved - frontend can see it now")
    
    # Teraz długa operacja
    logger.info("🏢 Step 1: Searching venues...")
    venue_response = await self.party_planner.search_venues_only()
    # ...
```

To da userowi natychmiastowy feedback że coś się dzieje.

---

## 🎯 Rekomendacja

**Najlepsze rozwiązanie:** Fix #1 + Fix #4
1. Zmień `venue_searcher.search_venues()` i `search_bakeries()` na async
2. Zmień `llm_client.send()` na async (lub dodaj `send_async()`)
3. Dodaj progress messages PRZED długimi operacjami
4. Popraw error handling z try-except i logowaniem

**Quick win (tymczasowy):** Fix #4
- Zapisz "Zaczynam wyszukiwanie..." PRZED wywołaniem venue_searcher
- User zobaczy że coś się dzieje (auto-refresh zadziała)
- Potem napraw async problem

---

## 🤔 Pytanie do Ciebie

**Co dalej?**
1. Chcesz żebym naprawił to teraz? (async + progress messages)
2. Wolisz najpierw zobaczyć logi z backendu żeby potwierdzić diagnozę?
3. Chcesz tylko quick win (progress messages) na razie?

---

**Data:** 29.11.2025 21:08  
**Status:** ✅ Root cause zidentyfikowany - blocking sync call w venue_searcher  
**Problem:** `llm_client.send()` blokuje event loop na 30s podczas venue search  
**Fix:** Zmienić venue_searcher + llm_client na async

