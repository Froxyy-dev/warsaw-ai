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
        
        # Prompts
        self.plan_generation_prompt = """Jesteś profesjonalnym organizatorem imprez i wydarzeń.

Użytkownik chce: "{user_request}"

Wygeneruj szczegółowy plan imprezy zawierający:
- Wszystkie konieczne rezerwacje (sala, miejsce)
- Zamówienia (tort, dekoracje, catering)
- Dodatkowe usługi i szczegóły

Format planu (WAŻNE - użyj dokładnie tego formatu):
📋 PLAN IMPREZY

1. 🏢 [Nazwa zadania]
   • [Szczegół 1]
   • [Szczegół 2]
   • [Szczegół 3]

2. 🎂 [Nazwa zadania]
   • [Szczegół 1]
   • [Szczegół 2]

(etc...)

─────────────────────────
💬 Czy chcesz coś dostosować czy potwierdzasz plan?"""

        self.plan_refinement_prompt = """Jesteś profesjonalnym organizatorem imprez.

AKTUALNY PLAN:
{current_plan}

FEEDBACK UŻYTKOWNIKA:
"{user_feedback}"

Zaktualizuj plan według feedbacku użytkownika. Zachowaj ten sam format:
📋 PLAN IMPREZY

1. 🏢 [Nazwa zadania]
   • [Szczegóły]

(etc...)

─────────────────────────
💬 Czy chcesz coś dostosować czy potwierdzasz plan?"""

        self.info_gathering_prompt = """Jesteś asystentem zbierającym dane potrzebne do zrealizowania planu imprezy.

ZATWIERDZONY PLAN:
{plan}

Musisz zebrać następujące informacje od użytkownika:
- Imię i nazwisko (do rezerwacji)
- Numer telefonu kontaktowy
- Dokładna data wydarzenia (jeśli nie podana)
- Dokładna godzina wydarzenia (jeśli nie podana)
- Adres/lokalizacja (jeśli potrzebna)

Pytaj o każdą informację po kolei w przyjazny sposób.
NIE pytaj o to co już masz.

Gdy zbierzesz WSZYSTKIE potrzebne informacje, zwróć TYLKO ten blok JSON:
```json
{{
    "full_name": "...",
    "phone": "...",
    "date": "...",
    "time": "...",
    "location": "..."
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
            "potwierdzam", "ok", "tak", "zgoda", "zatwierdź",
            "confirm", "yes", "dobra", "super", "git"
        ]
        content_lower = content.lower()
        return any(conf in content_lower for conf in confirmations)
    
    def is_modification_request(self, content: str) -> bool:
        """Detect if user wants to modify the plan"""
        modifications = [
            "zmień", "zmiana", "popraw", "modyfikuj", "dostosuj",
            "chcę", "dodaj", "usuń", "zamień", "nie"
        ]
        content_lower = content.lower()
        return any(mod in content_lower for mod in modifications)
    
    async def generate_plan(self, user_request: str) -> str:
        """Generate initial party plan based on user request"""
        logger.info(f"Generating plan for: {user_request}")
        
        try:
            # Create LLM client
            prompt = self.plan_generation_prompt.format(user_request=user_request)
            llm_client = LLMClient(model=self.model)
            
            # Generate plan
            response = llm_client.send(prompt)
            
            logger.info("Plan generated successfully")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
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
            
            # Generate refined plan
            response = llm_client.send(prompt)
            
            logger.info("Plan refined successfully")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to refine plan: {e}")
            return f"Przepraszam, nie udało się zaktualizować planu: {str(e)}"
    
    async def start_gathering(self, plan: str) -> str:
        """Start information gathering phase"""
        logger.info("Starting information gathering phase")
        
        # Create InformationGatherer with custom prompt
        gathering_prompt = self.info_gathering_prompt.format(plan=plan)
        self.info_gatherer = InformationGatherer(model=self.model)
        self.info_gatherer.system_prompt = gathering_prompt
        self.info_gatherer.llm_client = LLMClient(
            model=self.model,
            system_instruction=gathering_prompt
        )
        
        self.state = PlanState.GATHERING
        
        # Get first question from gatherer
        first_question = self.info_gatherer.process_message("Zacznij zbieranie danych")
        
        return f"""✅ Plan zatwierdzony!

📝 Teraz potrzebuję kilku danych do realizacji...

{first_question['text']}"""
    
    def process_gathering(self, user_input: str) -> Tuple[str, bool]:
        """
        Process user input during gathering phase
        
        Returns:
            (response, is_complete)
        """
        if not self.info_gatherer:
            return "Błąd: Brak aktywnego zbierania danych", False
        
        result = self.info_gatherer.process_message(user_input)
        
        if result["type"] == "complete":
            # Gathering complete
            self.gathered_info = result["data"]
            self.state = PlanState.COMPLETE
            
            response = f"""✅ Świetnie! Mam wszystkie potrzebne dane:

📋 Podsumowanie:
"""
            for key, value in self.gathered_info.items():
                response += f"• {key}: {value}\n"
            
            response += "\n🎉 Plan imprezy jest gotowy do realizacji!"
            
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
        logger.info(f"Processing request in state: {self.state}")
        
        try:
            # INITIAL state - first message, generate plan
            if self.state == PlanState.INITIAL:
                self.user_request = user_input
                self.current_plan = await self.generate_plan(user_input)
                self.state = PlanState.PLANNING
                return self.current_plan
            
            # PLANNING or REFINEMENT - user is reviewing plan
            elif self.state in [PlanState.PLANNING, PlanState.REFINEMENT]:
                # Check if user confirms
                if self.is_confirmation(user_input):
                    self.state = PlanState.CONFIRMED
                    return await self.start_gathering(self.current_plan)
                
                # Check if user wants modifications
                elif self.is_modification_request(user_input):
                    self.feedback_history.append(user_input)
                    self.current_plan = await self.refine_plan(
                        self.current_plan, 
                        user_input
                    )
                    self.state = PlanState.REFINEMENT
                    return self.current_plan
                
                else:
                    # Unclear response, ask for clarification
                    return """Nie jestem pewien czy chcesz zatwierdzić plan czy go zmienić. 

Możesz powiedzieć:
- "Potwierdzam" - jeśli plan jest OK
- Opisz zmiany - jeśli chcesz coś zmienić"""
            
            # GATHERING - collecting contact info
            elif self.state == PlanState.GATHERING:
                response, is_complete = self.process_gathering(user_input)
                return response
            
            # COMPLETE - done
            elif self.state == PlanState.COMPLETE:
                return "Plan jest już zakończony! Możesz rozpocząć nową konwersację jeśli chcesz zaplanować coś innego."
            
            else:
                return f"Nieznany stan: {self.state}"
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"Przepraszam, wystąpił błąd: {str(e)}"
    
    def reset(self):
        """Reset planner to initial state"""
        self.state = PlanState.INITIAL
        self.current_plan = None
        self.user_request = None
        self.feedback_history = []
        self.gathered_info = {}
        self.info_gatherer = None
        logger.info("PartyPlanner reset to initial state")


# Global instance (for testing)
party_planner = PartyPlanner()

