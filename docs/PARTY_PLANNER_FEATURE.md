# 🎉 Party Planner Feature - Plan Implementacji

## 📋 Podsumowanie Feature'a

Rozszerzenie systemu o **inteligentnego planera imprez**, który:
1. Rozumie request użytkownika (np. "Zorganizuj imprezę urodzinową na 10 osób")
2. Generuje szczegółowy plan imprezy
3. Iteracyjnie zbiera feedback i modyfikuje plan
4. Zbiera dane kontaktowe potrzebne do wykonania (nazwiska, telefony)
5. Integruje się z frontendem chatowym (już istniejącym)

## 🎯 Przykładowy Flow (z spec_file.md)

```
USER: "Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę na 10 osób."
  ↓
AGENT: [Generuje plan] "Oto plan:
  - Rezerwacja sali (Restaurant X, 19:00)
  - Tort urodzinowy (Cukiernia Y)
  - Dekoracje
  - Catering dla 10 osób
  
  Czy chcesz coś dostosować czy potwierdzasz?"
  ↓
USER: "Do rezerwacji sali chcę dorzucić balony, a tort chcę żeby był w dedykowanej cukierni"
  ↓
AGENT: [Modyfikuje plan] "Oto poprawiony plan:
  - Rezerwacja sali (Restaurant X, 19:00) + balony
  - Tort urodzinowy (Cukiernia specjalistyczna)
  - Catering dla 10 osób
  
  Czy chcesz coś dostosować czy potwierdzasz?"
  ↓
USER: "Potwierdzam"
  ↓
AGENT: "Świetnie! Teraz potrzebuję kilku danych do realizacji:
  - Imię i nazwisko do rezerwacji
  - Numer telefonu
  - Preferowana data i godzina
  ..."
  ↓
[Agent zbiera informacje jak w InformationGatherer]
  ↓
AGENT: "Mam wszystkie dane. Wykonuję rezerwacje..." [Calls API]
```

## 🏗️ Architektura Rozwiązania

### Backend Components

#### 1. **PartyPlanner Class** (nowy plik: `party_planner.py`)

```python
class PartyPlanner:
    """
    Multi-step party planning with iterative refinement
    
    States:
    - INITIAL: Zbieranie podstawowych wymagań
    - PLANNING: Generowanie planu
    - REFINEMENT: Modyfikacja planu na podstawie feedbacku
    - CONFIRMED: Plan zatwierdzony, zbieranie danych
    - GATHERING: Zbieranie szczegółów (info_gatherer)
    - EXECUTING: Wykonywanie akcji (calls, reservations)
    - COMPLETE: Zakończone
    """
```

**Kluczowe metody:**
- `process_request(user_input)` - główna logika state machine
- `generate_plan(requirements)` - generuje plan przez LLM
- `refine_plan(current_plan, feedback)` - modyfikuje plan
- `extract_plan_items()` - parsuje plan na actionable items
- `gather_execution_details()` - zbiera dane (phone, name, etc)
- `execute_plan()` - wykonuje akcje (API calls)

#### 2. **PlanState Model** (rozszerzenie `models.py`)

```python
class PlanState(str, Enum):
    INITIAL = "initial"
    PLANNING = "planning"
    REFINEMENT = "refinement"
    CONFIRMED = "confirmed"
    GATHERING = "gathering"
    EXECUTING = "executing"
    COMPLETE = "complete"

class PlanItem(BaseModel):
    id: str
    type: str  # "reservation", "order", "call"
    description: str
    venue: Optional[str]
    contact_needed: bool
    status: str  # "pending", "in_progress", "done"
    required_info: List[str]  # ["phone", "name", "date"]

class PartyPlan(BaseModel):
    id: str
    user_request: str
    current_plan: List[PlanItem]
    state: PlanState
    conversation_id: str
    gathered_info: dict  # Zebrane dane
    feedback_history: List[str]
    created_at: datetime
    updated_at: datetime
```

#### 3. **Integration z Chat** (modyfikacja `chat_service.py`)

```python
class ChatService:
    def __init__(self):
        self.party_planner = PartyPlanner()
        self.active_plans = {}  # conversation_id -> PartyPlan
    
    async def process_user_message(self, conversation_id, content):
        # Check if there's an active party plan
        if conversation_id in self.active_plans:
            return await self.party_planner.process_request(
                conversation_id, 
                content
            )
        
        # Check if message is party-related (detect intent)
        if self.is_party_request(content):
            # Start new party plan
            return await self.party_planner.start_planning(
                conversation_id,
                content
            )
        
        # Normal chat
        return await self.generate_ai_response(...)
```

#### 4. **Plan Storage** (rozszerzenie `storage_manager.py`)

```python
# database/plans/plan_{id}.json
{
  "id": "plan_123",
  "conversation_id": "conv_456",
  "state": "refinement",
  "user_request": "Zorganizuj imprezę na 10 osób",
  "current_plan": [
    {
      "id": "item_1",
      "type": "reservation",
      "description": "Rezerwacja sali Restaurant X na 19:00",
      "venue": "Restaurant X",
      "contact_needed": true,
      "required_info": ["full_name", "phone", "date", "time"],
      "status": "pending"
    }
  ],
  "gathered_info": {},
  "feedback_history": ["Dodaj balony"]
}
```

### Frontend Components (już mamy chat!)

**Nie trzeba zmieniać UI!** Używamy istniejącego chat interface.

Rozszerzamy tylko **formatowanie odpowiedzi**:
- Plan wyświetlany jako formatted text (lista)
- Akcje jako buttons? (opcjonalnie, można przez tekst)
- Status updates w real-time

## 🔄 State Machine Flow

```
INITIAL
  ↓ [user describes party]
PLANNING (LLM generates plan)
  ↓ [plan shown to user]
REFINEMENT (user gives feedback)
  ↓ [plan modified] → back to REFINEMENT
  ↓ [user confirms "potwierdzam"]
CONFIRMED
  ↓ [need contact details?]
GATHERING (InformationGatherer takes over)
  ↓ [all info collected]
EXECUTING (make calls, API requests)
  ↓
COMPLETE
```

## 📝 Prompty dla LLM

### Prompt 1: Plan Generation
```
Jesteś organizatorem imprez. Użytkownik chce: "{user_request}"

Wygeneruj szczegółowy plan imprezy zawierający:
1. Wszystkie konieczne rezerwacje (sala, catering, etc)
2. Zamówienia (tort, dekoracje, balony)
3. Dodatkowe usługi

Format planu:
PLAN IMPREZY:
1. [Nazwa zadania] - [Szczegóły]
2. [Nazwa zadania] - [Szczegóły]
...

Na końcu zapytaj: "Czy chcesz coś dostosować czy potwierdzasz plan?"
```

### Prompt 2: Plan Refinement
```
Aktualny plan:
{current_plan}

Użytkownik chce zmienić:
"{user_feedback}"

Zaktualizuj plan według feedbacku i wyświetl nową wersję.
Na końcu zapytaj: "Czy chcesz coś dostosować czy potwierdzasz plan?"
```

### Prompt 3: Information Gathering
```
Plan zatwierdzony. Następujące zadania wymagają danych kontaktowych:
{tasks_needing_info}

Zbierz od użytkownika:
- Imię i nazwisko
- Numer telefonu
- Datę i godzinę (jeśli nie podana)
- Inne szczegóły specyficzne dla zadania

Pytaj o jedną informację na raz.
Gdy wszystkie zebrane, zwróć JSON:
```json
{
  "full_name": "...",
  "phone": "...",
  "date": "...",
  "time": "...",
  ...
}
```
```

## ✅ To-Do Lista

### Phase 1: Backend Foundation (Core Logic)

- [ ] **Task 1.1: Create PartyPlanner Class**
  - [ ] Stwórz `backend/party_planner.py`
  - [ ] Implementuj state machine (enum States)
  - [ ] Implementuj `__init__` z LLMClient
  - [ ] Dodaj prompty (plan generation, refinement, gathering)

- [ ] **Task 1.2: Implement Plan Generation**
  - [ ] Metoda `generate_plan(user_request)` 
  - [ ] Wywołanie LLM z promptem generation
  - [ ] Parsowanie odpowiedzi
  - [ ] Return formatted plan string

- [ ] **Task 1.3: Implement Plan Refinement**
  - [ ] Metoda `refine_plan(current_plan, feedback)`
  - [ ] Wywołanie LLM z promptem refinement
  - [ ] Update planu
  - [ ] Return updated plan

- [ ] **Task 1.4: Detection & State Management**
  - [ ] Metoda `detect_confirmation(user_input)` - wykrywa "potwierdzam"
  - [ ] Metoda `should_gather_info(plan)` - sprawdza czy potrzebne dane
  - [ ] State transitions (INITIAL → PLANNING → REFINEMENT → etc)

### Phase 2: Models & Storage

- [ ] **Task 2.1: Extend Models**
  - [ ] Dodaj `PlanState` enum do `models.py`
  - [ ] Dodaj `PlanItem` model
  - [ ] Dodaj `PartyPlan` model
  - [ ] Dodaj Request/Response modele dla API

- [ ] **Task 2.2: Plan Storage**
  - [ ] Stwórz folder `database/plans/`
  - [ ] Dodaj `.gitkeep` i update `.gitignore`
  - [ ] Extend `storage_manager.py`:
    - [ ] `save_plan(plan: PartyPlan)`
    - [ ] `load_plan(plan_id: str)`
    - [ ] `get_plan_by_conversation(conversation_id: str)`
    - [ ] `update_plan(plan: PartyPlan)`

### Phase 3: Integration with Chat

- [ ] **Task 3.1: Modify ChatService**
  - [ ] Import PartyPlanner w `chat_service.py`
  - [ ] Dodaj `active_plans` dict (conversation_id → PartyPlan)
  - [ ] Metoda `is_party_request(content)` - intent detection
  - [ ] Modify `process_user_message()`:
    - [ ] Check if active plan exists
    - [ ] Route to party planner if active
    - [ ] Detect new party requests
    - [ ] Route to normal chat otherwise

- [ ] **Task 3.2: PartyPlanner Integration**
  - [ ] Metoda główna: `process_request(conversation_id, user_input)`
  - [ ] State machine logic wewnątrz:
    - [ ] INITIAL → generate_plan()
    - [ ] PLANNING/REFINEMENT → handle feedback
    - [ ] CONFIRMED → transition to gathering
    - [ ] GATHERING → use InformationGatherer
    - [ ] COMPLETE → finalize

- [ ] **Task 3.3: InformationGatherer Integration**
  - [ ] Import InformationGatherer
  - [ ] Modify InformationGatherer żeby przyjmował custom system prompt
  - [ ] Generate dynamic prompt based on plan requirements
  - [ ] Integrate gathering phase w PartyPlanner

### Phase 4: API Endpoints (Optional Enhancement)

- [ ] **Task 4.1: Plan Router** (opcjonalnie)
  - [ ] `GET /api/plans/{conversation_id}` - get active plan
  - [ ] `POST /api/plans/{conversation_id}/confirm` - confirm plan
  - [ ] `GET /api/plans/{plan_id}/status` - check execution status

### Phase 5: Execution Layer (Future)

- [ ] **Task 5.1: Action Executor** (dla calls/reservations)
  - [ ] Stwórz `action_executor.py`
  - [ ] Implementuj `execute_reservation(item, contact_info)`
  - [ ] Implementuj `make_call(item, contact_info)` (using voice_agent.py)
  - [ ] Return execution results

- [ ] **Task 5.2: Integration z Voice Agent**
  - [ ] Link z `voice_agent.py`
  - [ ] Pass contact details
  - [ ] Trigger automated calls
  - [ ] Get call status/results

### Phase 6: Testing & Polish

- [ ] **Task 6.1: End-to-End Testing**
  - [ ] Test pełnego flow: request → plan → refinement → confirm
  - [ ] Test gathering phase
  - [ ] Test edge cases (cancel, invalid input)
  - [ ] Test persistence (reload conversation)

- [ ] **Task 6.2: Error Handling**
  - [ ] Handle LLM failures
  - [ ] Handle invalid plans
  - [ ] Handle incomplete gathering
  - [ ] User-friendly error messages

- [ ] **Task 6.3: Documentation**
  - [ ] Dodaj examples do README
  - [ ] Document prompts
  - [ ] API documentation (if endpoints created)

## 🎨 UI/UX w Chacie (używamy istniejącego)

### Plan Display Format
```
📋 PLAN IMPREZY

1. 🏢 Rezerwacja sali
   • Miejsce: Restaurant X
   • Godzina: 19:00
   • Liczba osób: 10
   • Dodatki: Balony

2. 🎂 Tort urodzinowy
   • Cukiernia: Słodkie Cuda
   • Rodzaj: Urodzinowy
   • Wielkość: 10 osób

3. 🍽️ Catering
   • Menu: Mix przystawek + danie główne
   • Liczba osób: 10

─────────────────────────
💬 Czy chcesz coś dostosować czy potwierdzasz plan?
```

### Status Updates
```
✅ Plan zatwierdzony!

📝 Teraz potrzebuję kilku danych do realizacji...

Jakie jest Twoje imię i nazwisko? (do rezerwacji)
```

## 🔧 Technical Details

### Intent Detection (Simple)
```python
def is_party_request(content: str) -> bool:
    keywords = [
        "imprez", "urodziny", "przyjęcie", "celebration",
        "zorganizuj", "party", "event", "spotkanie"
    ]
    return any(keyword in content.lower() for keyword in keywords)
```

### Plan Parsing (from LLM response)
```python
def parse_plan_items(llm_response: str) -> List[PlanItem]:
    # Parse numbered list from LLM
    lines = llm_response.split('\n')
    items = []
    for line in lines:
        if re.match(r'^\d+\.', line):  # Numbered item
            item = PlanItem(
                id=str(uuid.uuid4()),
                description=line,
                type=detect_type(line),
                ...
            )
            items.append(item)
    return items
```

### Confirmation Detection
```python
def is_confirmation(user_input: str) -> bool:
    confirmations = [
        "potwierdzam", "ok", "tak", "zgoda", 
        "confirm", "yes", "zatwierdź"
    ]
    return any(word in user_input.lower() for word in confirmations)
```

## 📊 Data Flow

```
User Input
    ↓
ChatService.process_user_message()
    ↓
[Check if party request or active plan]
    ↓
PartyPlanner.process_request()
    ↓
[State Machine]
    ├─ INITIAL → generate_plan() → LLM
    ├─ REFINEMENT → refine_plan() → LLM  
    ├─ CONFIRMED → transition to GATHERING
    └─ GATHERING → InformationGatherer.process_message()
    ↓
Save to storage (plans + conversation)
    ↓
Return response to frontend
    ↓
Display in chat
```

## 🚀 Phased Implementation Strategy

### MVP (Minimum Viable Product) - Phase 1-3
**Goal:** Basic planning flow without execution
- User request → Plan generation → Refinement → Confirm
- Integration z chat
- Persistence

**Time:** ~6-8 hours

### Enhanced - Phase 4-5
**Goal:** Full execution with calls/reservations
- Information gathering
- Action execution
- Voice agent integration

**Time:** +4-6 hours

### Complete - Phase 6
**Goal:** Production ready
- Testing
- Error handling
- Documentation

**Time:** +2-3 hours

## 🎯 Success Criteria

✅ User może zażądać organizacji imprezy przez chat  
✅ System generuje sensowny plan  
✅ User może modyfikować plan wielokrotnie  
✅ System zbiera potrzebne dane (imię, telefon, etc)  
✅ Plan jest zapisywany i persystuje po reload  
✅ Całość działa płynnie w istniejącym chat UI  

## 💡 Key Insights

### Integration Points:
1. **ChatService** - routing logic (normal chat vs party planning)
2. **InformationGatherer** - reuse dla gathering phase
3. **LLMClient** - reuse dla wszystkich LLM calls
4. **Storage** - extend dla plans
5. **Frontend** - zero changes needed! (używamy chat)

### Challenges:
1. **State Management** - tracking plan state across messages
2. **LLM Consistency** - ensuring structured responses
3. **Context Preservation** - maintaining plan context
4. **Error Recovery** - handling invalid inputs/LLM failures

### Solutions:
1. Store state in PartyPlan object + persist to disk
2. Use structured prompts + parsing
3. Include plan history in each LLM call
4. Graceful degradation + clear error messages

---

**Czas implementacji (MVP):** ~8-10 godzin  
**Priorytet:** High (hackathon demo)  
**Dependencies:** LLMClient, InformationGatherer, ChatService, Storage


