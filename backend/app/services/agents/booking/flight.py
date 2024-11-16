from typing import Dict, Any, List, Optional
from ..base import BaseAgent
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FlightBookingAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a specialized flight booking assistant.
    Help users with flight bookings, updates, and cancellations.
    Always:
    1. Verify flight availability and details
    2. Confirm booking preferences
    3. Explain fees and policies clearly
    4. Handle schedule changes professionally
    5. Provide booking confirmations
    
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
    
    def _analyze_booking_intent(self, message: str) -> Dict[str, Any]:
        """Analyze booking intent from message."""
        intents = {
            "new_booking": False,
            "modification": False,
            "cancellation": False,
            "information": False
        }
        
        # New booking patterns
        if any(word in message.lower() for word in ["book", "reserve", "new flight", "schedule"]):
            intents["new_booking"] = True
            
        # Modification patterns
        if any(word in message.lower() for word in ["change", "modify", "reschedule", "update"]):
            intents["modification"] = True
            
        # Cancellation patterns
        if any(word in message.lower() for word in ["cancel", "refund", "void"]):
            intents["cancellation"] = True
            
        # Information patterns
        if any(word in message.lower() for word in ["info", "detail", "status", "when", "what time"]):
            intents["information"] = True
            
        return intents
    
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
            
            # Analyze booking intent
            intents = self._analyze_booking_intent(latest_msg.content)
            
            # Make LLM call
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(**context)
            )
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize, but I'm having trouble processing your request. "
                         "Let me connect you with customer service for assistance.")
                    ],
                    "requires_action": True,
                    "next": "CUSTOMER_SERVICE",
                    "action_type": "ERROR_RECOVERY",
                    "error": "LLM call failed"
                }
            
            # Update dialog state
            dialog_state = state.get("dialog_state", [])
            if "FLIGHT_BOOKING" not in dialog_state:
                dialog_state.append("FLIGHT_BOOKING")
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "requires_action": False,
                "dialog_state": dialog_state,
                "context": {
                    **state.get("context", {}),
                    "booking_intents": intents,
                    "last_flight_interaction": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in FlightBookingAgent.process: {e}")
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