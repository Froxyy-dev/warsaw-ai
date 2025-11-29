# 🧪 TEST TRANSKRYPTU - INSTRUKCJA

## Cel testu

Sprawdzenie czy:
1. ✅ Połączenie do ElevenLabs API działa
2. ✅ Transkrypt się pobiera
3. ✅ Transkrypt się parsuje poprawnie
4. ✅ Analiza LLM działa

## 🚀 Jak uruchomić

### Krok 1: Upewnij się że backend dependencies są zainstalowane

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Krok 2: Sprawdź `.env` - wymagane zmienne

```bash
ELEVEN_API_KEY=sk_...
ELEVEN_AGENT_ID=...
ELEVEN_AGENT_PHONE_NUMBER=...
GEMINI_API_KEY=...
```

### Krok 3: Uruchom test

```bash
cd backend
python test_single_call.py
```

## 📊 Co zobaczysz

### ✅ Sukces - przykładowy output:

```
================================================================================
TEST POJEDYNCZEGO POŁĄCZENIA - SPRAWDZANIE TRANSKRYPTU
================================================================================

📞 KROK 1: Inicjuję połączenie...
   Miejsce: Test Phone
   Telefon: +48886859039
   Notatki: To jest test. Powiedz 'Test udany' i zakończ rozmowę.

✅ Połączenie zainicjowane!
   Conversation ID: conv_abc123...
   Call SID: CAxxxx...

📞 KROK 2: Czekam na zakończenie rozmowy...
   (Maksymalnie 120 sekund)

   Status: done (30s)

✅ Rozmowa zakończona!
   Status: done

📞 KROK 3: Analiza struktury danych...

================================================================================
DEBUG: ELEVENLABS CONVERSATION DATA STRUCTURE
================================================================================

📋 Top-level keys: ['conversation_id', 'status', 'transcript', 'metadata']

📂 transcript (list): length=4
   First item type: <class 'dict'>
   First item keys: ['role', 'message', 'timestamp']
   Sample: role = agent

================================================================================

📞 KROK 4: Próba wyciągnięcia transkryptu...
================================================================================

============================================================
TRANSKRYPT ROZMOWY
============================================================

🤖 AGENT: Cześć! To jest test.

👤 USER: Test udany.

🤖 AGENT: Świetnie, dziękuję!

============================================================

================================================================================

📊 ANALIZA WYNIKU:

✅ TRANSKRYPT ZOSTAŁ POPRAWNIE SPARSOWANY!
   Długość transkryptu: 234 znaków
   Wypowiedzi agenta: 2
   Wypowiedzi użytkownika: 1

================================================================================
🎉 TEST ZAKOŃCZONY SUKCESEM!
   Transkrypt działa poprawnie
   Możesz teraz testować end-to-end workflow
================================================================================
```

### ❌ Problem - transkrypt pusty:

```
⚠️  TRANSKRYPT PUSTY
   Rozmowa mogła być zbyt krótka lub nie udana
   Status rozmowy: done
   ❌ Klucz 'transcript' NIE ISTNIEJE w danych

❌ TEST NIE POWIÓDŁ SIĘ
   Sprawdź logi powyżej
   Napraw problemy przed testowaniem end-to-end
```

W takim przypadku sprawdź **DEBUG STRUCTURE** - pokaże dokładnie jakie klucze są dostępne.

### ❌ Problem - parsowanie nie działa:

```
❌ PARSOWANIE NIE UDAŁO SIĘ
   Transkrypt nie mógł być sparsowany
   Sprawdź debug structure powyżej
```

To znaczy że:
- Transkrypt ISTNIEJE ale w innym formacie
- Sprawdź DEBUG STRUCTURE
- Skopiuj strukture i prześlij dev (mnie) - dodam support dla tego formatu

## 🔧 Troubleshooting

### Problem: "BŁĄD: Brakujące zmienne środowiskowe"

**Rozwiązanie:**
```bash
# Sprawdź .env
cat .env | grep ELEVEN

# Dodaj brakujące zmienne
echo "ELEVEN_API_KEY=sk_..." >> .env
echo "ELEVEN_AGENT_ID=..." >> .env
echo "ELEVEN_AGENT_PHONE_NUMBER=..." >> .env
```

### Problem: "❌ BŁĄD: Nie udało się zainicjować połączenia"

**Możliwe przyczyny:**
1. Nieprawidłowy `ELEVEN_API_KEY`
2. Nieprawidłowy `ELEVEN_AGENT_ID`
3. Nieprawidłowy `ELEVEN_AGENT_PHONE_NUMBER`
4. Problem z siecią/API ElevenLabs

**Rozwiązanie:**
```bash
# Sprawdź czy API key działa
curl -H "xi-api-key: $ELEVEN_API_KEY" \
  https://api.elevenlabs.io/v1/user

# Powinno zwrócić dane użytkownika
```

### Problem: Timeout po 120s

**Przyczyna:** Rozmowa trwa dłużej niż 120 sekund

**Rozwiązanie:**
Edytuj `test_single_call.py` i zwiększ timeout:
```python
conversation_data = wait_for_conversation_completion(
    conversation_id, 
    max_wait_seconds=180  # Zwiększ do 180s
)
```

### Problem: LLM Analysis fails

**To jest OK dla tego testu!** Test sprawdza tylko pobieranie transkryptu.

Jeśli zobaczysz:
```
⚠️  LLM error: ...
⚠️  LLM unavailable, using fallback heuristics
```

To normalne - ten test nie testuje LLM, tylko transkrypt.

## 📝 Co dalej po udanym teście?

1. ✅ Test zakończony sukcesem → **możesz testować end-to-end workflow**
2. ❌ Test nie działa → **najpierw napraw transkrypt, potem end-to-end**

### Uruchom end-to-end:

```bash
# Terminal 1: Backend
cd backend
make run

# Terminal 2: Frontend
cd frontend
npm start

# Przeglądarka: http://localhost:3000
```

## 🐛 Debug verbose mode

Jeśli chcesz więcej informacji, możesz edytować `test_single_call.py`:

```python
# Na początku pliku dodaj:
import logging
logging.basicConfig(level=logging.DEBUG)
```

To pokaże wszystkie requesty HTTP i więcej detali.

## 📞 Kontakt

Jeśli test nie działa i nie wiesz dlaczego:
1. Skopiuj **cały output** z terminala
2. Szczególnie **DEBUG STRUCTURE section**
3. Prześlij developerowi - dodam support dla tego formatu

