"""
Venue Searcher - Uses Google Search to find venues and bakeries for party planning
"""
import re
import json
import logging
from typing import List, Optional
from datetime import datetime

from llm_client import LLMClient
from models import Venue, VenueSearchResult

logger = logging.getLogger(__name__)


class VenueSearcher:
    """
    Searches for venues and bakeries using Google Search via LLM
    """
    
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
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        Initialize VenueSearcher with LLM client
        
        Args:
            model: Model name to use (has Google Search tool)
        """
        self.model = model
        self.llm_client = LLMClient(model=model)
        logger.info(f"VenueSearcher initialized with model {model}")
    
    async def search_venues(
        self, 
        location: str, 
        query_type: str = "lokale z salami/restauracje", 
        count: int = 3
    ) -> VenueSearchResult:
        """
        Search for venues using Google Search (ASYNC - non-blocking)
        
        Args:
            location: City/location (e.g. "Warszawa")
            query_type: Type of venue (e.g. "lokale z salami", "restauracje")
            count: Number of results to return (default 3)
            
        Returns:
            VenueSearchResult with list of venues
        """
        try:
            logger.info(f"🔍 Searching for {count} venues: {query_type} in {location}")
            
            # Format the prompt
            prompt = self.VENUE_SEARCH_PROMPT.format(
                query_type=query_type,
                location=location
            )
            
            # ✅ ASYNC call - won't block event loop
            logger.info(f"📡 Calling LLM with Google Search...")
            response = await self.llm_client.send_async(prompt)
            logger.info(f"✅ LLM responded, parsing results...")
            
            # ✅ Parse the response (async)
            venues = await self._parse_search_results(response, venue_type="restaurant")
            
            logger.info(f"✅ Found {len(venues)} venues")
            
            return VenueSearchResult(
                venues=venues[:count],  # Limit to requested count
                location=location,
                query_type=query_type,
                searched_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search venues: {e}", exc_info=True)
            # Return empty result on error
            return VenueSearchResult(
                venues=[],
                location=location,
                query_type=query_type,
                searched_at=datetime.now()
            )
    
    async def search_bakeries(self, location: str, count: int = 3) -> VenueSearchResult:
        """
        Search for bakeries using Google Search (ASYNC - non-blocking)
        
        Args:
            location: City/location (e.g. "Warszawa")
            count: Number of results to return (default 3)
            
        Returns:
            VenueSearchResult with list of bakeries
        """
        try:
            logger.info(f"🔍 Searching for {count} bakeries in {location}")
            
            # Format the prompt for bakeries
            prompt = self.VENUE_SEARCH_PROMPT.format(
                query_type="profesjonalne cukiernie",
                location=location
            )
            
            # ✅ ASYNC call - won't block event loop
            logger.info(f"📡 Calling LLM with Google Search...")
            response = await self.llm_client.send_async(prompt)
            logger.info(f"✅ LLM responded, parsing results...")
            
            # ✅ Parse the response (async)
            bakeries = await self._parse_search_results(response, venue_type="bakery")
            
            logger.info(f"✅ Found {len(bakeries)} bakeries")
            
            return VenueSearchResult(
                venues=bakeries[:count],  # Limit to requested count
                location=location,
                query_type="cukiernie",
                searched_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to search bakeries: {e}", exc_info=True)
            # Return empty result on error
            return VenueSearchResult(
                venues=[],
                location=location,
                query_type="cukiernie",
                searched_at=datetime.now()
            )
    
    async def _parse_search_results(self, text: str, venue_type: str) -> List[Venue]:
        """
        Parse LLM response to extract venue information using AI parsing (ASYNC)
        
        Args:
            text: LLM response text
            venue_type: Type of venue ("restaurant", "bakery")
            
        Returns:
            List of Venue objects
        """
        venues = []
        
        try:
            # Use LLM to parse the results - much more robust than regex!
            parsing_prompt = f"""Wyciągnij z poniższego tekstu informacje o miejscach w formacie JSON.

Tekst do sparsowania:
{text}

Zwróć TYLKO JSON array (bez żadnego dodatkowego tekstu) w formacie:
[
  {{"name": "Nazwa miejsca", "phone": "+48 XXX XXX XXX", "website": "www.strona.com"}},
  {{"name": "Nazwa miejsca 2", "phone": "+48 YYY YYY YYY", "website": null}}
]

WAŻNE:
- Tylko JSON array, bez markdown, bez ```json
- Jeśli nie ma strony www, użyj null
- Numer telefonu bez nawiasów kwadratowych
- Tylko numery telefonów polskie (+48)
"""
            
            # ✅ ASYNC call to LLM
            parser_client = LLMClient(model=self.model)
            response = await parser_client.send_async(parsing_prompt)
            
            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                # Remove code block markers
                response = re.sub(r'^```(?:json)?\n', '', response)
                response = re.sub(r'\n```$', '', response)
                response = response.strip()
            
            # Parse JSON
            import json
            parsed_data = json.loads(response)
            
            # Convert to Venue objects
            for item in parsed_data:
                venue = Venue(
                    name=item.get("name", "").strip(),
                    phone=item.get("phone", "").strip(),
                    website=item.get("website"),
                    venue_type=venue_type
                )
                
                # Validate
                if venue.name and venue.phone:
                    venues.append(venue)
                    logger.info(f"✓ Parsed venue: {venue.name} | {venue.phone}")
                else:
                    logger.warning(f"⚠️ Skipping incomplete venue: {item}")
            
            if not venues:
                logger.warning(f"⚠️ No venues parsed from response.")
                logger.debug(f"Original text:\n{text[:400]}")
                logger.debug(f"Parser response:\n{response[:400]}")
            else:
                logger.info(f"✅ Successfully parsed {len(venues)} venues")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response was: {response[:200]}")
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return venues
    
    def format_venues_for_user(self, venues: List[Venue], title: str = "Znalezione lokale") -> str:
        """
        Format venues for display to user in chat
        
        Args:
            venues: List of Venue objects
            title: Title for the list
            
        Returns:
            Formatted string with emoji and readable format
        """
        if not venues:
            return "❌ Nie znalazłem odpowiednich miejsc."
        
        # Choose emoji based on venue type
        emoji_map = {
            "restaurant": "🏢",
            "bakery": "🍰",
            "venue": "🎉"
        }
        
        venue_type = venues[0].venue_type if venues else "venue"
        emoji = emoji_map.get(venue_type, "📍")
        
        result = f"{emoji} {title}:\n\n"
        
        for i, venue in enumerate(venues, 1):
            result += f"{i}. {venue.name}\n"
            if venue.phone:
                result += f"   📞 {venue.phone}\n"
            if venue.website:
                result += f"   🌐 {venue.website}\n"
            result += "\n"
        
        return result.strip()

