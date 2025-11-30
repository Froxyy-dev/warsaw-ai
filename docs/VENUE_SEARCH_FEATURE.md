# 🔍 Venue & Bakery Search Feature - Plan Implementacji

> **⚠️ WAŻNE:** Ten feature używa istniejącego formatu `Task` i `Place` z `backend/task.py`.  
> NIE tworzymy nowych modeli dla tasków - używamy tego co już istnieje!

## 📋 Podsumowanie Feature'a

Po zebraniu danych od użytkownika (imię, telefon, lokalizacja), system musi:
1. **Znaleźć 3 lokale z salami** w danej lokalizacji (web search)
2. **Wyświetlić lokale** użytkownikowi w chacie (nazwa, telefon, link)
3. **Znaleźć 3 cukiernie** w danej lokalizacji (web search)
4. **Wyświetlić cukiernie** użytkownikowi w chacie
5. **Przygotować task list** dla voice agenta
6. **Wyświetlić task list** w konsoli backendu (do walidacji)

## 📦 Task Format (z task.py)

**WAŻNE:** Używamy istniejącego formatu `Task` i `Place` z `backend/task.py`:

```python
@dataclass
class Place:
    name: str        # Nazwa miejsca (np. "Restaurant Warszawa")
    phone: str       # Numer telefonu

@dataclass
class Task:
    task_id: str              # Unique ID (np. "party-restaurant-001")
    notes_for_agent: str      # Wszystkie instrukcje w JEDNYM stringu
    places: List[Place]       # Lista miejsc do zadzwonienia
```

**Zalety tego formatu:**
- ✅ Już istnieje w projekcie
- ✅ Prosty i czytelny dla voice agenta
- ✅ notes_for_agent to naturalny tekst (nie lista)
- ✅ Może mieć wiele Places w jednym Task
- ✅ Łatwy do serializacji do JSON

**Przykład Task:**
```python
Task(
    task_id="party-restaurant-abc123",
    notes_for_agent=(
        "Dzwonisz do restauracji aby zarezerwować miejsce na imprezę urodzinową. "
        "Dane organizatora: Mateusz Winiarek, tel: 886859039. "
        "Szczegóły: Data 1 grudnia, 16:00, 5h, około 10 osób, "
        "menu tradycyjna polska kuchnia, dekoracje urodzinowe."
    ),
    places=[Place(name="Restaurant Warszawa", phone="+48221234567")]
)
```

## 🎯 Główne Cele

### Use Case Flow (z spec_file.md):
```
[User zatwierdza plan]
  ↓
[Zbieranie danych: imię, telefon, lokalizacja]
  ↓
[NOWY KROK: Web Search]
  ↓
AI: "Szukam lokali w Warszawie..."
  ↓
AI: "Znalazłem 3 lokale:
     1. Restaurant X - tel: +48... - www.restaurantx.pl
     2. Sala Bankietowa Y - tel: +48... - www.salay.pl
     3. Lounge Z - tel: +48... - www.loungez.pl"
  ↓
AI: "Szukam cukierni..."
  ↓
AI: "Znalazłem 3 cukiernie:
     1. Słodkie Cuda - tel: +48... - www.slodkiecuda.pl
     2. Tort Master - tel: +48... - www.tortmaster.pl
     3. Cukiernia Ada - tel: +48... - www.cukierniaada.pl"
  ↓
[Backend console - Task objects]:

Task(
    task_id="party-restaurant-abc123",
    notes_for_agent=(
        "Dzwonisz do Restaurant X w sprawie imprezy urodzinowej.\n"
        "Dane kontaktowe organizatora: Mateusz Winiarek, tel: 886859039.\n\n"
        "Szczegóły:\n"
        "- Rezerwacja: 1 grudnia, 16:00, 5h\n"
        "- Liczba: 10 osób\n"
        "- Dekoracje urodzinowe\n"
        "- Menu: tradycyjna polska kuchnia\n\n"
        "Jeśli nie ma dostępności na podany termin, zapytaj o najbliższy możliwy. "
        "Na koniec potwierdź wszystkie szczegóły."
    ),
    places=[Place(name="Restaurant X", phone="+48 123 456 789")]
)

Task(
    task_id="party-bakery-def456",
    notes_for_agent=(
        "Dzwonisz do Słodkie Cuda w sprawie imprezy urodzinowej.\n"
        "Dane kontaktowe organizatora: Mateusz Winiarek, tel: 886859039.\n\n"
        "Szczegóły:\n"
        "- Tort urodzinowy\n"
        "- Napis: 'Wszystkiego najlepszego Ada'\n\n"
        "Zapytaj o cenę i dostępność na 1 grudnia. "
        "Potwierdź wszystkie szczegóły zamówienia."
    ),
    places=[Place(name="Słodkie Cuda", phone="+48 987 654 321")]
)

Total Tasks: 2 | Ready for Voice Agent: YES
─────────────────────────────
```

## 🏗️ Architektura Rozwiązania

### 1. **VenueSearcher Class** (nowy: `venue_searcher.py`)

```python
class VenueSearcher:
    """
    Searches for venues and bakeries using web search
    """
    
    def __init__(self):
        self.llm_client = LLMClient()  # Has Google Search tool
    
    def search_venues(self, location: str, query_type: str, count: int = 3):
        """
        Search for venues using Google Search
        
        Args:
            location: City/location (e.g. "Warszawa")
            query_type: "lokale z salami" or "cukiernie"
            count: Number of results to return
            
        Returns:
            List of venues with name, phone, website
        """
```

**Metody:**
- `search_venues(location, "lokale z salami", count=3)` → List[Venue]
- `search_bakeries(location, count=3)` → List[Venue]
- `parse_search_results(llm_response)` → List[Venue]
- `format_for_user(venues)` → str (formatted list for chat)

### 2. **Venue Model** (extend `models.py`)

```python
class Venue(BaseModel):
    name: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    type: str  # "restaurant", "bakery", "venue"

class VenueSearchResult(BaseModel):
    venues: List[Venue]
    location: str
    query_type: str
    searched_at: datetime
```

### 3. **TaskList Generator** (extend `party_planner.py`)

```python
from backend.task import Task, Place

class PartyPlanner:
    def generate_task_list(
        self,
        plan: PartyPlan,
        venues: List[Venue],
        bakeries: List[Venue],
        user_info: dict
    ) -> List[Task]:
        """
        Generate task list for voice agent based on:
        - Confirmed plan (action groups)
        - Selected venues
        - Gathered contact info (name, phone)
        
        Returns List[Task] in format from task.py
        """
```

### 4. **Task Format** (już istnieje w `task.py`)

**WAŻNE:** Używamy istniejącego formatu z `backend/task.py`:

```python
@dataclass
class Place:
    name: str
    phone: str

@dataclass
class Task:
    task_id: str
    notes_for_agent: str  # Single string with ALL instructions
    places: List[Place]   # List of places to call
```

**Przykład:**
```python
Task(
    task_id="party-restaurant-001",
    notes_for_agent=(
        "Dzwonisz do restauracji aby zarezerwować miejsce na imprezę urodzinową. "
        "Dane kontaktowe organizatora: Mateusz Winiarek, tel: +48 886 859 039. "
        "Szczegóły rezerwacji: "
        "- Data: 1 grudnia, godzina rozpoczęcia: 16:00 "
        "- Czas trwania: około 5 godzin "
        "- Liczba osób: około 10 "
        "- Menu: tradycyjna kuchnia polska "
        "- Dekoracje: proste dekoracje urodzinowe "
        "Jeśli restauracja nie ma wolnych miejsc na ten termin, zapytaj o najbliższy możliwy termin. "
        "Na koniec potwierdź wszystkie szczegóły rezerwacji."
    ),
    places=[
        Place(name="Restaurant Warszawa", phone="+48 22 123 4567")
    ]
)
```

**Dodatkowy Model dla Storage:**
```python
class TaskList(BaseModel):
    id: str
    plan_id: str
    tasks: List[Dict]  # List of Task objects (serialized)
    created_at: datetime
    status: str  # "pending", "in_progress", "completed"
```

### 5. **Integration w PartyPlanner**

Po gathering complete:
```python
from backend.task import Task, Place

# Current state: GATHERING → COMPLETE
# New flow: GATHERING → SEARCHING → TASK_GENERATION → COMPLETE

if state == PlanState.GATHERING and gathering_complete:
    # Transition to SEARCHING
    state = PlanState.SEARCHING
    
    # Search for venues
    location = gathered_info["location"]
    venues = venue_searcher.search_venues(location, "lokale", 3)
    # Show to user (formatted list)
    
    # Search for bakeries
    bakeries = venue_searcher.search_bakeries(location, 3)
    # Show to user (formatted list)
    
    # Transition to TASK_GENERATION
    state = PlanState.TASK_GENERATION
    
    # Generate task list (returns List[Task] from task.py)
    tasks = generate_task_list(
        plan=current_plan,
        venue=venues[0],  # Use first venue
        bakery=bakeries[0],  # Use first bakery
        user_info=gathered_info
    )
    
    # Print to console (for validation)
    print_task_list_to_console(tasks)
    
    # Save task list to database
    storage.save_task_list(tasks, plan_id=current_plan.id)
    
    # Transition to COMPLETE
    state = PlanState.COMPLETE
    return "✅ Wszystko gotowe! Lista zadań została przygotowana dla voice agenta."
```

## 🔍 Web Search Strategy

### Option 1: LLM z Google Search Tool (RECOMMENDED)
```python
# LLMClient już ma Google Search tool!
prompt = f"""Znajdź 3 najlepsze lokale z salami/restauracje w {location}.
Dla każdego podaj:
- Nazwa
- Numer telefonu
- Strona www (jeśli dostępna)

Format odpowiedzi (WAŻNE):
1. [Nazwa] - tel: [telefon] - [www]
2. [Nazwa] - tel: [telefon] - [www]
3. [Nazwa] - tel: [telefon] - [www]
"""

response = llm_client.send(prompt)
venues = parse_results(response)
```

**Zalety:**
- ✅ Już mamy Google Search w LLMClient
- ✅ Nie potrzeba dodatkowych API keys
- ✅ LLM może filtrować wyniki
- ✅ Działa z grounding_tool

### Option 2: Google Places API
Bardziej strukturalne, ale wymaga API key i setupu.

**Wybieramy Option 1 dla MVP!**

## 📝 Output Formats

### Format dla Użytkownika (w chacie):
```
🔍 Znalazłem lokale w Warszawie:

1. Restaurant Warszawa
   📞 +48 22 123 4567
   🌐 www.restaurantwarszawa.pl

2. Sala Bankietowa Elegance
   📞 +48 22 987 6543
   🌐 www.elegance.pl

3. Lounge & Dine
   📞 +48 22 555 1234
   🌐 www.loungedine.pl

──────────────────

🍰 Znalazłem cukiernie:

1. Słodkie Cuda
   📞 +48 22 111 2222
   🌐 www.slodkiecuda.pl

2. Tort Master
   📞 +48 22 333 4444
   🌐 www.tortmaster.pl

3. Cukiernia Królewska
   📞 +48 22 555 6666
   🌐 www.krolewska.pl

──────────────────

✅ Używam pierwszego z każdej listy do realizacji planu.
```

### Format dla Voice Agent (console):
```
═══════════════════════════════════════════════════════════════
VOICE AGENT TASK LIST
═══════════════════════════════════════════════════════════════

TASK ID: party-restaurant-001
─────────────────────────────────────────────────────────────

PLACES TO CALL:
  1. Restaurant Warszawa
     Phone: +48 22 123 4567

NOTES FOR AGENT:
  Dzwonisz do restauracji aby zarezerwować miejsce na imprezę 
  urodzinową. Dane kontaktowe organizatora: Mateusz Winiarek, 
  tel: +48 886 859 039.
  
  Szczegóły rezerwacji:
  - Data: 1 grudnia, godzina rozpoczęcia: 16:00
  - Czas trwania: około 5 godzin
  - Liczba osób: około 10
  - Menu: tradycyjna kuchnia polska
  - Dekoracje: proste dekoracje urodzinowe
  
  Jeśli restauracja nie ma wolnych miejsc na ten termin, zapytaj 
  o najbliższy możliwy termin. Na koniec potwierdź wszystkie 
  szczegóły rezerwacji.

═══════════════════════════════════════════════════════════════

TASK ID: party-bakery-001
─────────────────────────────────────────────────────────────

PLACES TO CALL:
  1. Słodkie Cuda
     Phone: +48 22 111 2222

NOTES FOR AGENT:
  Dzwonisz do cukierni aby zamówić tort urodzinowy.
  Dane kontaktowe organizatora: Mateusz Winiarek, 
  tel: +48 886 859 039.
  
  Szczegóły zamówienia:
  - Tort urodzinowy
  - Napis na torcie: "Wszystkiego najlepszego Ada"
  - Data odbioru: 1 grudnia
  
  Zapytaj o cenę i czy tort będzie gotowy na podany dzień.
  Potwierdź wszystkie szczegóły zamówienia.

═══════════════════════════════════════════════════════════════
Total Tasks: 2
Ready for Voice Agent: YES
═══════════════════════════════════════════════════════════════
```

## ✅ To-Do Lista

### Phase 1: Venue Search Implementation

- [ ] **Task 1.1: Create VenueSearcher Class**
  - [ ] Stwórz `backend/venue_searcher.py`
  - [ ] Implementuj `__init__` z LLMClient
  - [ ] Define search prompts

- [ ] **Task 1.2: Implement Search Methods**
  - [ ] `search_venues(location, query_type, count)` 
  - [ ] `search_bakeries(location, count)`
  - [ ] Use Google Search tool via LLMClient
  - [ ] Handle errors (no results, API errors)

- [ ] **Task 1.3: Implement Result Parsing**
  - [ ] `parse_search_results(llm_response)` → List[Venue]
  - [ ] Regex/parsing dla formatu "Nazwa - tel: X - www.Y"
  - [ ] Handle missing phone/website
  - [ ] Validation

- [ ] **Task 1.4: Implement Formatting**
  - [ ] `format_venues_for_user(venues)` → pretty string
  - [ ] Emoji, czytelny format
  - [ ] Numbered list

### Phase 2: Models & Storage

- [ ] **Task 2.1: Add Models**
  - [ ] `Venue` model w `models.py`
  - [ ] `VenueSearchResult` model
  - [ ] `TaskList` model (dla storage)
  - [ ] ✅ `Task` i `Place` już istnieją w `task.py`

- [ ] **Task 2.2: Storage for Tasks**
  - [ ] Stwórz folder `database/tasks/`
  - [ ] Extend `storage_manager.py`:
    - [ ] `save_task_list(tasks: List[Task], plan_id: str)`
    - [ ] `load_task_list(task_list_id: str) -> List[Task]`
    - [ ] `get_tasks_by_plan(plan_id: str) -> List[Task]`
  - [ ] Helper do konwersji Task → dict i dict → Task
  - [ ] JSON format: `database/tasks/{plan_id}.json`
  ```json
  {
    "plan_id": "conv-abc-plan-123",
    "created_at": "2025-11-29T...",
    "tasks": [
      {
        "task_id": "party-restaurant-abc",
        "notes_for_agent": "Dzwonisz do...",
        "places": [
          {"name": "Restaurant X", "phone": "+48..."}
        ]
      }
    ]
  }
  ```

### Phase 3: Task List Generation

- [ ] **Task 3.1: Implement Task Generator**
  - [ ] Metoda w `party_planner.py`: `generate_task_list()`
  - [ ] Parse action groups z planu
  - [ ] Match z venues/bakeries
  - [ ] Create `Task` objects (z `task.py`)
  - [ ] Build `notes_for_agent` jako single string
  - [ ] Include user info (name, phone) w notes

- [ ] **Task 3.2: Console Output**
  - [ ] `print_task_list(tasks: List[Task])` - pretty console output
  - [ ] Format zgodny z task.py structure
  - [ ] Show task_id, places, notes_for_agent
  - [ ] Readable formatting

- [ ] **Task 3.3: Venue Selection Logic**
  - [ ] Automatycznie wybierz pierwszy z listy (MVP)
  - [ ] Możliwość manual selection (future)
  - [ ] Map action groups → venues
  - [ ] Generate unique task_id dla każdego taska

### Phase 4: Integration with Party Flow

- [ ] **Task 4.1: Extend PlanState**
  - [ ] Add new state: `SEARCHING` (między GATHERING a COMPLETE)
  - [ ] Flow: GATHERING → SEARCHING → TASK_GENERATION → COMPLETE

- [ ] **Task 4.2: Modify PartyPlanner.process_request()**
  - [ ] Import: `from backend.task import Task, Place`
  - [ ] Po gathering complete:
    - [ ] Transition to SEARCHING
    - [ ] Trigger venue search
    - [ ] Display results to user
    - [ ] Trigger bakery search
    - [ ] Display results to user
    - [ ] Transition to TASK_GENERATION
    - [ ] Generate task list → List[Task]
    - [ ] Print to console (validation)
    - [ ] Save tasks to database
    - [ ] Transition to COMPLETE

- [ ] **Task 4.3: Update process_gathering()**
  - [ ] Gdy gathering complete:
    - [ ] Instead of COMPLETE → SEARCHING
    - [ ] Return searching message
    - [ ] Trigger searches in background

### Phase 5: Testing & Validation

- [ ] **Task 5.1: Test Web Search**
  - [ ] Test search_venues("Warszawa", "lokale", 3)
  - [ ] Validate results (phone numbers, websites)
  - [ ] Test error handling (no results)

- [ ] **Task 5.2: Test Full Flow**
  - [ ] Party request → plan → gathering → SEARCH → tasks
  - [ ] Validate venue results shown to user
  - [ ] Validate bakery results shown to user
  - [ ] Validate task list in console

- [ ] **Task 5.3: Test Task List Format**
  - [ ] Sprawdź czy console output ma dobry format
  - [ ] Wszystkie detale obecne (phone, instructions, user info)
  - [ ] Ready for voice agent

## 🔧 Technical Implementation Details

### 0. Task Serialization (dla JSON storage)

```python
from backend.task import Task, Place
from dataclasses import asdict

def task_to_dict(task: Task) -> dict:
    """Convert Task dataclass to dict for JSON storage"""
    return {
        "task_id": task.task_id,
        "notes_for_agent": task.notes_for_agent,
        "places": [
            {"name": place.name, "phone": place.phone}
            for place in task.places
        ]
    }

def dict_to_task(data: dict) -> Task:
    """Convert dict back to Task dataclass"""
    return Task(
        task_id=data["task_id"],
        notes_for_agent=data["notes_for_agent"],
        places=[
            Place(name=p["name"], phone=p["phone"])
            for p in data["places"]
        ]
    )
```

### 1. Search Prompt Design

```python
VENUE_SEARCH_PROMPT = """Znajdź 3 najlepsze {query_type} w {location} odpowiednie na imprezę urodzinową.

Dla każdego podaj:
- Nazwa lokalu
- Numer telefonu kontaktowy
- Strona www (jeśli dostępna)

WAŻNE:
- Tylko PRAWDZIWE, ISTNIEJĄCE miejsca
- Z aktualnymi numerami telefonów
- Lokale które przyjmują rezerwacje na imprezy

Format odpowiedzi (DOKŁADNIE w tej formie):
1. [Nazwa] - tel: [+48 XX XXX XXXX] - www.[strona]
2. [Nazwa] - tel: [+48 XX XXX XXXX] - www.[strona]
3. [Nazwa] - tel: [+48 XX XXX XXXX] - www.[strona]

Jeśli nie ma www, użyj: "brak strony"
"""
```

### 2. Parsing Strategy

```python
import re

def parse_search_results(text: str) -> List[Venue]:
    venues = []
    
    # Regex pattern: "1. Name - tel: +48... - www.example.com"
    pattern = r'(\d+)\.\s*(.+?)\s*-\s*tel:\s*([+\d\s]+)\s*-\s*(?:www\.)?(.+)'
    
    for match in re.finditer(pattern, text):
        number, name, phone, website = match.groups()
        
        venue = Venue(
            name=name.strip(),
            phone=phone.strip(),
            website=website.strip() if "brak" not in website.lower() else None,
            type="venue"  # or "bakery"
        )
        venues.append(venue)
    
    return venues
```

### 3. Task List Generation

```python
from backend.task import Task, Place

def generate_task_list(
    plan: PartyPlan,
    venue: Venue,
    bakery: Venue,
    user_info: dict
) -> List[Task]:
    """Generate tasks in format from task.py"""
    tasks = []
    
    # Parse plan to extract action groups
    action_groups = plan.action_groups  # List[ActionGroup]
    
    for i, group in enumerate(action_groups):
        # Determine recipient
        if "lokal" in group.target.lower() or "restaurac" in group.target.lower():
            place = venue
            task_id = f"party-restaurant-{str(uuid.uuid4())[:8]}"
        elif "cukierni" in group.target.lower():
            place = bakery
            task_id = f"party-bakery-{str(uuid.uuid4())[:8]}"
        else:
            continue
        
        # Build notes_for_agent as single string
        notes = f"Dzwonisz do {place.name} w sprawie imprezy urodzinowej.\n"
        notes += f"Dane kontaktowe organizatora: {user_info['full_name']}, "
        notes += f"tel: {user_info['phone']}.\n\n"
        notes += "Szczegóły:\n"
        
        for instruction in group.instructions:
            notes += f"- {instruction.description}\n"
        
        notes += "\nJeśli nie ma dostępności na podany termin, "
        notes += "zapytaj o najbliższy możliwy. "
        notes += "Na koniec potwierdź wszystkie szczegóły."
        
        task = Task(
            task_id=task_id,
            notes_for_agent=notes,
            places=[Place(name=place.name, phone=place.phone)]
        )
        tasks.append(task)
    
    return tasks
```

### 4. Console Output

```python
from backend.task import Task

def print_task_list_to_console(tasks: List[Task]):
    """Print beautifully formatted task list to console"""
    
    width = 70
    print("\n" + "═" * width)
    print("VOICE AGENT TASK LIST")
    print("═" * width)
    
    for task in tasks:
        print(f"\nTASK ID: {task.task_id}")
        print("─" * width)
        
        print("\nPLACES TO CALL:")
        for i, place in enumerate(task.places, 1):
            print(f"  {i}. {place.name}")
            print(f"     Phone: {place.phone}")
        
        print("\nNOTES FOR AGENT:")
        # Format notes with proper indentation
        for line in task.notes_for_agent.split('\n'):
            print(f"  {line}")
        
        print()
    
    print("═" * width)
    print(f"Total Tasks: {len(tasks)}")
    print(f"Ready for Voice Agent: YES")
    print("═" * width + "\n")
```

## 🎨 User Experience (Chat)

### Search In Progress:
```
AI: ✅ Mam wszystkie dane!

🔍 Szukam lokali w Warszawie...
```

### Venues Found:
```
AI: 🏢 Znalazłem lokale:

1. Restaurant Warszawa
   📞 +48 22 123 4567
   🌐 www.restaurantwarszawa.pl

2. Sala Bankietowa Elegance
   📞 +48 22 987 6543
   🌐 www.elegance.pl

3. Lounge & Dine
   📞 +48 22 555 1234
   🌐 www.loungedine.pl
```

### Bakeries Found:
```
AI: 🍰 Szukam cukierni...

Znalazłem cukiernie:

1. Słodkie Cuda
   📞 +48 22 111 2222
   🌐 www.slodkiecuda.pl

2. Tort Master
   📞 +48 22 333 4444
   🌐 www.tortmaster.pl

3. Cukiernia Królewska
   📞 +48 22 555 6666
   🌐 www.krolewska.pl
```

### Task List Confirmation:
```
AI: ✅ Używam pierwszego z każdej listy do realizacji.

📋 Przygotowałem listę zadań dla voice agenta:
- Połączenie z Restaurant Warszawa
- Połączenie z Słodkie Cuda

Szczegóły wyświetlone w konsoli backendu.

🎉 Wszystko gotowe do wykonania!
```

## 🔄 Updated State Machine

```
INITIAL
  ↓
PLANNING (generate plan)
  ↓
REFINEMENT (user modifies)
  ↓
CONFIRMED
  ↓
GATHERING (collect user info)
  ↓
SEARCHING (NEW! - find venues & bakeries)
  ↓
TASK_GENERATION (NEW! - create voice tasks)
  ↓
COMPLETE
```

## 📊 Data Flow

```
1. User confirms plan
   ↓
2. Gather contact info (name, phone, location)
   ↓
3. Extract location from gathered_info
   ↓
4. VenueSearcher.search_venues(location, "lokale", 3)
   ↓
5. Parse results → List[Venue]
   ↓
6. Format & display to user
   ↓
7. VenueSearcher.search_bakeries(location, 3)
   ↓
8. Parse results → List[Venue]
   ↓
9. Format & display to user
   ↓
10. Select venues (first from each list)
   ↓
11. generate_task_list(plan, venue, bakery, user_info)
    → List[Task] (from task.py)
   ↓
12. print_task_list_to_console(tasks: List[Task])
    → Pretty console output
   ↓
13. Convert tasks to dict: [task_to_dict(t) for t in tasks]
   ↓
14. Save to database/tasks/{plan_id}.json
   ↓
15. Return success message to user
   ↓
16. [FUTURE] Voice agent reads tasks and makes calls
```

## 🚧 Challenges & Solutions

### Challenge 1: Web Search Quality
**Problem:** Google Search może nie zwrócić telefonów  
**Solution:** Prompt explicitly asks for phone numbers + validation

### Challenge 2: Parsing Variability
**Problem:** LLM może zwrócić różne formaty  
**Solution:** Very strict format in prompt + robust regex parsing

### Challenge 3: No Results
**Problem:** Brak wyników dla małych miast  
**Solution:** Fallback message + ask user for manual input (future)

### Challenge 4: Action Group Parsing
**Problem:** Trzeba zmapować action groups → venues  
**Solution:** Simple keyword matching ("lokal" → venue, "cukierni" → bakery)

## 📋 File Changes Summary

### New Files:
1. `backend/venue_searcher.py` - venue search logic
2. `database/tasks/` - task storage folder

### Modified Files:
1. `backend/models.py` - add `Venue`, `VenueSearchResult`, `TaskList` (dla storage)
2. `backend/storage_manager.py` - add task storage methods
3. `backend/party_planner.py` - integrate search flow, task generation
4. `backend/chat_service.py` - handle new state (SEARCHING, TASK_GENERATION)

### Existing Files (używamy bez zmian):
1. `backend/task.py` - ✅ Format `Task` i `Place` już istnieje!

## 🎯 Success Criteria

✅ Web search znajduje 3 lokale  
✅ Web search znajduje 3 cukiernie  
✅ Wyniki pokazane użytkownikowi w chacie (nazwa, telefon, www)  
✅ Task list wygenerowany (List[Task] z task.py)  
✅ Task list wyświetlony w konsoli (readable format)  
✅ Task list zapisany do database/tasks/{plan_id}.json  
✅ Task objects zawierają:
  - task_id (unique)
  - notes_for_agent (pełne instrukcje + user info)
  - places (nazwa + telefon)
✅ Format gotowy dla voice agenta  

## ⏱️ Estimated Time

- **Phase 1** (Venue Search): 2-3 godziny
- **Phase 2** (Models & Storage): 1 godzina
- **Phase 3** (Task Generation): 2 godziny
- **Phase 4** (Integration): 1 godzina
- **Phase 5** (Testing): 1 godzina

**Total MVP: ~7-8 godzin**

## 🔮 Future Enhancements

- [ ] User może wybrać które venue/bakery (nie zawsze pierwszy)
- [ ] Caching search results (nie szukać ponownie)
- [ ] Rating/reviews w search results
- [ ] Map integration (show on map)
- [ ] Save search history
- [ ] Retry search if poor results

---

**Status:** 📋 Ready to Implement  
**Priority:** 🔥 High (needed for voice agent)  
**Complexity:** 🟡 Medium (web search + parsing)  
**Dependencies:** LLMClient (Google Search), PartyPlanner, Models


