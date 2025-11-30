# 💬 Chat Interface Integration - Plan Implementacji

## 📋 Podsumowanie Feature'a

Implementacja multiturn chat interface'u z integracją backend-frontend, który umożliwi użytkownikom interakcję z AI agentem w formie czatu. Komunikaty będą zapisywane lokalnie w folderze `database/` jako pliki JSON, bez użycia bazy danych. System będzie asynchronicznie zapisywał wiadomości podczas przetwarzania i umożliwi przeładowanie frontendu z zachowaniem historii konwersacji.

## 🎯 Główne Cele

1. **Chat Interface na Frontendzie** - Stworzenie nowoczesnego, responsywnego okienka chatowego
2. **Lokalne Przechowywanie** - Zapisywanie konwersacji jako JSONy w folderze `database/`
3. **Backend Integration** - Nowe endpointy API do obsługi wiadomości
4. **Asynchroniczność** - Zapisywanie wiadomości w tle podczas przetwarzania
5. **Persystencja** - Możliwość wczytania historii po przeładowaniu strony

## 🏗️ Architektura Rozwiązania

### Backend (FastAPI)

#### 1. Nowy Model Danych (`models.py`)
```python
class Message(BaseModel):
    id: str
    conversation_id: str
    role: str  # "user" lub "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None

class Conversation(BaseModel):
    id: str
    title: Optional[str]
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    status: str  # "active", "archived"
```

#### 2. Nowy Router (`routers/chat.py`)
Endpointy:
- `POST /api/chat/conversations/` - Stwórz nową konwersację
- `GET /api/chat/conversations/` - Pobierz listę wszystkich konwersacji
- `GET /api/chat/conversations/{conversation_id}` - Pobierz konwersację z historią
- `POST /api/chat/conversations/{conversation_id}/messages` - Wyślij wiadomość do chatu (z przetwarzaniem AI)
- `DELETE /api/chat/conversations/{conversation_id}` - Usuń konwersację
- `GET /api/chat/conversations/{conversation_id}/stream` - WebSocket/SSE endpoint dla streaming responses (opcjonalnie)

#### 3. Storage Manager (`storage_manager.py`)
Moduł do zarządzania plikami JSON:
- Zapis/odczyt konwersacji z folderu `database/conversations/`
- Naming convention: `conversation_{id}.json`
- Obsługa błędów i walidacja
- Atomiczne zapisy (używając temp files)
- Thread-safe operations

#### 4. Chat Service (`chat_service.py`)
Logika biznesowa:
- Integracja z LLM (Gemini/OpenAI)
- Asynchroniczne przetwarzanie wiadomości
- Context management dla konwersacji
- Zapis wiadomości w tle (background tasks)

### Frontend (React)

#### 1. Nowy Komponent `ChatWindow.js`
Funkcjonalności:
- Wyświetlanie wiadomości w stylu czatu
- Input field z auto-focus
- Scrollowanie do najnowszej wiadomości
- Loading states (typing indicator)
- Error handling
- Markdown support dla odpowiedzi AI (opcjonalnie)

#### 2. Nowy Komponent `ConversationsList.js`
Funkcjonalności:
- Lista dostępnych konwersacji
- Tworzenie nowej konwersacji
- Przełączanie między konwersacjami
- Usuwanie konwersacji
- Timestamp i preview ostatniej wiadomości

#### 3. Aktualizacja `App.js`
- Nowy tab "💬 Chat"
- State management dla aktywnej konwersacji
- Routing między konwersacjami

#### 4. API Client (`api/chatApi.js`)
Wszystkie requesty do backend chat endpoints

### Database Structure

```
database/
├── conversations/
│   ├── conversation_abc123.json
│   ├── conversation_def456.json
│   └── ...
└── .gitkeep
```

Format pliku JSON:
```json
{
  "id": "abc123",
  "title": "Pytanie o wizyty",
  "created_at": "2025-11-29T10:00:00Z",
  "updated_at": "2025-11-29T10:05:00Z",
  "status": "active",
  "messages": [
    {
      "id": "msg_001",
      "conversation_id": "abc123",
      "role": "user",
      "content": "Cześć, chciałbym umówić wizytę",
      "timestamp": "2025-11-29T10:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg_002",
      "conversation_id": "abc123",
      "role": "assistant",
      "content": "Oczywiście! Kiedy chciałbyś umówić wizytę?",
      "timestamp": "2025-11-29T10:00:05Z",
      "metadata": {
        "processing_time": 0.5,
        "model": "gemini-pro"
      }
    }
  ]
}
```

## 🔄 Flow Działania

### 1. Użytkownik Tworzy Nową Konwersację
```
Frontend → POST /api/chat/conversations/
Backend → Tworzy nowy JSON file w database/conversations/
Backend → Zwraca conversation_id
Frontend → Przełącza się na nowy chat
```

### 2. Użytkownik Wysyła Wiadomość
```
Frontend → Dodaje wiadomość user do UI (optimistic update)
Frontend → POST /api/chat/conversations/{id}/messages {"content": "..."}
Backend → Zapisuje user message do JSON (asynchronicznie)
Backend → Przetwarza przez LLM
Backend → Zapisuje assistant message do JSON (asynchronicznie)
Backend → Zwraca assistant message
Frontend → Aktualizuje UI z odpowiedzią
```

### 3. Użytkownik Przeładowuje Stronę
```
Frontend → Ładuje się na nowo
Frontend → GET /api/chat/conversations/
Backend → Czyta listę plików z database/conversations/
Backend → Zwraca listę konwersacji (bez pełnej historii)
Frontend → Wyświetla listę konwersacji
Użytkownik wybiera konwersację
Frontend → GET /api/chat/conversations/{id}
Backend → Czyta JSON file
Backend → Zwraca pełną historię
Frontend → Wyświetla chat z historią
```

## ✅ To-Do Lista

### Backend Tasks

- [ ] **Task 1: Setup Storage Structure**
  - [ ] Stwórz folder `database/conversations/` z `.gitkeep`
  - [ ] Dodaj do `.gitignore` pliki `database/conversations/*.json`

- [ ] **Task 2: Implementacja Models**
  - [ ] Dodaj `Message` model do `models.py`
  - [ ] Dodaj `Conversation` model do `models.py`
  - [ ] Dodaj pomocnicze modele: `MessageRequest`, `ConversationResponse`

- [ ] **Task 3: Storage Manager**
  - [ ] Stwórz `backend/storage_manager.py`
  - [ ] Implementuj funkcje:
    - [ ] `save_conversation(conversation: Conversation)`
    - [ ] `load_conversation(conversation_id: str) -> Conversation`
    - [ ] `list_conversations() -> List[ConversationMetadata]`
    - [ ] `delete_conversation(conversation_id: str)`
    - [ ] `add_message_to_conversation(conversation_id: str, message: Message)`
  - [ ] Dodaj error handling i logging
  - [ ] Implementuj thread-safe operations (locks)

- [ ] **Task 4: Chat Service**
  - [ ] Stwórz `backend/chat_service.py`
  - [ ] Implementuj funkcje:
    - [ ] `process_user_message(conversation_id: str, content: str) -> Message`
    - [ ] `generate_ai_response(conversation_history: List[Message]) -> str`
  - [ ] Integracja z `llm_client.py` lub `gemini.py`
  - [ ] Context window management (ostatnie N wiadomości)

- [ ] **Task 5: Chat Router**
  - [ ] Stwórz `backend/routers/chat.py`
  - [ ] Implementuj endpointy:
    - [ ] `POST /api/chat/conversations/`
    - [ ] `GET /api/chat/conversations/`
    - [ ] `GET /api/chat/conversations/{conversation_id}`
    - [ ] `POST /api/chat/conversations/{conversation_id}/messages`
    - [ ] `DELETE /api/chat/conversations/{conversation_id}`
  - [ ] Dodaj background tasks dla asynchronicznych zapisów
  - [ ] Error handling i walidacja
  - [ ] Dodaj logging

- [ ] **Task 6: Integracja w Main**
  - [ ] Dodaj chat router do `main.py`
  - [ ] Zaktualizuj CORS jeśli potrzeba
  - [ ] Przetestuj wszystkie endpointy przez Swagger UI

### Frontend Tasks

- [ ] **Task 7: API Client**
  - [ ] Stwórz `frontend/src/api/chatApi.js`
  - [ ] Implementuj funkcje API:
    - [ ] `createConversation()`
    - [ ] `getConversations()`
    - [ ] `getConversation(id)`
    - [ ] `sendMessage(conversationId, content)`
    - [ ] `deleteConversation(id)`

- [ ] **Task 8: Chat Components - Część 1**
  - [ ] Stwórz `frontend/src/components/ChatWindow.js`
  - [ ] Stwórz `frontend/src/components/ChatWindow.css`
  - [ ] Implementuj UI:
    - [ ] Messages container z scrollowaniem
    - [ ] Message bubbles (user vs assistant styling)
    - [ ] Input field z button
    - [ ] Loading indicator (typing...)
  - [ ] Implementuj logikę:
    - [ ] Wyświetlanie wiadomości
    - [ ] Wysyłanie wiadomości
    - [ ] Auto-scroll do dołu
    - [ ] Loading states

- [ ] **Task 9: Chat Components - Część 2**
  - [ ] Stwórz `frontend/src/components/ConversationsList.js`
  - [ ] Stwórz `frontend/src/components/ConversationsList.css`
  - [ ] Implementuj UI:
    - [ ] Lista konwersacji w sidebar
    - [ ] New conversation button
    - [ ] Delete conversation button
    - [ ] Active conversation highlighting
  - [ ] Implementuj logikę:
    - [ ] Fetch conversations on mount
    - [ ] Switch between conversations
    - [ ] Create new conversation
    - [ ] Delete conversation with confirmation

- [ ] **Task 10: Integracja w App**
  - [ ] Zaktualizuj `App.js`:
    - [ ] Dodaj nowy tab "💬 Chat"
    - [ ] Dodaj state dla conversations
    - [ ] Dodaj state dla activeConversationId
  - [ ] Layout: sidebar + chat window
  - [ ] Obsługa loading states
  - [ ] Error boundaries

- [ ] **Task 11: Styling i UX**
  - [ ] Responsive design (mobile-friendly)
  - [ ] Smooth animations
  - [ ] Dark mode support (opcjonalnie)
  - [ ] Accessibility (ARIA labels, keyboard navigation)
  - [ ] Empty states (brak konwersacji, brak wiadomości)

### Testing & Polish

- [ ] **Task 12: Testing**
  - [ ] Test tworzenia nowej konwersacji
  - [ ] Test wysyłania wiadomości
  - [ ] Test przeładowania strony (persystencja)
  - [ ] Test usuwania konwersacji
  - [ ] Test error scenarios
  - [ ] Test długich konwersacji (scroll, performance)

- [ ] **Task 13: Documentation**
  - [ ] Zaktualizuj README.md z nowym feature
  - [ ] Dodaj komentarze w kodzie
  - [ ] Stwórz przykłady użycia API

- [ ] **Task 14: Cleanup**
  - [ ] Usuń console.logs
  - [ ] Zoptymalizuj imports
  - [ ] Sprawdź linter errors
  - [ ] Code review i refactoring

## 🚀 Kolejność Implementacji

### Faza 1: Backend Foundation (Tasks 1-3)
Podstawowa infrastruktura storage i modele danych

### Faza 2: Backend Logic (Tasks 4-6)
Business logic, routing i integracja z LLM

### Faza 3: Frontend Foundation (Tasks 7-8)
API client i podstawowy chat interface

### Faza 4: Frontend Complete (Tasks 9-10)
Pełna funkcjonalność UI z zarządzaniem konwersacjami

### Faza 5: Polish (Tasks 11-14)
Styling, testing i dokumentacja

## 🎨 UI/UX Considerations

### Layout
- Dwa-kolumnowy layout: sidebar (lista konwersacji) + main area (chat window)
- Mobile: collapsible sidebar lub tabs
- Szerokość: sidebar 300px, chat window flexible

### Styling
- Chat bubbles: user (prawo, niebieski), assistant (lewo, szary)
- Timestamps: subtle, nad wiadomością
- Input: fixed na dole z padding
- Smooth scrolling i fade-in animations

### User Feedback
- Loading states: typing indicator dla AI
- Error messages: toast notifications
- Success feedback: subtle animations
- Optimistic updates: instant UI response

## 🔐 Security & Best Practices

- Walidacja input na backend
- Sanitization HTML/XSS prevention
- Rate limiting dla API calls (opcjonalnie)
- Error messages bez wrażliwych informacji
- Proper error handling (try-catch blocks)
- Logging dla debugging

## 📊 Future Enhancements (Post-MVP)

- [ ] WebSocket dla real-time updates
- [ ] Streaming responses (SSE)
- [ ] Message editing/deletion
- [ ] Conversation search
- [ ] Export konwersacji do PDF/TXT
- [ ] Sharing conversations
- [ ] Voice input
- [ ] File attachments
- [ ] Markdown rendering dla AI responses
- [ ] Code syntax highlighting

## 📝 Notatki Techniczne

### Async Zapisywanie
FastAPI Background Tasks:
```python
@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: MessageRequest,
    background_tasks: BackgroundTasks
):
    # Save user message in background
    background_tasks.add_task(storage.add_message, user_message)
    
    # Process AI response
    ai_response = await chat_service.process(...)
    
    # Save AI message in background
    background_tasks.add_task(storage.add_message, ai_message)
    
    return ai_message
```

### Thread Safety
Użyj `threading.Lock()` w storage_manager.py:
```python
import threading

class StorageManager:
    def __init__(self):
        self._locks = {}  # conversation_id -> Lock
    
    def _get_lock(self, conversation_id):
        if conversation_id not in self._locks:
            self._locks[conversation_id] = threading.Lock()
        return self._locks[conversation_id]
```

### React State Management
Dla prostoty: useState + useEffect
Jeśli skomplikowane: rozważ Context API lub Redux

---

**Czas implementacji:** ~8-12 godzin
**Priorytet:** High
**Dependencies:** llm_client.py / gemini.py dla AI responses


