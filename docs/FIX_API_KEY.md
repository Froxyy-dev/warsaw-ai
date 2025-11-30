# 🔑 Fix: Gemini API Key Issues

## Problem: 429 RESOURCE_EXHAUSTED

Ten błąd oznacza że:
1. Wyczerpałeś limit free tier dla tego modelu
2. API key jest nieprawidłowy
3. Musisz poczekać aż quota się zresetuje

## ✅ Rozwiązanie

### Krok 1: Test API Key

```bash
cd /home/mwiniarek/warsaw-ai
python3 test_gemini.py
```

To sprawdzi które modele działają z Twoim API key.

### Krok 2: Opcja A - Zmień Model (ZROBIONE)

Zmieniłem już domyślny model z `gemini-2.0-flash-exp` na `gemini-1.5-flash` który ma:
- ✅ Wyższy limit free tier
- ✅ Stabilniejszy
- ✅ Lepsze quota

**Restart backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### Krok 3: Opcja B - Nowy API Key

Jeśli nadal nie działa, wygeneruj nowy API key:

1. Idź do: https://aistudio.google.com/apikey
2. Kliknij "Create API Key"
3. Skopiuj nowy klucz
4. Zaktualizuj `backend/.env`:
   ```bash
   GEMINI_API_KEY=twoj_nowy_klucz_tutaj
   ```
5. Restart backend

### Krok 4: Opcja C - Poczekaj

Free tier ma limity:
- **Per minute**: 15 requests
- **Per day**: 1500 requests

Jeśli przekroczyłeś limit, poczekaj:
- 1 minutę (dla per-minute limit)
- Do północy (dla daily limit)

## 📊 Sprawdzenie Użycia

Zobacz swoje usage tutaj:
https://ai.dev/usage?tab=rate-limit

## 🔍 Debug Commands

### Sprawdź czy .env istnieje:
```bash
ls -la backend/.env
```

### Sprawdź zawartość (bez pokazywania klucza):
```bash
cat backend/.env | grep GEMINI_API_KEY | head -c 30
```

### Test simple request:
```bash
python3 test_gemini.py
```

## ⚡ Quick Fix

Jeśli wszystko inne zawodzi:

```bash
# 1. Wygeneruj nowy API key
# https://aistudio.google.com/apikey

# 2. Podmień w .env
echo "GEMINI_API_KEY=nowy_klucz" > backend/.env

# 3. Restart backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

## 💡 Wskazówki

### Free Tier Limits:
- **gemini-1.5-flash**: 15 RPM, 1M TPM, 1500 RPD
- **gemini-1.5-pro**: 2 RPM, 32K TPM, 50 RPD
- **gemini-2.0-flash-exp**: Eksperymentalny, niższe limity

### Best Practices:
- Używaj `gemini-1.5-flash` dla development
- Dodaj rate limiting w kodzie
- Cache responses gdzie to możliwe
- Monitor usage na https://ai.dev/usage

## 🆘 Jeśli Nic Nie Działa

1. **Sprawdź quota**: https://ai.dev/usage?tab=rate-limit
2. **Nowy projekt**: Stwórz nowy projekt w Google AI Studio
3. **Nowy klucz**: Wygeneruj klucz z nowego projektu
4. **Upgrade**: Rozważ płatny tier jeśli potrzebujesz więcej

