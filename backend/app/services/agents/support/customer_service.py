from typing import Dict, Any, List
from ..base import BaseAgent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class CustomerServiceAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a customer service specialist.
    Handle general inquiries, billing questions, and account-related issues.
    Always:
    1. Be empathetic and professional
    2. Verify account details when needed
    3. Provide clear explanations of policies and procedures
    4. Offer additional assistance if needed
    
    If technical support is needed, indicate that in your response.
    If product information is needed, indicate that in your response.
    
    Current context:
    User ID: {user_id}
    Previous interactions: {interaction_history}
    Additional context: {additional_context}
    """
    
    def _format_interaction_history(self, messages: List[BaseMessage]) -> str:
        """Format previous interactions for context."""
        history = []
        for msg in messages[-5:]:  # Only include last 5 messages
            if isinstance(msg, (HumanMessage, AIMessage)):
                role = "Customer" if isinstance(msg, HumanMessage) else "Agent"
                history.append(f"{role}: {msg.content}")
        return "\n".join(history) if history else "No previous interactions"
    
    def _check_for_escalation(self, response: str) -> tuple[bool, str, str]:
        """Check if response indicates need for escalation."""
        response_lower = response.lower()
        
        if any(keyword in response_lower for keyword in 
               ["technical issue", "technical support", "bug", "error"]):
            return True, "TECHNICAL", "Technical support needed"
            
        if any(keyword in response_lower for keyword in 
               ["product details", "product specifications", "product features"]):
            return True, "PRODUCT", "Product information needed"
            
        return False, "", ""
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update conversation memory
            self.update_memory(messages)
            
            # Format context for prompt
            context = {
                "user_id": state.get("context", {}).get("user_id", "Unknown"),
                "interaction_history": self._format_interaction_history(messages),
                "additional_context": self.format_context(state.get("context", {}))
            }
            
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(**context)
            )
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize for the technical difficulty. "
                         "Let me connect you with someone who can help.")
                    ],
                    "requires_action": True,
                    "next": "TECHNICAL",
                    "error": "LLM call failed"
                }
            
            # Check for needed escalation
            needs_escalation, next_dept, reason = self._check_for_escalation(response)
            
            # Update dialog state
            dialog_state = state.get("dialog_state", [])
            if "CUSTOMER_SERVICE" not in dialog_state:
                dialog_state.append("CUSTOMER_SERVICE")
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "requires_action": needs_escalation,
                "next": next_dept if needs_escalation else None,
                "action_type": "ESCALATE" if needs_escalation else None,
                "reason": reason if needs_escalation else None,
                "dialog_state": dialog_state
            }
            
        except Exception as e:
            logger.error(f"Error in CustomerServiceAgent.process: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I'm having trouble processing your request. "
                     "Please try again in a moment.")
                ],
                "requires_action": False,
                "error": str(e)
            } 