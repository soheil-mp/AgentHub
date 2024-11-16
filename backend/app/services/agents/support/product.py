from typing import Dict, Any, List, Optional, Tuple
from ..base import BaseAgent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ProductAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a product specialist for our company. 
    You have deep knowledge of our products, features, and pricing.
    Always:
    1. Be precise and accurate about product specifications
    2. Verify product availability before making recommendations
    3. Explain features and benefits clearly
    4. Compare products when relevant
    5. Provide pricing information when available
    
    Current context:
    User ID: {user_id}
    Previous interactions: {interaction_history}
    Additional context: {additional_context}
    
    If you need to escalate:
    - Technical support: For installation, bugs, or technical issues
    - Customer service: For billing, accounts, or general inquiries
    
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
    
    def _analyze_escalation_need(self, response: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Analyze if response indicates need for escalation."""
        technical_patterns = [
            r"(technical|support|install|bug|error|issue)",
            r"(not working|doesn't work|failed|crash)",
            r"(setup|configure|integration)",
            r"(troubleshoot|debug|fix)"
        ]
        
        service_patterns = [
            r"(billing|payment|account|subscription)",
            r"(refund|cancel|return)",
            r"(policy|terms|conditions)",
            r"(customer service|support team)"
        ]
        
        response_lower = response.lower()
        
        # Check for technical escalation
        if any(re.search(pattern, response_lower) for pattern in technical_patterns):
            return True, "TECHNICAL", "Technical support needed for implementation/issues"
            
        # Check for customer service escalation
        if any(re.search(pattern, response_lower) for pattern in service_patterns):
            return True, "CUSTOMER_SERVICE", "Account or billing related inquiry"
            
        return False, None, None
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory with conversation history
            self.update_memory(messages)
            
            # Format context for the LLM
            context = {
                "user_id": state.get("context", {}).get("user_id", "Unknown"),
                "interaction_history": self._format_interaction_history(messages),
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
                        ("assistant", "I apologize, but I'm having trouble accessing product information. "
                         "Let me connect you with customer service for assistance.")
                    ],
                    "requires_action": True,
                    "next": "CUSTOMER_SERVICE",
                    "action_type": "ERROR_RECOVERY",
                    "error": "LLM call failed"
                }
            
            # Analyze response for escalation needs
            needs_escalation, next_dept, reason = self._analyze_escalation_need(response)
            
            # Update dialog state
            dialog_state = state.get("dialog_state", [])
            if "PRODUCT" not in dialog_state:
                dialog_state.append("PRODUCT")
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "requires_action": needs_escalation,
                "next": next_dept if needs_escalation else None,
                "action_type": "ESCALATE" if needs_escalation else None,
                "reason": reason if needs_escalation else None,
                "dialog_state": dialog_state,
                "context": {
                    **state.get("context", {}),
                    "last_product_interaction": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in ProductAgent.process: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I'm having trouble processing your request. "
                     "Let me connect you with customer service for assistance.")
                ],
                "requires_action": True,
                "next": "CUSTOMER_SERVICE",
                "action_type": "ERROR_RECOVERY",
                "error": str(e)
            }