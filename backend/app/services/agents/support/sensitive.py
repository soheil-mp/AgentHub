from typing import Dict, Any, List
from app.services.agents.base import BaseAgent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SensitiveWorkflowAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a specialized agent handling sensitive operations.
    Your role is to:
    1. Process sensitive requests securely
    2. Handle payment information with strict security measures
    3. Manage personal data with appropriate privacy controls
    4. Ensure compliance with data protection regulations
    
    Current context:
    User ID: {user_id}
    Request type: {request_type}
    Security level: {security_level}
    Additional context: {additional_context}
    """

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update conversation memory
            self.update_memory(messages)
            
            # Format context for the LLM
            context = {
                "user_id": state.get("context", {}).get("user_id", "Unknown"),
                "request_type": self._determine_request_type(messages[-1].content if messages else ""),
                "security_level": "HIGH",  # Default to high security
                "additional_context": self.format_context(state.get("context", {}))
            }
            
            # Make LLM call with safety measures
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(**context)
            )
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize, but I'm having trouble processing your sensitive request securely. "
                         "Please try again or contact support for assistance.")
                    ],
                    "next": "ASSISTANT",
                    "requires_action": True,
                    "error": "Failed to process sensitive request"
                }
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "next": "ASSISTANT",
                "requires_action": False,
                "context": {
                    **state.get("context", {}),
                    "last_sensitive_interaction": datetime.utcnow().isoformat(),
                    "security_level": "HIGH",
                    "sensitive_operation_completed": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sensitive workflow: {str(e)}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I encountered an error while processing your sensitive request. "
                              "For your security, please try again or contact support.")
                ],
                "next": "ASSISTANT",
                "error": str(e)
            }

    def _determine_request_type(self, message: str) -> str:
        """Determine the type of sensitive request."""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["payment", "credit", "card", "billing"]):
            return "PAYMENT"
        elif any(keyword in message_lower for keyword in ["personal", "private", "data", "information"]):
            return "PERSONAL_DATA"
        elif any(keyword in message_lower for keyword in ["password", "login", "account", "security"]):
            return "ACCOUNT_SECURITY"
        else:
            return "GENERAL_SENSITIVE" 