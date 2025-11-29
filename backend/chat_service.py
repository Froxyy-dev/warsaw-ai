"""
Chat Service for handling chat conversations with LLM integration.
Manages context, processes messages, and generates AI responses.
"""
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from llm_client import LLMClient
from models import Message, MessageRole, Conversation, PartyPlan, PlanState
from storage_manager import storage_manager
from party_planner import PartyPlanner

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat conversations with AI"""
    
    def __init__(self, max_context_messages: int = 20):
        """
        Initialize chat service.
        
        Args:
            max_context_messages: Maximum number of messages to include in context window
        """
        self.max_context_messages = max_context_messages
        self.party_planner = PartyPlanner()
        self.active_plans = {}  # conversation_id -> PartyPlan
        self.conversation_locks = {}  # conversation_id -> asyncio.Lock
        self.system_prompt = """Jesteś pomocnym asystentem AI dla systemu umawiania wizyt i połączeń telefonicznych.
Możesz pomóc użytkownikom w:
- Umawianiu wizyt
- Sprawdzaniu statusu połączeń
- Zarządzaniu terminarzem
- Odpowiadaniu na pytania o system

Odpowiadaj w sposób profesjonalny, przyjazny i konkretny."""
    
    def _create_llm_client(self, conversation_history: List[Message]) -> LLMClient:
        """
        Create a new LLM client with conversation context.
        
        Args:
            conversation_history: List of previous messages for context
        """
        # Create new LLM client
        client = LLMClient()
        
        # Build context from conversation history
        # Take only the last N messages to stay within context window
        context_messages = conversation_history[-self.max_context_messages:]
        
        # If there's history, send it to establish context
        if context_messages:
            # Build context string
            context = "Poprzednia konwersacja:\n\n"
            for msg in context_messages:
                role = "Użytkownik" if msg.role == MessageRole.USER else "Asystent"
                context += f"{role}: {msg.content}\n\n"
            
            # Send system prompt with context
            try:
                client.send(f"{self.system_prompt}\n\n{context}")
            except Exception as e:
                logger.error(f"Failed to set context: {e}")
        else:
            # Just send system prompt for new conversations
            try:
                client.send(self.system_prompt)
            except Exception as e:
                logger.error(f"Failed to send system prompt: {e}")
        
        return client
    
    async def process_user_message(
        self, 
        conversation_id: str, 
        content: str
    ) -> tuple[Message, Message]:
        """
        Process a user message and generate AI response.
        
        Handles both normal chat and party planning flow.
        Uses a lock to prevent concurrent processing of the same conversation.
        
        Args:
            conversation_id: ID of the conversation
            content: User message content
            
        Returns:
            Tuple of (user_message, assistant_message)
        """
        # Get or create lock for this conversation
        if conversation_id not in self.conversation_locks:
            self.conversation_locks[conversation_id] = asyncio.Lock()
        
        lock = self.conversation_locks[conversation_id]
        
        # Acquire lock - only one request per conversation at a time
        async with lock:
            logger.info(f"🔒 Acquired lock for conversation {conversation_id}")
            try:
                # Load conversation to get history
                conversation = storage_manager.load_conversation(conversation_id)
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
                
                # Create user message
                user_message = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    role=MessageRole.USER,
                    content=content,
                    timestamp=datetime.now(),
                    metadata={}
                )
                
                # Check if there's an active party plan for this conversation
                plan = storage_manager.get_plan_by_conversation(conversation_id)
                
                if plan and plan.state != PlanState.COMPLETE:
                    # Active party plan exists - route to party planner
                    logger.info(f"Routing to party planner (state: {plan.state})")
                    ai_content = await self._process_party_planning(
                        conversation_id,
                        content,
                        plan
                    )
                elif self.party_planner.is_party_request(content):
                    # New party request detected
                    logger.info("New party request detected, starting party planner")
                    ai_content = await self._start_party_planning(
                        conversation_id,
                        content
                    )
                else:
                    # Normal chat flow
                    logger.info("Normal chat flow")
                    ai_content = await self.generate_ai_response(
                        conversation.messages,
                        content
                    )
                
                # Create assistant message
                assistant_message = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    role=MessageRole.ASSISTANT,
                    content=ai_content,
                    timestamp=datetime.now(),
                    metadata={
                        "model": "gemini-2.5-flash"
                    }
                )
                
                logger.info(f"Processed message for conversation {conversation_id}")
                return user_message, assistant_message
                
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                raise
            finally:
                logger.info(f"🔓 Released lock for conversation {conversation_id}")
    
    async def _start_party_planning(
        self,
        conversation_id: str,
        user_request: str
    ) -> str:
        """
        Start a new party planning session
        
        Args:
            conversation_id: ID of the conversation
            user_request: Initial user request
            
        Returns:
            AI response (initial plan)
        """
        logger.info(f"Starting party planning for conversation {conversation_id}")
        
        # Reset party planner
        self.party_planner.reset()
        
        # Process initial request
        response = await self.party_planner.process_request(user_request)
        
        # Create and save plan
        plan = PartyPlan(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_request=user_request,
            current_plan=self.party_planner.current_plan,
            state=self.party_planner.state,
            gathered_info={},
            feedback_history=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        storage_manager.save_plan(plan)
        logger.info(f"Created plan {plan.id} for conversation {conversation_id}")
        
        return response
    
    async def _process_party_planning(
        self,
        conversation_id: str,
        user_input: str,
        plan: PartyPlan
    ) -> str:
        """
        Continue an existing party planning session
        
        Args:
            conversation_id: ID of the conversation
            user_input: User's message
            plan: Existing PartyPlan
            
        Returns:
            AI response
        """
        logger.info(f"Continuing party planning for plan {plan.id}, state: {plan.state}")
        
        # Restore party planner state
        self.party_planner.state = plan.state
        self.party_planner.current_plan = plan.current_plan
        self.party_planner.user_request = plan.user_request
        self.party_planner.feedback_history = plan.feedback_history
        self.party_planner.gathered_info = plan.gathered_info
        # Ensure conversation_id is in gathered_info for task storage
        self.party_planner.gathered_info["conversation_id"] = conversation_id
        
        # Store the state BEFORE processing
        state_before = self.party_planner.state
        
        # Process user input
        response = await self.party_planner.process_request(user_input)
        
        # Check if we JUST TRANSITIONED to SEARCHING (gathering just completed)
        # Frontend will auto-refresh to see new messages as they appear
        if state_before == PlanState.GATHERING and self.party_planner.state == PlanState.SEARCHING:
            logger.info("🔍 Gathering complete, executing search flow step by step...")
            
            # Step 1: Venue search
            logger.info("🏢 Step 1: Searching venues...")
            venue_response = await self.party_planner.search_venues_only()
            venue_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=venue_response,
                timestamp=datetime.now(),
                metadata={"step": "venue_search"}
            )
            storage_manager.add_message_to_conversation(conversation_id, venue_msg)
            logger.info("✅ Venue search message saved (frontend can now see it)")
            
            # Step 2: Bakery search
            logger.info("🍰 Step 2: Searching bakeries...")
            bakery_response = await self.party_planner.search_bakeries_only()
            bakery_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=bakery_response,
                timestamp=datetime.now(),
                metadata={"step": "bakery_search"}
            )
            storage_manager.add_message_to_conversation(conversation_id, bakery_msg)
            logger.info("✅ Bakery search message saved (frontend can now see it)")
            
            # Step 3: Task generation
            logger.info("📋 Step 3: Generating tasks...")
            task_response = await self.party_planner.generate_and_save_tasks()
            task_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=task_response,
                timestamp=datetime.now(),
                metadata={"step": "task_generation"}
            )
            storage_manager.add_message_to_conversation(conversation_id, task_msg)
            logger.info("✅ Task generation message saved")
            logger.info("🎉 All 3 messages saved! Frontend auto-refresh will show them.")
            
            # ⭐ Check if we transitioned to EXECUTING (party_planner changed state)
            if self.party_planner.state == PlanState.EXECUTING:
                logger.info("📞 Starting voice agent execution...")
                plan_id = self.party_planner.gathered_info.get("plan_id")
                
                if plan_id:
                    await self.execute_voice_agent_tasks(conversation_id, plan_id)
                    
                    # After execution, mark as complete
                    self.party_planner.state = PlanState.COMPLETE
                else:
                    logger.error("No plan_id found in gathered_info!")
        
        # Update plan
        plan.current_plan = self.party_planner.current_plan
        plan.state = self.party_planner.state
        plan.feedback_history = self.party_planner.feedback_history
        plan.gathered_info = self.party_planner.gathered_info
        plan.updated_at = datetime.now()
        
        storage_manager.save_plan(plan)
        logger.info(f"Updated plan {plan.id}, new state: {plan.state}")
        
        return response
    
    async def execute_voice_agent_tasks(
        self,
        conversation_id: str,
        plan_id: str
    ) -> None:
        """
        Wykonuje tasks przez voice agent z real-time komunikacją do użytkownika
        
        Args:
            conversation_id: ID konwersacji
            plan_id: ID planu (do pobrania tasks z storage)
        """
        from voice_agent import initiate_call, wait_for_conversation_completion, format_transcript, analyze_call_with_llm
        import time
        
        # Pobierz tasks z storage
        tasks = storage_manager.load_task_list(plan_id)
        if not tasks:
            logger.error(f"No tasks found for plan_id: {plan_id}")
            return
        
        logger.info(f"🎯 Executing {len(tasks)} tasks...")
        
        for task_idx, task in enumerate(tasks):
            # Task already loaded from storage (Task object)
            
            logger.info(f"📋 Task {task_idx + 1}/{len(tasks)}: {task.task_id}")
            
            # Send initial message about this task
            task_type = "lokal/restaurację" if "restaurant" in task.task_id else "cukiernię"
            intro_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=f"📞 Zaczynam dzwonić do {task_type}...\n\nMam {len(task.places)} opcji do wypróbowania.",
                timestamp=datetime.now(),
                metadata={"task_id": task.task_id, "step": "task_start"}
            )
            storage_manager.add_message_to_conversation(conversation_id, intro_msg)
            
            # Try each place until success
            for place_idx, place in enumerate(task.places):
                logger.info(f"📞 Calling place {place_idx + 1}/{len(task.places)}: {place.name}")
                
                # OVERRIDE phone number for POC
                original_phone = place.phone
                place.phone = "+48886859039"  # HARDCODED FOR POC
                
                # 1. Send "Calling..." message
                calling_msg_content = f"""📞 Dzwonię do: **{place.name}**
📱 Numer: {place.phone}

📝 **Instrukcje dla agenta:**
{task.notes_for_agent}

⏳ Czekam na połączenie..."""
                
                calling_msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    role=MessageRole.ASSISTANT,
                    content=calling_msg_content,
                    timestamp=datetime.now(),
                    metadata={
                        "task_id": task.task_id,
                        "place_name": place.name,
                        "place_phone": place.phone,
                        "step": "calling"
                    }
                )
                storage_manager.add_message_to_conversation(conversation_id, calling_msg)
                
                # 2. Initiate call
                call_result = initiate_call(task, place)
                
                if not call_result or not call_result.get('conversation_id'):
                    # Call failed to initiate
                    error_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"❌ Nie udało się nawiązać połączenia z {place.name}.\n\nPróbuję kolejne miejsce...",
                        timestamp=datetime.now(),
                        metadata={"step": "call_failed"}
                    )
                    storage_manager.add_message_to_conversation(conversation_id, error_msg)
                    place.phone = original_phone  # Restore
                    continue  # Try next place
                
                eleven_conversation_id = call_result['conversation_id']
                
                # 3. Wait for completion
                conversation_data = wait_for_conversation_completion(eleven_conversation_id)
                
                if not conversation_data:
                    # Failed to get conversation data
                    error_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"❌ Nie udało się pobrać transkryptu rozmowy z {place.name}.\n\nPróbuję kolejne miejsce...",
                        timestamp=datetime.now(),
                        metadata={"step": "transcript_failed"}
                    )
                    storage_manager.add_message_to_conversation(conversation_id, error_msg)
                    place.phone = original_phone  # Restore
                    continue  # Try next place
                
                # 4. Format and display transcript
                try:
                    logger.info(f"📝 Formatting transcript for {place.name}...")
                    logger.info(f"   Conversation status: {conversation_data.get('status')}")
                    logger.info(f"   Has transcript key: {bool(conversation_data.get('transcript'))}")
                    
                    # Debug: Show structure if transcript might be problematic
                    from voice_agent import debug_conversation_structure
                    if not conversation_data.get('transcript'):
                        logger.warning(f"⚠️  No 'transcript' key in conversation data for {place.name}")
                        debug_conversation_structure(conversation_data)
                    else:
                        logger.info(f"   Transcript items: {len(conversation_data.get('transcript', []))}")
                    
                    transcript = format_transcript(conversation_data)
                    
                    # Check if transcript parsing failed
                    if "Failed to parse transcript" in transcript or "Transcript is empty" in transcript:
                        logger.warning(f"⚠️  Transcript parsing issue for {place.name}")
                        debug_conversation_structure(conversation_data)
                    else:
                        logger.info(f"✅ Transcript formatted successfully ({len(transcript)} chars)")
                        # Show first 200 chars of transcript for verification
                        logger.info(f"   Preview: {transcript[:200]}...")
                    
                    transcript_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"📞 **Zakończono rozmowę z {place.name}**\n\n{transcript}",
                        timestamp=datetime.now(),
                        metadata={
                            "task_id": task.task_id,
                            "place_name": place.name,
                            "step": "transcript",
                            "conversation_id": eleven_conversation_id
                        }
                    )
                    storage_manager.add_message_to_conversation(conversation_id, transcript_msg)
                    
                except Exception as e:
                    logger.error(f"❌ Error formatting transcript: {e}")
                    error_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"❌ Błąd podczas formatowania transkryptu z {place.name}.\n\nStatus rozmowy: {conversation_data.get('status', 'unknown')}\nSprawdź logi backendu dla szczegółów.",
                        timestamp=datetime.now(),
                        metadata={"step": "transcript_format_error"}
                    )
                    storage_manager.add_message_to_conversation(conversation_id, error_msg)
                    place.phone = original_phone  # Restore
                    continue  # Try next place
                
                # 5. Analyze with LLM
                logger.info(f"🤖 Analyzing call with LLM...")
                logger.info(f"   Transcript length for analysis: {len(transcript)} chars")
                
                analysis = analyze_call_with_llm(task, place, transcript)
                
                logger.info(f"✅ LLM analysis complete!")
                logger.info(f"   Success: {analysis.get('success')}")
                logger.info(f"   Should continue: {analysis.get('should_continue')}")
                logger.info(f"   Confidence: {analysis.get('confidence', 0.0):.2f}")
                logger.info(f"   Reason: {analysis.get('reason', 'N/A')[:100]}")
                
                # 6. Send analysis result
                if analysis['success'] and not analysis['should_continue']:
                    # SUCCESS - goal achieved!
                    success_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"""✅ **Sukces w {place.name}!**

📊 Analiza rozmowy:
- Status: Cel osiągnięty ✅
- Powód: {analysis['reason']}
- Pewność: {analysis.get('confidence', 0) * 100:.0f}%

🎉 Przechodzę do następnego zadania...""",
                        timestamp=datetime.now(),
                        metadata={
                            "task_id": task.task_id,
                            "step": "analysis",
                            "analysis": analysis
                        }
                    )
                    storage_manager.add_message_to_conversation(conversation_id, success_msg)
                    
                    # Restore original phone
                    place.phone = original_phone
                    
                    # BREAK - move to next task
                    break
                else:
                    # FAILED or UNCLEAR - try next place
                    retry_msg = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=f"""⚠️ **Rozmowa z {place.name} nieudana**

📊 Analiza rozmowy:
- Status: Cel nieosiągnięty
- Powód: {analysis['reason']}
- Decyzja: Próbuję kolejne miejsce

⏭️ Przechodzę do następnej opcji...""",
                        timestamp=datetime.now(),
                        metadata={
                            "task_id": task.task_id,
                            "step": "analysis_retry",
                            "analysis": analysis
                        }
                    )
                    storage_manager.add_message_to_conversation(conversation_id, retry_msg)
                    
                    # Restore original phone
                    place.phone = original_phone
                    
                    # Short pause before next call
                    if place_idx < len(task.places) - 1:
                        time.sleep(5)
                    
                    # CONTINUE - try next place
                    continue
        
        # All tasks completed
        final_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=f"""🎉 **Zakończono wszystkie zadania!**

📞 Wykonano połączenia dla {len(tasks)} zadań.

Sprawdź transkrypty powyżej aby zobaczyć szczegóły każdej rozmowy.""",
            timestamp=datetime.now(),
            metadata={"step": "execution_complete"}
        )
        storage_manager.add_message_to_conversation(conversation_id, final_msg)
        
        logger.info("✅ All tasks executed!")
    
    async def generate_ai_response(
        self, 
        conversation_history: List[Message],
        user_message: str
    ) -> str:
        """
        Generate AI response based on conversation history and new message.
        
        Args:
            conversation_history: Previous messages in the conversation
            user_message: New user message
            
        Returns:
            AI generated response
        """
        try:
            # Create LLM client with context
            client = self._create_llm_client(conversation_history)
            
            # Generate response
            start_time = datetime.now()
            response = client.send(user_message)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Generated AI response in {processing_time:.2f}s")
            
            # Clean up response
            response = response.strip()
            
            if not response:
                response = "Przepraszam, nie mogłem wygenerować odpowiedzi. Spróbuj ponownie."
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate AI response: {error_msg}")
            
            # Check for specific errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return "Przepraszam, API osiągnęło limit zapytań. Spróbuj ponownie za chwilę lub sprawdź ustawienia API key."
            elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                return "Błąd autoryzacji API. Sprawdź czy GEMINI_API_KEY jest poprawnie ustawiony."
            elif "INVALID_ARGUMENT" in error_msg:
                return "Nieprawidłowe zapytanie do API. Sprawdź konfigurację."
            else:
                return f"Przepraszam, wystąpił błąd: {error_msg[:100]}"
    
    def create_conversation(self, initial_message: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            initial_message: Optional initial user message
            
        Returns:
            New conversation object
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        messages = []
        if initial_message:
            messages.append(Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=initial_message,
                timestamp=now,
                metadata={}
            ))
        
        conversation = Conversation(
            id=conversation_id,
            title=initial_message[:50] + "..." if initial_message and len(initial_message) > 50 else initial_message,
            messages=messages,
            created_at=now,
            updated_at=now
        )
        
        # Save to disk
        storage_manager.save_conversation(conversation)
        
        logger.info(f"Created new conversation {conversation_id}")
        return conversation


# Global instance
chat_service = ChatService()

