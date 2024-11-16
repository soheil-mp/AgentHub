from typing import Dict, Any, List, Optional
from ..base import BaseAgent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ExcursionAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a specialized excursion and trip planning assistant.
    Help users discover and book exciting activities and experiences.
    Always:
    1. Verify activity availability and schedules
    2. Confirm booking preferences and group size
    3. Explain activity details and requirements
    4. Handle special requests professionally
    5. Provide booking confirmations and important details
    
    Current context:
    User ID: {user_id}
    Previous interactions: {interaction_history}
    Additional context: {additional_context}
    Current time: {current_time}
    
    If you need to escalate:
    - Customer service: For billing or account issues
    - Technical support: For booking system problems
    
    Indicate the need for escalation in your response.
    """
    
    def _format_interaction_history(self, messages: List[BaseMessage]) -> str:
        """Format previous interactions for context."""
        history = []
        for msg in messages[-5:]:  # Only include last 5 messages
            if isinstance(msg, (HumanMessage, AIMessage)):
                role = "Customer" if isinstance(msg, HumanMessage) else "Agent"
                history.append(f"{role}: {msg.content}")
        return "\n".join(history) if history else "No previous interactions"
    
    def _analyze_excursion_preferences(self, message: str) -> Dict[str, Any]:
        """Analyze excursion preferences from message."""
        preferences = {
            "location": None,
            "dates": None,
            "activity_type": None,
            "group_size": None,
            "interests": [],
            "price_range": None,
            "duration": None
        }
        
        message_lower = message.lower()
        
        # Location analysis
        location_patterns = [
            r"in\s+([a-zA-Z\s]+)",
            r"at\s+([a-zA-Z\s]+)",
            r"near\s+([a-zA-Z\s]+)",
            r"around\s+([a-zA-Z\s]+)"
        ]
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                preferences["location"] = match.group(1).strip()
                break
        
        # Activity type analysis
        activity_types = [
            "sightseeing", "adventure", "cultural", "food", 
            "nature", "sports", "relaxation", "shopping"
        ]
        for activity in activity_types:
            if activity in message_lower:
                preferences["activity_type"] = activity
                break
        
        # Interest analysis
        interests = [
            "history", "art", "music", "outdoor", "wine", 
            "photography", "architecture", "local"
        ]
        preferences["interests"] = [
            interest for interest in interests 
            if interest in message_lower
        ]
        
        # Duration analysis
        duration_patterns = [
            r"(\d+)\s*(day|hour|week)s?",
            r"half[- ]day",
            r"full[- ]day"
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, message_lower)
            if match:
                preferences["duration"] = match.group(0)
                break
        
        return preferences
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory
            self.update_memory(messages)
            
            # Format context for the LLM
            context = {
                "user_id": state.get("context", {}).get("user_id", "Unknown"),
                "interaction_history": self._format_interaction_history(messages),
                "additional_context": self.format_context(state.get("context", {})),
                "current_time": datetime.utcnow().isoformat()
            }
            
            # Get latest message
            latest_msg = messages[-1] if messages else None
            if not latest_msg:
                return {
                    "messages": state["messages"],
                    "requires_action": True,
                    "next": "ROUTER",
                    "error": "No messages found"
                }
            
            # Analyze excursion preferences
            preferences = self._analyze_excursion_preferences(latest_msg.content)
            
            # Make LLM call
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(**context)
            )
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize, but I'm having trouble with the booking system. "
                         "Let me connect you with customer service for assistance.")
                    ],
                    "requires_action": True,
                    "next": "CUSTOMER_SERVICE",
                    "action_type": "ERROR_RECOVERY",
                    "error": "LLM call failed"
                }
            
            # Update dialog state
            dialog_state = state.get("dialog_state", [])
            if "EXCURSION" not in dialog_state:
                dialog_state.append("EXCURSION")
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "requires_action": False,
                "dialog_state": dialog_state,
                "context": {
                    **state.get("context", {}),
                    "excursion_preferences": preferences,
                    "last_excursion_interaction": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in ExcursionAgent.process: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I'm having trouble with the booking system. "
                     "Let me connect you with customer service for assistance.")
                ],
                "requires_action": True,
                "next": "CUSTOMER_SERVICE",
                "action_type": "ERROR_RECOVERY",
                "error": str(e)
            } 