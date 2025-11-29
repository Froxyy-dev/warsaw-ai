# 🎉 Party Planner - Instrukcja Użytkowania

## ✅ Feature Zaimplementowany!

Party Planner został w pełni zaimplementowany i jest gotowy do użycia przez chat interface.

## 🚀 Jak Używać

### 1. Uruchom Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

### 2. Uruchom Frontend

```bash
cd frontend
npm start
```

### 3. Otwórz Chat

Otwórz http://localhost:3000 w przeglądarce.

## 💬 Przykładowy Flow

### Krok 1: Rozpocznij Planning

W chacie napisz coś typu:
```
"Zorganizuj imprezę urodzinową na 10 osób pojutrze"
```

lub

```
"Chcę zrobić party dla mojej dziewczyny, będzie 15 osób"
```

**System wykryje** że to party request i automatycznie przejdzie w tryb planowania.

### Krok 2: System Generuje Plan (Action-Oriented Format)

Otrzymasz plan w formacie gotowym do wykonania:

```
Oto plan dla Twojej imprezy:

Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Impreza zaczyna się około godziny 16:00 i potrwa około 5 godzin.
- Zarezerwuj stolik w restauracji lub małą salę na 10 osób.
- Poproś o proste dekoracje, takie jak balony i serwetki.
- Omów menu z restauracją.
- Poproś o tort urodzinowy.

Czy chcesz coś zmienić czy zatwierdzasz?
```

**Nowy Format:** Instrukcje są pogrupowane po miejscach do których trzeba zadzwonić - gotowe do wykonania przez asystenta lub voice agent!

### Krok 3a: Modyfikuj Plan (opcjonalnie)

Możesz wprowadzać zmiany:

**Przykład: Przenieś tort do dedykowanej cukierni**
```
"Tort chcę z dedykowanej cukierni, napis 'Wszystkiego najlepszego Ada'"
```

System utworzy **nową grupę akcji** dla cukierni:
```
Oto zaktualizowany plan:

Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Impreza zaczyna się około godziny 16:00 i potrwa około 5 godzin.
- Zarezerwuj stolik w restauracji lub małą salę na 10 osób.
- Poproś o proste dekoracje, takie jak balony i serwetki.
- Omów menu z restauracją.

Zadzwonić do cukierni z tortami z następującymi instrukcjami:
- Poproś o tort urodzinowy.
- Na torcie powinno być napisane "Wszystkiego najlepszego Ada".

Czy chcesz coś zmienić czy zatwierdzasz?
```

System **automatycznie** przeniesie instrukcje między grupami!

### Krok 3b: Potwierdź Plan

Gdy plan jest OK:
```
"Potwierdzam"
```

lub

```
"OK"
```

```
"Tak, zatwierdź"
```

### Krok 4: Podaj Dane Kontaktowe

System poprosi o dane potrzebne do realizacji:

```
✅ Plan zatwierdzony!

📝 Teraz potrzebuję kilku danych do realizacji...

Jakie jest Twoje imię i nazwisko? (do rezerwacji)
```

Odpowiadasz po kolei:
```
YOU: Jan Kowalski
AI: Świetnie! A jaki numer telefonu kontaktowy?

YOU: +48 123 456 789
AI: Dziękuję! Potrzebuję jeszcze dokładnej daty...

YOU: 15 grudnia 2024
AI: I ostatnie - godzina wydarzenia?

YOU: 18:00
```

### Krok 5: Gotowe!

System potwierdzi:
```
✅ Świetnie! Mam wszystkie potrzebne dane:

📋 Podsumowanie:
• Imię i nazwisko: Jan Kowalski
• Telefon: +48 123 456 789
• Data: 15 grudnia 2024
• Godzina: 18:00

🎉 Plan imprezy jest gotowy do realizacji!
```

## 🔧 Testowanie

### Quick Test (CLI)

```bash
python3 test_party_planner.py
```

To uruchomi symulowany flow w terminalu.

### Full Test (przez Chat)

1. Uruchom backend i frontend
2. Otwórz http://localhost:3000
3. Napisz party request
4. Przejdź przez cały flow

## 🎯 Wykrywane Słowa Kluczowe

System automatycznie wykrywa party requests po słowach:
- "imprez", "urodziny", "przyjęcie"
- "celebration", "party", "event"
- "zorganizuj", "spotkanie"
- "świętowanie", "rocznica", "jubileusz"

## 📊 Persistence

- **Plany są zapisywane** w `database/plans/plan_{id}.json`
- **State jest persystentny** - możesz przeładować stronę i kontynuować
- **Historia jest zachowana** - wszystkie modyfikacje są zapisane

## 🔍 Debugging

### Sprawdź czy plan istnieje:
```bash
ls -la database/plans/
cat database/plans/plan_*.json
```

### Sprawdź logi backendu:
W terminalu gdzie działa uvicorn zobaczysz:
```
INFO: Routing to party planner (state: refinement)
INFO: Updated plan abc123, new state: confirmed
```

### Sprawdź state w database:
```bash
cat database/plans/plan_*.json | grep state
```

## ⚙️ Konfiguracja

### Zmiana Modelu

W `backend/party_planner.py`:
```python
def __init__(self, model: str = "gemini-2.5-flash"):
```

Zmień na inny model Gemini jeśli potrzebujesz.

### Modyfikacja Promptów

W `backend/party_planner.py` możesz edytować:
- `plan_generation_prompt` - jak generować plan
- `plan_refinement_prompt` - jak modyfikować plan
- `info_gathering_prompt` - jakie dane zbierać

## 🎨 UI Integration

**Zero zmian w UI!** Feature działa całkowicie przez istniejący chat interface.

- Plan jest wyświetlany jako sformatowany tekst
- Emoji dodają visual appeal
- Wszystkie interakcje przez zwykłe wiadomości

## 🚧 Limitations (MVP)

Obecna wersja **nie wykonuje** rzeczywistych akcji (calls, reservations).

To jest **planowanie i zbieranie danych**. 

Następny krok: integracja z execution layer (voice_agent.py, API calls).

## 📝 Troubleshooting

### Problem: "Nie wykrywa party request"
**Rozwiązanie:** Użyj klarowniejszego języka:
- ❌ "Chcę coś zorganizować"
- ✅ "Zorganizuj imprezę"

### Problem: "Plan nie się modyfikuje"
**Rozwiązanie:** Bądź konkretny w feedback:
- ❌ "Zmień coś"
- ✅ "Dodaj balony do dekoracji"

### Problem: "Nie przechodzi do gathering"
**Rozwiązanie:** Użyj confirmation keyword:
- ❌ "Jest OK"
- ✅ "Potwierdzam"

### Problem: "Backend error 500"
**Rozwiązanie:**
1. Sprawdź czy GEMINI_API_KEY jest ustawiony
2. Zobacz logi backendu
3. Sprawdź czy masz quota na API

## 🎯 Success Metrics

✅ Wykrywa party requests automatycznie  
✅ Generuje sensowne plany  
✅ Pozwala na iteracyjne modyfikacje  
✅ Zbiera wszystkie potrzebne dane  
✅ Persystuje state między reloadami  
✅ Działa płynnie w chat UI  

## 🚀 Next Steps (Future Enhancement)

1. **Execution Layer** - faktyczne wykonywanie akcji
2. **Voice Integration** - automated calls przez voice_agent
3. **API Integrations** - połączenie z booking APIs
4. **Calendar Integration** - sync z Google Calendar
5. **Email Notifications** - potwierdzenia email
6. **Payment Integration** - płatności online

---

**Implementacja:** ✅ Complete  
**Status:** 🟢 Ready to Use  
**Version:** 1.0 MVP  

Enjoy planning parties! 🎉

