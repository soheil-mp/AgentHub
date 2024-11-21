from typing import Dict, Any, List
from app.services.agents.base import BaseAgent
from datetime import datetime
import re

class AssistantAgent(BaseAgent):
    SYSTEM_PROMPT = """You are an intelligent travel assistant that coordinates various specialized services.
    Your role is to:
    1. Understand user requests and determine the appropriate service to handle them
    2. Delegate tasks to specialized agents:
       - FLIGHT: For flight bookings and inquiries
       - HOTEL: For hotel reservations
       - CAR_RENTAL: For vehicle rentals
       - EXCURSION: For activity bookings
       - SENSITIVE: For tasks requiring special handling (e.g., payment processing)
    3. Maintain context and coordinate between different services
    4. Ensure a smooth user experience

    Current context:
    User ID: {user_id}
    Previous interactions: {interaction_history}
    Additional context: {additional_context}
    """

    def _determine_next_agent(self, user_message: str) -> str:
        """Determine which specialized agent should handle the request."""
        message_lower = user_message.lower()
        
        # Flight-related keywords
        if any(keyword in message_lower for keyword in [
            "flight", "plane", "airport", "airline", "travel"
        ]):
            return "FLIGHT"
            
        # Hotel-related keywords
        if any(keyword in message_lower for keyword in [
            "hotel", "room", "accommodation", "stay", "resort"
        ]):
            return "HOTEL"
            
        # Car rental keywords
        if any(keyword in message_lower for keyword in [
            "car", "vehicle", "rental", "drive"
        ]):
            return "CAR_RENTAL"
            
        # Excursion keywords
        if any(keyword in message_lower for keyword in [
            "tour", "activity", "excursion", "visit", "sightseeing"
        ]):
            return "EXCURSION"
            
        # Sensitive workflow keywords
        if any(keyword in message_lower for keyword in [
            "payment", "credit card", "personal", "sensitive", "private"
        ]):
            return "SENSITIVE"
            
        return "NONE"  # Handle directly if no specific agent needed

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update conversation memory
            self.update_memory(messages)
            
            # Get latest user message
            latest_msg = messages[-1].content if messages else ""
            
            # Determine which agent should handle the request
            next_agent = self._determine_next_agent(latest_msg)
            
            if next_agent == "NONE":
                # Handle directly if no specialized agent is needed
                response = await self._safe_llm_call(
                    messages,
                    system_override=self.SYSTEM_PROMPT.format(
                        user_id=state.get("context", {}).get("user_id", "Unknown"),
                        interaction_history=self._format_interaction_history(messages),
                        additional_context=self.format_context(state.get("context", {}))
                    )
                )
                
                return {
                    "messages": state["messages"] + [("assistant", response)],
                    "next": "NONE",
                    "requires_action": False,
                    "context": {
                        **state.get("context", {}),
                        "last_assistant_interaction": datetime.utcnow().isoformat()
                    }
                }
            
            # Prepare handoff message
            handoff_messages = {
                "FLIGHT": "Let me help you with your flight arrangements.",
                "HOTEL": "I'll assist you with your hotel booking.",
                "CAR_RENTAL": "I'll help you find the right vehicle rental.",
                "EXCURSION": "I'll help you discover and book exciting activities.",
                "SENSITIVE": "I'll handle your sensitive request securely."
            }
            
            return {
                "messages": state["messages"] + [("assistant", handoff_messages[next_agent])],
                "next": next_agent,
                "requires_action": True,
                "context": {
                    **state.get("context", {}),
                    "last_assistant_interaction": datetime.utcnow().isoformat(),
                    "delegated_to": next_agent
                }
            }
            
        except Exception as e:
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I'm having trouble processing your request. "
                              "Please try again in a moment.")
                ],
                "next": "NONE",
                "error": str(e)
            } 