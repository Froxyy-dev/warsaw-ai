"""
Party Planner - Multi-step party planning with iterative refinement
"""
import re
import json
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import uuid

from llm_client import LLMClient
from information_gatherer import InformationGatherer
from models import PlanState
from venue_searcher import VenueSearcher
from task import Task, Place

logger = logging.getLogger(__name__)


class PartyPlanner:
    """
    Multi-step party planning with iterative refinement
    
    Flow:
    1. INITIAL: User describes party needs
    2. PLANNING: Generate initial plan
    3. REFINEMENT: User provides feedback, modify plan
    4. CONFIRMED: User confirms plan
    5. GATHERING: Collect contact details
    6. EXECUTING: Execute actions (calls, reservations)
    7. COMPLETE: Done
    """
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self.state = PlanState.INITIAL
        self.current_plan = None
        self.user_request = None
        self.feedback_history = []
        self.gathered_info = {}
        self.info_gatherer = None
        self.venue_searcher = VenueSearcher(model=model)
        self.found_venues = []
        self.found_bakeries = []
        self.generated_tasks = []
        
        # Prompts
        self.plan_generation_prompt = """Tworzysz KRÓTKIE plany do wykonania przez voice agenta. Bądź zwięzły!

Request: "{user_request}"

ZASADY (KRYTYCZNE - CZYTANE PRZEZ TELEFON!):
1. MAX 4-5 instrukcji na grupę (voice agent musi to przeczytać!)
2. Każda instrukcja MAX 10 słów
3. Format: "Zadzwonić do [miejsce] z następującymi instrukcjami:"
4. Tylko essentials: data, godzina, liczba osób, główne wymagania
5. BEZ gadania, BEZ oczywistości, TYLKO fakty

DOBRY przykład (krótki):
Zadzwonić do lokalu z salami z następującymi instrukcjami:
- Rezerwacja: [data], [godzina], [czas trwania]
- Liczba osób: [X]
- Dekoracje urodzinowe
- Menu na imprezę
- Tort urodzinowy

ZŁY przykład (za długi):
- "Zarezerwuj salę lub odpowiednią przestrzeń na imprezę urodzinową dla Twojej dziewczyny..." ❌

Odpowiedź (pisz bez nawiasów kwadratowych):
Oto plan dla Twojej imprezy:

Zadzwonić do [miejsce] z następującymi instrukcjami:
- [instrukcja 1]
- [instrukcja 2]

Czy chcesz coś zmienić czy zatwierdzasz?"""

        self.plan_refinement_prompt = """Aktualizuj plan według feedbacku. KRÓTKO! To czyta voice agent przez telefon.

PLAN:
{current_plan}

FEEDBACK:
"{user_feedback}"

ZASADY:
1. MAX 4-5 instrukcji na grupę (voice agent czyta!)
2. Każda instrukcja MAX 10 słów
3. Jeśli przenosi coś (np. tort → cukiernia): stwórz nową grupę
4. Jeśli dodaje szczegół: dodaj KRÓTKO
5. BEZ gadania, TYLKO fakty

Odpowiedź (pisz bez nawiasów kwadratowych, oddzielaj grupy pustą linią):
Oto zaktualizowany plan:

Zadzwonić do [miejsce 1] z następującymi instrukcjami:
- [instrukcja]

Zadzwonić do [miejsce 2] z następującymi instrukcjami (jeśli potrzebne):
- [instrukcja]

Czy chcesz coś zmienić czy zatwierdzasz?"""

        self.info_gathering_prompt = """Zbierasz dane do rezerwacji. Pytaj KRÓTKO (max 5 słów).

ORIGINAL REQUEST (wyciągnij wszystko!):
"{original_request}"

PLAN:
{plan}

ANALIZA - co już MASZ z original request:
1. "w Warszawie" / "w [miasto]" → location="Warszawa"
2. "16:00" / "o godzinie X" → time="16:00"  
3. "pojutrze" / "1 grudnia" → date="1 grudnia" (DATA IMPREZY!)
4. "10 osób" / "na X osób" → guests="10"
5. "5 godzin" / "potrwa X" → duration="5 godzin"

WAŻNE:
- "pojutrze urodziny" → date to DATA IMPREZY (oblicz pojutrze!)
- NIE PYTAJ o datę urodzin - potrzebujesz datę IMPREZY!

Pytaj TYLKO o brakujące:
- full_name (do rezerwacji)
- phone (kontaktowy)

NIE PYTAJ jeśli jest w original request!

Gdy masz WSZYSTKO, zwróć JSON (włącz dane z original):
```json
{{
    "full_name": "...",
    "phone": "...",
    "date": "...",
    "time": "...",
    "location": "...",
    "guests": "...",
    "duration": "..."
}}
```"""
    
    def is_party_request(self, content: str) -> bool:
        """Detect if message is a party planning request"""
        keywords = [
            "imprez", "urodziny", "przyjęcie", "celebration",
            "zorganizuj", "party", "event", "spotkanie",
            "świętowanie", "rocznica", "jubileusz"
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    def is_confirmation(self, content: str) -> bool:
        """Detect if user is confirming the plan"""
        confirmations = [
            "potwierdzam", "ok", "tak", "zgoda", "zatwierdź", "zatwierdzam",
            "confirm", "yes", "dobra", "super", "git", "okey"
        ]
        content_lower = content.lower()
        return any(conf in content_lower for conf in confirmations)
    
    def is_modification_request(self, content: str) -> bool:
        """Detect if user wants to modify the plan"""
        modifications = [
            "zmień", "zmiana", "zmiany", "popraw", "modyfikuj", "dostosuj",
            "chcę", "chciałbym", "chcialbym", "chciałabym",
            "dodaj", "usuń", "zamień", "nie",
            "jako", "żeby", "zeby", "zamiast",
            "lepiej", "wolę", "wole", "preferuję", "preferuje"
        ]
        content_lower = content.lower()
        return any(mod in content_lower for mod in modifications)
    
    async def generate_plan(self, user_request: str) -> str:
        """Generate initial party plan based on user request (ASYNC)"""
        logger.info(f"Generating plan for: {user_request}")
        
        try:
            # Create LLM client
            prompt = self.plan_generation_prompt.format(user_request=user_request)
            llm_client = LLMClient(model=self.model)
            
            # ✅ ASYNC call - won't block!
            logger.info("🔄 Calling LLM to generate plan...")
            response = await llm_client.send_async(prompt)
            logger.info("✅ Plan generated successfully")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Failed to generate plan: {e}", exc_info=True)
            return f"Przepraszam, nie udało się wygenerować planu: {str(e)}"
    
    async def refine_plan(self, current_plan: str, feedback: str) -> str:
        """Refine existing plan based on user feedback"""
        logger.info(f"Refining plan with feedback: {feedback}")
        
        try:
            # Create LLM client
            prompt = self.plan_refinement_prompt.format(
                current_plan=current_plan,
                user_feedback=feedback
            )
            llm_client = LLMClient(model=self.model)
            
            # ✅ ASYNC call - won't block!
            logger.info("🔄 Calling LLM to refine plan...")
            response = await llm_client.send_async(prompt)
            logger.info("✅ Plan refined successfully")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Failed to refine plan: {e}", exc_info=True)
            return f"Przepraszam, nie udało się zaktualizować planu: {str(e)}"
    
    async def start_gathering(self, plan: str) -> str:
        """Start information gathering phase"""
        logger.info("Starting information gathering phase")
        
        # Create InformationGatherer with custom prompt including original request
        gathering_prompt = self.info_gathering_prompt.format(
            plan=plan,
            original_request=self.user_request or "brak"
        )
        self.info_gatherer = InformationGatherer(model=self.model)
        self.info_gatherer.system_prompt = gathering_prompt
        self.info_gatherer.llm_client = LLMClient(
            model=self.model,
            system_instruction=gathering_prompt
        )
        
        self.state = PlanState.GATHERING
        
        # Get first question from gatherer (sync OK here - initialization)
        first_question = self.info_gatherer.process_message("Zacznij zbieranie danych")
        
        return f"""✅ Plan zatwierdzony!

📝 Teraz potrzebuję kilku danych do realizacji...

{first_question['text']}"""
    
    async def process_gathering(self, user_input: str) -> Tuple[str, bool]:
        """
        Process user input during gathering phase (ASYNC non-blocking)
        
        Returns:
            (response, is_complete)
        """
        if not self.info_gatherer:
            return "Błąd: Brak aktywnego zbierania danych", False
        
        # ✅ ASYNC call - won't block event loop
        result = await self.info_gatherer.process_message_async(user_input)
        
        if result["type"] == "complete":
            # Gathering complete - transition to SEARCHING
            # Return just completion message, the rest will be handled by chat_service
            self.gathered_info = result["data"]
            self.state = PlanState.SEARCHING
            
            response = "✅ Świetnie! Mam wszystkie potrzebne dane.\n\n🔍 Zaczynam wyszukiwanie..."
            
            return response, True
        else:
            # Continue gathering
            return result["text"], False
    
    async def process_request(self, user_input: str) -> str:
        """
        Main processing method - handles state machine
        
        Args:
            user_input: User's message
            
        Returns:
            Response to user
        """
        logger.info(f"🟢 party_planner.process_request() STARTED")
        logger.info(f"   Current state: {self.state}")
        logger.info(f"   User input: {user_input[:100]}...")
        
        try:
            # INITIAL state - first message, generate plan
            if self.state == PlanState.INITIAL:
                logger.info(f"   📝 State: INITIAL - generating plan...")
                self.user_request = user_input
                logger.info(f"   ⏳ Calling generate_plan()...")
                self.current_plan = await self.generate_plan(user_input)
                logger.info(f"   ✅ Plan generated, length: {len(self.current_plan)}")
                self.state = PlanState.PLANNING
                logger.info(f"   ✅ State changed to: PLANNING")
                return self.current_plan
            
            # PLANNING or REFINEMENT - user is reviewing plan
            elif self.state in [PlanState.PLANNING, PlanState.REFINEMENT]:
                # Check if user confirms
                if self.is_confirmation(user_input):
                    self.state = PlanState.CONFIRMED
                    return await self.start_gathering(self.current_plan)
                
                # Default: treat as modification (more user-friendly)
                # User is probably giving feedback unless explicitly confirming
                else:
                    self.feedback_history.append(user_input)
                    self.current_plan = await self.refine_plan(
                        self.current_plan, 
                        user_input
                    )
                    self.state = PlanState.REFINEMENT
                    return self.current_plan
            
            # GATHERING - collecting contact info
            elif self.state == PlanState.GATHERING:
                logger.info(f"   📝 State: GATHERING - processing user input...")
                logger.info(f"   ⏳ Calling process_gathering()...")
                response, is_complete = await self.process_gathering(user_input)
                logger.info(f"   ✅ process_gathering() returned")
                logger.info(f"   Is complete: {is_complete}")
                logger.info(f"   Response: {response[:100]}...")
                return response
            
            # SEARCHING - finding venues (auto-executed after gathering)
            elif self.state == PlanState.SEARCHING:
                # This state is handled automatically, but if user sends message
                # during this phase, we process it
                return "🔍 Wyszukuję miejsca, proszę czekać..."
            
            # TASK_GENERATION - creating voice agent tasks
            elif self.state == PlanState.TASK_GENERATION:
                # This state is also auto-executed
                # User shouldn't normally be here, but handle it gracefully
                return "📋 Tworzę listę zadań, proszę czekać..."
            
            # COMPLETE - done
            elif self.state == PlanState.COMPLETE:
                return "Plan jest już zakończony! Możesz rozpocząć nową konwersację jeśli chcesz zaplanować coś innego."
            
            else:
                return f"Nieznany stan: {self.state}"
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"Przepraszam, wystąpił błąd: {str(e)}"
    
    async def search_venues_only(self) -> str:
        """
        Search for venues only (first step) - ASYNC non-blocking
        
        Returns:
            Response message with venue results
        """
        try:
            location = self.gathered_info.get("location", "Warszawa")
            logger.info(f"🔍 Searching for venues in {location}")
            
            # ✅ ASYNC call with await
            venue_results = await self.venue_searcher.search_venues(
                location=location,
                query_type="lokale z salami/restauracje",
                count=3
            )
            self.found_venues = venue_results.venues
            
            # Format results for user
            if self.found_venues:
                response = self.venue_searcher.format_venues_for_user(
                    self.found_venues,
                    title="Lokale w " + location
                )
            else:
                response = "❌ Nie znalazłem lokali."
            
            logger.info(f"✅ Found {len(self.found_venues)} venues")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error during venue search: {e}", exc_info=True)
            return f"❌ Błąd podczas wyszukiwania lokali: {str(e)}"
    
    async def search_bakeries_only(self) -> str:
        """
        Search for bakeries only (second step) - ASYNC non-blocking
        
        Returns:
            Response message with bakery results
        """
        try:
            location = self.gathered_info.get("location", "Warszawa")
            logger.info(f"🔍 Searching for bakeries in {location}")
            
            # ✅ ASYNC call with await
            bakery_results = await self.venue_searcher.search_bakeries(
                location=location,
                count=3
            )
            self.found_bakeries = bakery_results.venues
            
            # Format results for user
            if self.found_bakeries:
                response = self.venue_searcher.format_venues_for_user(
                    self.found_bakeries,
                    title="Cukiernie w " + location
                )
            else:
                response = "❌ Nie znalazłem cukierni."
            
            logger.info(f"✅ Found {len(self.found_bakeries)} bakeries")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error during bakery search: {e}", exc_info=True)
            return f"❌ Błąd podczas wyszukiwania cukierni: {str(e)}"
    
    async def generate_and_save_tasks(self) -> str:
        """
        Generate task list and save to storage (final step)
        
        Returns:
            Response message with task generation result
        """
        try:
            logger.info("📋 Generating task list...")
            
            # Generate tasks
            tasks = self.generate_task_list()
            
            if tasks:
                # Print to console for validation
                self.print_task_list_to_console(tasks)
                
                # Save tasks to storage
                from storage_manager import storage_manager
                plan_id = f"plan-{str(uuid.uuid4())[:8]}"
                conversation_id = self.gathered_info.get("conversation_id", "")
                storage_manager.save_task_list(tasks, plan_id, conversation_id)
                logger.info(f"Saved {len(tasks)} tasks to storage (plan_id: {plan_id})")
                
                # ⭐ Save plan_id for later retrieval
                self.gathered_info["plan_id"] = plan_id
                
                # ❌ COMMENTED OUT - user doesn't want these verbose messages
                # response = f"✅ Lista zadań gotowa! Przygotowano {len(tasks)} zadań.\n"
                # response += "📋 Szczegóły wyświetlone w konsoli backendu.\n\n"
                # response += "📞 Rozpoczynam wykonywanie zadań..."
                
                # ⭐ Transition to EXECUTING (not COMPLETE - we'll execute now!)
                self.state = PlanState.EXECUTING
                return ""  # Return empty string - chat_service will handle voice agent messages
            else:
                return "❌ Nie udało się wygenerować zadań."
            
        except Exception as e:
            logger.error(f"Error generating tasks: {e}")
            return f"❌ Błąd podczas generowania zadań: {str(e)}"
    
    def generate_task_list(self) -> List[Task]:
        """
        Generate task list for voice agent
        
        Returns:
            List of Task objects (from task.py)
            Each task contains ALL venues/bakeries as fallback options
        """
        try:
            tasks = []
            user_info = self.gathered_info
            
            # Parse plan to find what needs to be done
            has_venue_task = self.found_venues and ("lokal" in self.current_plan.lower() or "restaurac" in self.current_plan.lower())
            has_bakery_task = self.found_bakeries and "cukierni" in self.current_plan.lower()
            
            # Generate venue task with ALL venues (fallback if first is unavailable)
            if has_venue_task:
                venue_task = self._create_venue_task(self.found_venues, user_info)
                tasks.append(venue_task)
            
            # Generate bakery task with ALL bakeries (fallback if first is unavailable)
            if has_bakery_task:
                bakery_task = self._create_bakery_task(self.found_bakeries, user_info)
                tasks.append(bakery_task)
            
            self.generated_tasks = tasks
            logger.info(f"Generated {len(tasks)} tasks (with {len(self.found_venues) + len(self.found_bakeries)} total places)")
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error generating task list: {e}")
            return []
    
    def _create_venue_task(self, venues: List, user_info: dict) -> Task:
        """
        Create a task for calling venues (with multiple fallback options)
        
        Args:
            venues: List of Venue objects (all will be added as Places)
            user_info: User contact information
        """
        task_id = f"party-restaurant-{str(uuid.uuid4())[:8]}"
        
        # Build notes_for_agent (same instructions for ALL venues)
        notes = "Dzwonisz do lokalu/restauracji aby zarezerwować miejsce na imprezę urodzinową.\n"
        notes += f"Dane kontaktowe organizatora: {user_info.get('full_name', 'brak')}, "
        notes += f"tel: {user_info.get('phone', 'brak')}.\n\n"
        notes += "Szczegóły rezerwacji:\n"
        
        # Extract details from gathered info
        if 'date' in user_info:
            notes += f"- Data: {user_info['date']}\n"
        if 'time' in user_info:
            notes += f"- Godzina rozpoczęcia: {user_info['time']}\n"
        if 'duration' in user_info:
            notes += f"- Czas trwania: około {user_info['duration']}\n"
        if 'guests' in user_info:
            notes += f"- Liczba osób: około {user_info['guests']}\n"
        
        # Parse plan for additional details
        if "menu" in self.current_plan.lower() and "polska" in self.current_plan.lower():
            notes += "- Menu: tradycyjna kuchnia polska\n"
        if "dekorac" in self.current_plan.lower():
            notes += "- Dekoracje: proste dekoracje urodzinowe\n"
        
        notes += "\nJeśli ten lokal nie ma wolnych miejsc, spróbuj kolejny z listy. "
        notes += "Na koniec potwierdź wszystkie szczegóły rezerwacji."
        
        # Create Places list with ALL venues (fallback options)
        places = [Place(name=v.name, phone=v.phone) for v in venues]
        
        return Task(
            task_id=task_id,
            notes_for_agent=notes,
            places=places
        )
    
    def _create_bakery_task(self, bakeries: List, user_info: dict) -> Task:
        """
        Create a task for calling bakeries (with multiple fallback options)
        
        Args:
            bakeries: List of Venue objects (all will be added as Places)
            user_info: User contact information
        """
        task_id = f"party-bakery-{str(uuid.uuid4())[:8]}"
        
        # Build notes_for_agent (same instructions for ALL bakeries)
        notes = "Dzwonisz do cukierni aby zamówić tort urodzinowy.\n"
        notes += f"Dane kontaktowe organizatora: {user_info.get('full_name', 'brak')}, "
        notes += f"tel: {user_info.get('phone', 'brak')}.\n\n"
        notes += "Szczegóły zamówienia:\n"
        notes += "- Tort urodzinowy\n"
        
        # Look for cake message in plan
        if "napis" in self.current_plan.lower():
            # Try to extract the message
            match = re.search(r'[Nn]apis[:\s]*["\'](.+?)["\']', self.current_plan)
            if match:
                notes += f"- Napis na torcie: \"{match.group(1)}\"\n"
        
        if 'date' in user_info:
            notes += f"- Data odbioru: {user_info['date']}\n"
        
        notes += "\nJeśli ta cukiernia nie może zrealizować zamówienia, spróbuj kolejną z listy. "
        notes += "Zapytaj o cenę i czy tort będzie gotowy na podany dzień. "
        notes += "Potwierdź wszystkie szczegóły zamówienia."
        
        # Create Places list with ALL bakeries (fallback options)
        places = [Place(name=b.name, phone=b.phone) for b in bakeries]
        
        return Task(
            task_id=task_id,
            notes_for_agent=notes,
            places=places
        )
    
    def print_task_list_to_console(self, tasks: List[Task]):
        """
        Print beautifully formatted task list to console
        
        Args:
            tasks: List of Task objects
        """
        width = 70
        print("\n" + "═" * width)
        print("VOICE AGENT TASK LIST".center(width))
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
        print(f"Total Tasks: {len(tasks)}".center(width))
        print(f"Ready for Voice Agent: YES".center(width))
        print("═" * width + "\n")
    
    def reset(self):
        """Reset planner to initial state"""
        self.state = PlanState.INITIAL
        self.current_plan = None
        self.user_request = None
        self.feedback_history = []
        self.gathered_info = {}
        self.info_gatherer = None
        self.found_venues = []
        self.found_bakeries = []
        self.generated_tasks = []
        logger.info("PartyPlanner reset to initial state")


# Global instance (for testing)
party_planner = PartyPlanner()

