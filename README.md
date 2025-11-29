# 🤖 AI Call Agent

Agent AI do automatycznych rozmów telefonicznych i umawiania wizyt.

## 🚀 Szybki Start

### Wymagania
- Python 3.8+
- Node.js 16+
- npm lub yarn

### Instalacja

1. **Sklonuj repozytorium i zainstaluj zależności:**
```bash
make setup
```

2. **Uruchom aplikację:**

W dwóch osobnych terminalach:
```bash
# Terminal 1 - Backend
make run-backend

# Terminal 2 - Frontend
make run-frontend
```

Lub w jednym terminalu:
```bash
make run-all
```

3. **Otwórz aplikację w przeglądarce:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Struktura Projektu

```
warsaw-ai/
├── backend/                # FastAPI Backend
│   ├── main.py            # Główna aplikacja FastAPI
│   ├── models.py          # Modele danych (Pydantic)
│   ├── routers/           # Endpointy API
│   │   ├── calls.py       # Zarządzanie połączeniami
│   │   └── appointments.py # Zarządzanie wizytami
│   └── requirements.txt   # Zależności Python
│
├── frontend/              # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # Komponenty React
│   │   │   ├── CallForm.js        # Formularz nowego połączenia
│   │   │   ├── CallsList.js       # Lista połączeń
│   │   │   └── AppointmentsList.js # Lista wizyt
│   │   ├── api/
│   │   │   └── axios.js   # Konfiguracja API
│   │   ├── App.js         # Główny komponent
│   │   └── index.js       # Entry point
│   └── package.json
│
├── Makefile              # Komendy do zarządzania projektem
└── README.md            # Ten plik
```

## 🎯 Funkcjonalności

### Aktualnie dostępne:
- ✅ Tworzenie nowych połączeń AI
- ✅ Przegląd historii połączeń
- ✅ Zarządzanie wizytami
- ✅ REST API z dokumentacją (FastAPI)
- ✅ Nowoczesny interfejs użytkownika (React)
- ✅ **Chat AI z integracją Gemini** - Multiturn konwersacje z AI agentem
- ✅ **Persystencja konwersacji** - Lokalne przechowywanie w JSON
- ✅ **🎉 Party Planner** - Inteligentne planowanie imprez z iteracyjnym refinementem
  - Automatyczne wykrywanie party requests
  - Generowanie szczegółowych planów
  - Modyfikacja planów na podstawie feedbacku
  - Zbieranie danych kontaktowych
  - State persistence między sesjami

### Do implementacji:
- 🔄 Integracja z Twilio (dla prawdziwych połączeń)
- 🔄 Baza danych (PostgreSQL/MongoDB) - obecnie używamy JSON storage
- 🔄 Automatyczne transkrypcje rozmów
- 🔄 System powiadomień
- 🔄 Kalendarz i synchronizacja wizyt
- 🔄 WebSocket dla real-time chat updates
- 🔄 Streaming AI responses

## 🔧 API Endpointy

### Calls (Połączenia)
- `POST /api/calls/` - Utwórz nowe połączenie
- `GET /api/calls/` - Pobierz wszystkie połączenia
- `GET /api/calls/{call_id}` - Pobierz szczegóły połączenia
- `PATCH /api/calls/{call_id}/status` - Zaktualizuj status połączenia
- `DELETE /api/calls/{call_id}` - Usuń połączenie

### Appointments (Wizyty)
- `POST /api/appointments/` - Utwórz nową wizytę
- `GET /api/appointments/` - Pobierz wszystkie wizyty
- `GET /api/appointments/{appointment_id}` - Pobierz szczegóły wizyty
- `PATCH /api/appointments/{appointment_id}/status` - Zaktualizuj status wizyty
- `DELETE /api/appointments/{appointment_id}` - Usuń wizytę

### Chat (Konwersacje AI)
- `POST /api/chat/conversations/` - Utwórz nową konwersację
- `GET /api/chat/conversations/` - Pobierz listę konwersacji
- `GET /api/chat/conversations/{conversation_id}` - Pobierz konwersację z historią
- `POST /api/chat/conversations/{conversation_id}/messages` - Wyślij wiadomość
- `DELETE /api/chat/conversations/{conversation_id}` - Usuń konwersację
- `GET /api/chat/conversations/{conversation_id}/messages` - Pobierz wiadomości (z paginacją)

## 🔑 Konfiguracja (TODO)

Stwórz plik `.env` w katalogu `backend/`:

```env
# OpenAI API Key (dla AI konwersacji)
OPENAI_API_KEY=your_openai_api_key_here

# Twilio credentials (dla prawdziwych połączeń)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## 🛠️ Komendy Makefile

```bash
make help          # Pokaż wszystkie dostępne komendy
make setup         # Zainstaluj wszystkie zależności
make run-backend   # Uruchom backend
make run-frontend  # Uruchom frontend
make run-all       # Uruchom obie aplikacje
make clean         # Wyczyść instalacje
```

## 🧪 Testowanie API

Możesz przetestować API używając:
1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **curl** lub **Postman**

Przykład curl:
```bash
curl -X POST "http://localhost:8000/api/calls/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+48123456789",
    "customer_name": "Jan Kowalski",
    "purpose": "schedule_appointment",
    "preferred_date": "2025-12-01"
  }'
```

## 🚧 Następne Kroki

1. **Integracja z AI:**
   - Dodaj OpenAI GPT dla naturalnych konwersacji
   - Implementuj rozpoznawanie intencji użytkownika

2. **Integracja z Twilio:**
   - Połączenia głosowe
   - SMS powiadomienia
   - Transkrypcje rozmów

3. **Baza danych:**
   - Przejście z in-memory do PostgreSQL/MongoDB
   - Migracje bazy danych

4. **Autoryzacja:**
   - System logowania
   - JWT tokens
   - Role użytkowników

5. **UI/UX:**
   - Panel administracyjny
   - Kalendarz wizyt
   - Statystyki i raporty

## 📝 Licencja

MIT

## 👨‍💻 Rozwój

To jest szkielet projektu gotowy do dalszego rozwoju. Możesz:
- Dodawać nowe endpointy w `backend/routers/`
- Tworzyć nowe komponenty w `frontend/src/components/`
- Rozszerzać modele danych w `backend/models.py`

Happy coding! 🚀

