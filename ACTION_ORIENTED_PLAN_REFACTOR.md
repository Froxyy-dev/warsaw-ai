# 📞 Action-Oriented Plan Format - Refactor Plan

## 📋 Podsumowanie Zmian

Obecnie plan jest **item-oriented** (lista rzeczy do zrobienia):
```
- Rezerwacja miejsca
- Dekoracje
- Tort
- Catering
```

Nowy format ma być **action-oriented** (grupowane po akcjach/telefonach):
```
Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Zarezerwuj stolik na 10 osób
- Poproś o dekoracje (balony, serwetki)
- Omów menu

Zadzwonić do cukierni z następującymi instrukcjami:
- Poproś o tort urodzinowy
- Napis: "Wszystkiego najlepszego Ada"
```

## 🎯 Dlaczego Ta Zmiana?

### Use Case: Voice Agent Integration
Ten format jest **gotowy do wykonania** przez voice agent:
1. System widzi "Zadzwonić do lokalu z salami"
2. Ma listę instrukcji co powiedzieć
3. Może bezpośrednio wykonać call z tymi instrukcjami

### Korzyści:
- ✅ **Executable** - można bezpośrednio przekazać do voice_agent.py
- ✅ **Grouped by recipient** - jasne kto ma być wywołany
- ✅ **Clear instructions** - agent wie co powiedzieć
- ✅ **Easy to modify** - user może przenieść tort do innej cukierni
- ✅ **Scalable** - łatwo dodać więcej akcji/callów

## 📐 Przykładowy Flow (z spec_file.md)

### Request:
```
USER: Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę urodzinową, 
która zacznie się około godziny 16:00 i potrwa około 5 godzin
```

### Initial Plan:
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

### User Modification:
```
USER: Jest okej, ale chciałbym żeby tort urodzinowy zamówić z cukierni 
zajmującej się profesjonalnie tortami, a na torcie będzie napis 
"Wszystkiego najlepszego Ada"
```

### Refined Plan:
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

## 🔧 Zmiany Techniczne

### 1. **Format Struktury Planu**

#### Stary Format (Item List):
```
Oto plan:
- [Item 1]
- [Item 2]
- [Item 3]
```

#### Nowy Format (Action Groups):
```
Oto plan dla Twojej imprezy:

[ACTION GROUP 1: Recipient]
[Instruction 1]
[Instruction 2]

[ACTION GROUP 2: Recipient]
[Instruction 1]
[Instruction 2]
```

### 2. **Prompt Changes**

Trzeba zaktualizować prompty w `party_planner.py`:

#### plan_generation_prompt:
- Dodać kontekst o czasie trwania imprezy
- Grupować po akcjach (calls)
- Format: "Zadzwonić do [miejsce] z następującymi instrukcjami:"
- Każda instrukcja jako bullet point

#### plan_refinement_prompt:
- Umieć przenosić instrukcje między grupami
- Umieć tworzyć nowe grupy akcji (np. nowa cukiernia)
- Zachować format z grupowaniem

### 3. **Parsowanie Planu (Future Enhancement)**

Dla późniejszej integracji z voice agent:

```python
class ActionGroup:
    recipient: str  # "lokal z salami", "cukiernia"
    instructions: List[str]  # Lista instrukcji
    
def parse_action_plan(plan_text: str) -> List[ActionGroup]:
    """Parse plan into executable action groups"""
    # Regex to find groups:
    # "Zadzwonić do [recipient] z następującymi instrukcjami:"
    # followed by bullet points
```

## ✅ To-Do Lista

### Phase 1: Prompt Updates (Core Changes)

- [ ] **Task 1.1: Update plan_generation_prompt**
  - [ ] Zmień strukturę na action-oriented format
  - [ ] Dodaj "Zadzwonić do [miejsce] z następującymi instrukcjami:"
  - [ ] Grupuj instrukcje pod każdym action header
  - [ ] Uwzględnij informacje o czasie (godzina rozpoczęcia, czas trwania)
  - [ ] Usuń emojis/fancy formatting - prosty text

- [ ] **Task 1.2: Update plan_refinement_prompt**
  - [ ] Zachowaj action-oriented format
  - [ ] Umożliw przenoszenie instrukcji między grupami
  - [ ] Umożliw tworzenie nowych grup (np. nowa cukiernia)
  - [ ] Instrukcje jak interpretować feedback typu "tort z innej cukierni"

- [ ] **Task 1.3: Update info_gathering_prompt (optional)**
  - [ ] Uwzględnij że plan zawiera action groups
  - [ ] Może być potrzebne więcej szczegółów (np. nazwa cukierni)

### Phase 2: Testing & Validation

- [ ] **Task 2.1: Test Basic Flow**
  - [ ] Test z przykładem z spec_file.md
  - [ ] Sprawdź czy plan ma poprawny format
  - [ ] Sprawdź czy instrukcje są sensowne

- [ ] **Task 2.2: Test Refinement**
  - [ ] Test przenoszenia tort do cukierni
  - [ ] Test dodawania nowych instrukcji
  - [ ] Test usuwania instrukcji
  - [ ] Test tworzenia nowych action groups

- [ ] **Task 2.3: Test Edge Cases**
  - [ ] Co jeśli user chce wszystko w jednym miejscu?
  - [ ] Co jeśli user chce więcej grup (dekoracje osobno)?
  - [ ] Co jeśli user chce zmienić godzinę?

### Phase 3: Plan Parsing (Future - for Voice Agent)

- [ ] **Task 3.1: Create ActionGroup Model**
  - [ ] Dodaj ActionGroup do models.py
  - [ ] recipient: str
  - [ ] instructions: List[str]
  - [ ] metadata: dict (phone number, address, etc)

- [ ] **Task 3.2: Implement Parser**
  - [ ] Funkcja parse_action_plan(text) -> List[ActionGroup]
  - [ ] Regex dla "Zadzwonić do [X]"
  - [ ] Extract bullet points po każdym header
  - [ ] Return structured data

- [ ] **Task 3.3: Voice Agent Integration**
  - [ ] Extend voice_agent.py
  - [ ] Przyjmuj ActionGroup jako input
  - [ ] Generate script z instructions
  - [ ] Make call

### Phase 4: UI Enhancement (Optional)

- [ ] **Task 4.1: Structured Display**
  - [ ] Jeśli chcesz fancy UI w chacie
  - [ ] Każda action group jako osobny blok
  - [ ] Collapsible instructions
  - [ ] Icons dla różnych typów akcji

## 📝 Szczegółowe Zmiany w Kodzie

### File: `backend/party_planner.py`

#### Stary plan_generation_prompt:
```python
self.plan_generation_prompt = """Jesteś profesjonalnym organizatorem imprez.

Użytkownik chce: "{user_request}"

Wygeneruj PROSTY i KRÓTKI plan (3-4 zdania). Wymień tylko główne rzeczy:
- Rezerwacja miejsca/sali
- Dekoracje
- Tort
- Catering (jeśli potrzebny)

Format:
Oto plan dla Twojej imprezy:
- [zadanie 1]
- [zadanie 2]
- [zadanie 3]

Czy chcesz coś zmienić czy zatwierdzasz?"""
```

#### Nowy plan_generation_prompt:
```python
self.plan_generation_prompt = """Jesteś profesjonalnym organizatorem imprez, który przygotowuje plany do wykonania przez asystenta.

Użytkownik chce: "{user_request}"

Wygeneruj plan w formacie ACTION-ORIENTED - grupuj zadania po miejscach/osobach do których trzeba zadzwonić.

WAŻNE ZASADY:
1. Każda grupa zaczyna się od: "Zadzwonić do [miejsce/osoba] z następującymi instrukcjami:"
2. Pod tym header wymień konkretne instrukcje jako bullet points (-)
3. Uwzględnij WSZYSTKIE szczegóły z requesta (godzina, czas trwania, liczba osób, specjalne życzenia)
4. Bądź konkretny - instrukcje muszą być gotowe do przekazania przez telefon
5. Domyślnie grupuj wszystko pod jednym miejscem (np. lokal z salami), chyba że user wymaga osobno

PRZYKŁAD:
Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Zarezerwuj stolik na [X] osób
- Impreza zaczyna się o [godzina] i potrwa około [czas]
- Poproś o dekoracje: balony, serwetki
- Omów menu
- Poproś o tort urodzinowy

Format odpowiedzi:
Oto plan dla Twojej imprezy:

[ACTION GROUP 1]
[instructions...]

[ACTION GROUP 2 - jeśli potrzebny]
[instructions...]

Czy chcesz coś zmienić czy zatwierdzasz?"""
```

#### Nowy plan_refinement_prompt:
```python
self.plan_refinement_prompt = """Jesteś profesjonalnym organizatorem imprez, który aktualizuje plany według feedbacku.

AKTUALNY PLAN:
{current_plan}

FEEDBACK UŻYTKOWNIKA:
"{user_feedback}"

Zaktualizuj plan według feedbacku, zachowując ACTION-ORIENTED format.

WAŻNE ZASADY AKTUALIZACJI:
1. Jeśli user chce przenieść coś do innego miejsca (np. "tort z cukierni"):
   - Usuń tę instrukcję z obecnej grupy
   - Stwórz nową grupę: "Zadzwonić do [nowe miejsce] z następującymi instrukcjami:"
   
2. Jeśli user dodaje szczegóły (np. "napis na torcie"):
   - Dodaj jako nowy bullet point w odpowiedniej grupie
   
3. Jeśli user usuwa coś:
   - Usuń odpowiedni bullet point
   - Jeśli grupa zostaje pusta, usuń całą grupę

4. Zachowaj format:
   "Zadzwonić do [miejsce] z następującymi instrukcjami:"
   - [instrukcja 1]
   - [instrukcja 2]

Format odpowiedzi:
Oto zaktualizowany plan:

[ACTION GROUP 1]
[instructions...]

[ACTION GROUP 2]
[instructions...]

Czy chcesz coś zmienić czy zatwierdzasz?"""
```

## 🎯 Przykłady Testowe

### Test 1: Basic Request
```
INPUT: "Zorganizuj imprezę urodzinową na 10 osób, start 16:00, 5 godzin"

EXPECTED OUTPUT:
Oto plan dla Twojej imprezy:

Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Impreza zaczyna się około godziny 16:00 i potrwa około 5 godzin.
- Zarezerwuj stolik w restauracji lub małą salę na 10 osób.
- Poproś o proste dekoracje, takie jak balony i serwetki.
- Omów menu z restauracją.
- Poproś o tort urodzinowy.

Czy chcesz coś zmienić czy zatwierdzasz?
```

### Test 2: Refinement - Move to Bakery
```
INPUT: "Tort chcę z dedykowanej cukierni, napis 'Wszystkiego najlepszego Ada'"

EXPECTED OUTPUT:
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

### Test 3: Add Details
```
INPUT: "Dodaj że menu ma być wegetariańskie"

EXPECTED OUTPUT:
Oto zaktualizowany plan:

Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Impreza zaczyna się około godziny 16:00 i potrwa około 5 godzin.
- Zarezerwuj stolik w restauracji lub małą salę na 10 osób.
- Poproś o proste dekoracje, takie jak balony i serwetki.
- Omów menu z restauracją - WEGETARIAŃSKIE.

Zadzwonić do cukierni z tortami z następującymi instrukcjami:
- Poproś o tort urodzinowy.
- Na torcie powinno być napisane "Wszystkiego najlepszego Ada".

Czy chcesz coś zmienić czy zatwierdzasz?
```

## 🔮 Future Enhancements

### 1. Structured Parsing
Po zatwierdzeniu planu, parsuj go na ActionGroups:
```python
plan = PartyPlan(...)
action_groups = parse_action_plan(plan.current_plan)
# [
#   ActionGroup(recipient="lokal z salami", instructions=[...]),
#   ActionGroup(recipient="cukiernia", instructions=[...])
# ]
```

### 2. Voice Agent Integration
```python
for action_group in action_groups:
    script = generate_call_script(action_group)
    result = voice_agent.make_call(
        recipient=action_group.recipient,
        script=script,
        user_info=gathered_info
    )
```

### 3. Contact Database
```python
# Mapa miejsc -> kontakty
contacts = {
    "lokal z salami": {
        "Restaurant X": "+48 123 456 789",
        "Sala Bankietowa Y": "+48 987 654 321"
    },
    "cukiernia": {
        "Słodkie Cuda": "+48 111 222 333",
        "Tort Master": "+48 444 555 666"
    }
}
```

## 📊 Impact Analysis

### Breaking Changes:
- ❌ Żadnych! Format jest tylko w promptach
- ✅ Backward compatible - stare konwersacje działają
- ✅ Storage bez zmian
- ✅ Frontend bez zmian (to tylko tekst)

### Risk Level: **LOW**
- To tylko zmiana promptów
- Łatwo rollback jeśli nie działa
- Nie wymaga migracji danych

### Estimated Time:
- **Phase 1** (Prompts): 30 minut
- **Phase 2** (Testing): 30 minut
- **Phase 3** (Parsing - future): 2-3 godziny
- **Phase 4** (Voice integration - future): 4-6 godzin

## 🚀 Implementation Order

1. **Update prompts** (Task 1.1, 1.2) - 30min
2. **Test basic flow** (Task 2.1) - 15min
3. **Test refinement** (Task 2.2) - 15min
4. **Deploy & validate** - 10min

**Total for MVP: ~1 hour**

---

**Status:** 📋 Ready to Implement  
**Priority:** 🔥 High (needed for voice agent integration)  
**Complexity:** 🟢 Low (just prompt changes)


