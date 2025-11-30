# Plan: Grupowanie wiadomości o połączeniach

## 🎯 Cel
Zmniejszyć verbose output przez zgrupowanie wszystkich wiadomości związanych z jednym połączeniem w jedną rozwijaną kartę.

## 📋 Obecny problem

Każde połączenie generuje **3 osobne wiadomości**:

1. **"📞 Dzwonię do Restauracja Kameralna"** - wiadomość startowa
2. **"📞 Zakończono rozmowę z..."** + TRANSKRYPT - wiadomość z transkryptem
3. **"⚠️ Nie udało się w..."** lub **"✅ Sukces w..."** - wiadomość z podsumowaniem

To daje **za dużo miejsca** i jest **trudne do przeczytania**.

---

## ✅ Rozwiązanie

### Frontend: Grupowanie wiadomości
1. **Wykryj sekwencję połączeń** w `ChatWindow.tsx`:
   - Znajdź wiadomość startową: `"📞 Dzwonię do:"`
   - Znajdź następną wiadomość z transkryptem: `"Zakończono rozmowę"`
   - Znajdź następną wiadomość z podsumowaniem: `"⚠️ Nie udało się"` lub `"✅ Sukces"`

2. **Zgrupuj te 3 wiadomości** w jeden komponent `CallGroup`:
   ```
   [CallGroup component]
   ├─ Header (zawsze widoczny):
   │  ├─ Pulsująca ikona 📞
   │  ├─ "Dzwonię do: Restauracja Kameralna"
   │  └─ Status: "⏳ W trakcie..." / "✅ Sukces" / "⚠️ Niepowodzenie"
   │
   └─ Collapsible Details (kliknij żeby rozwinąć):
      ├─ Transkrypt rozmowy (jeśli istnieje)
      ├─ Analiza/podsumowanie (jeśli istnieje)
      └─ Instrukcje dla agenta (opcjonalnie)
   ```

3. **Animacja statusu**:
   - Podczas dzwonienia: ikona pulsuje + "⏳ Dzwonię..."
   - Po zakończeniu: ikona stała + status sukcesu/błędu

---

## 🔧 Implementacja

### Krok 1: Nowy komponent `CallGroup.tsx`
Stwórz komponent który:
- Przyjmuje 1-3 wiadomości (startowa, transkrypt, podsumowanie)
- Renderuje zgrupowaną kartę z collapsible details
- Obsługuje 3 stany: `calling`, `success`, `failed`

### Krok 2: Modyfikacja `ChatWindow.tsx`
Przed renderowaniem wiadomości:
- Przejdź przez tablicę `messages`
- Znajdź sekwencje połączeń (startowa → transkrypt → podsumowanie)
- Zgrupuj je w obiekty `CallGroupData[]`
- Renderuj `CallGroup` zamiast 3 osobnych `ChatMessage`

### Krok 3: Identyfikacja wiadomości
Użyj `metadata` z backendu:
```typescript
// Wiadomość startowa
metadata: {
  call_id: "call-123",
  call_stage: "initiated",
  place_name: "Restauracja Kameralna"
}

// Wiadomość z transkryptem
metadata: {
  call_id: "call-123",
  call_stage: "transcript",
  place_name: "Restauracja Kameralna"
}

// Wiadomość z podsumowaniem
metadata: {
  call_id: "call-123",
  call_stage: "completed",
  place_name: "Restauracja Kameralna",
  call_success: false
}
```

---

## 🎨 UI Flow

### Podczas dzwonienia (tylko wiadomość startowa):
```
┌─────────────────────────────────────────┐
│ 📞 [pulsing] Dzwonię do Restauracja...  │
│ ⏳ Czekam na połączenie...               │
│                                          │
│ [▼ Szczegóły połączenia]                │
└─────────────────────────────────────────┘
```

### Po zakończeniu (wszystkie 3 wiadomości zgrupowane):
```
┌─────────────────────────────────────────┐
│ ⚠️  Nie udało się: Restauracja Kameralna│
│ 💬 Brak wolnych miejsc                   │
│                                          │
│ [▼ Zobacz transkrypt i szczegóły] ◄──┐  │
└───────────────────────────────────────┘  │
                                           │
  ┌────────────────────────────────────────┘
  │ (Po kliknięciu rozwijane)
  │
  ▼
┌─────────────────────────────────────────┐
│ ⚠️  Nie udało się: Restauracja Kameralna│
│ 💬 Brak wolnych miejsc                   │
│                                          │
│ [▲ Ukryj szczegóły]                     │
│ ┌─────────────────────────────────────┐ │
│ │ 📝 Instrukcje dla agenta:           │ │
│ │ Dzwonisz do lokalu/restauracji...   │ │
│ │                                     │ │
│ │ 📞 Transkrypt:                      │ │
│ │ 🤖 AGENT: Dzień dobry...            │ │
│ │ 👤 USER: Niestety nie ma...         │ │
│ │                                     │ │
│ │ 💬 Analiza:                         │ │
│ │ Rozmowa została przerwana...        │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🚀 Korzyści

1. ✅ **Kompaktowy widok** - jedna karta zamiast 3 wiadomości
2. ✅ **Mniej scrollowania** - łatwiejsze przeglądanie historii
3. ✅ **Jasny status** - na pierwszy rzut oka widać wynik
4. ✅ **Szczegóły na żądanie** - rozwiń gdy potrzebujesz więcej info
5. ✅ **Live updates** - status zmienia się w czasie rzeczywistym

---

## 🔄 Backend: Dodanie call_id do metadata

Zmodyfikuj `chat_service.py`:

```python
# Generuj unikalny call_id dla każdego połączenia
call_id = f"call-{uuid.uuid4().hex[:8]}"

# Wiadomość startowa
Message(
    metadata={
        "call_id": call_id,
        "call_stage": "initiated",
        "place_name": place.name,
        "task_id": task.task_id
    }
)

# Wiadomość z transkryptem
Message(
    metadata={
        "call_id": call_id,
        "call_stage": "transcript",
        "place_name": place.name
    }
)

# Wiadomość z podsumowaniem
Message(
    metadata={
        "call_id": call_id,
        "call_stage": "completed",
        "place_name": place.name,
        "call_success": success
    }
)
```

---

## 📦 Podsumowanie zmian

### Backend (`chat_service.py`):
- Dodaj `call_id` do metadata wszystkich wiadomości związanych z połączeniem
- Dodaj `call_stage`: `"initiated"`, `"transcript"`, `"completed"`
- Dodaj `call_success`: `true`/`false` w wiadomości podsumowującej

### Frontend:
- **Nowy komponent**: `CallGroup.tsx` - zgrupowana karta połączenia
- **Modyfikacja**: `ChatWindow.tsx` - grupowanie wiadomości przed renderowaniem
- **Opcjonalna modyfikacja**: `ChatMessage.tsx` - lepsze wykrywanie typu wiadomości

---

## ✨ Rezultat końcowy

Zamiast:
```
[AI] Dzwonię do Restauracja A
[AI] Transkrypt: ...
[AI] ⚠️ Niepowodzenie

[AI] Dzwonię do Restauracja B  
[AI] Transkrypt: ...
[AI] ✅ Sukces!

[AI] Dzwonię do Cukiernia X
[AI] Transkrypt: ...
[AI] ✅ Sukces!
```

Będzie:
```
[CallGroup] ⚠️ Restauracja A [▼]
[CallGroup] ✅ Restauracja B [▼]  
[CallGroup] ✅ Cukiernia X [▼]
```

**Dużo mniej verbose, dużo bardziej czytelne!** 🎯

