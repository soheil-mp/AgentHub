from typing import Dict, Any, List
from ..base import BaseAgent
from langchain_core.messages import HumanMessage, AIMessage
import re

class TechnicalAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a technical support specialist.
    Help users resolve technical issues, bugs, and errors.
    Always try to:
    1. Understand the specific technical issue
    2. Ask for relevant error messages or symptoms if needed
    3. Provide clear step-by-step solutions
    4. Explain preventive measures for future reference
    
    If you need product specifications or billing assistance, indicate that in your response.
    
    Current context:
    {context}
    """
    
    def _needs_escalation(self, response: str) -> tuple[bool, str, str]:
        """Analyze if the response needs escalation to another department."""
        product_patterns = [
            r"product (specs|specifications|details|information)",
            r"(don't|do not) have (the |)product information",
            r"need to check (the |)product"
        ]
        
        billing_patterns = [
            r"billing (issue|question|concern)",
            r"payment (processing|method|issue)",
            r"account (status|balance|billing)"
        ]
        
        response_lower = response.lower()
        
        if any(re.search(pattern, response_lower) for pattern in product_patterns):
            return True, "PRODUCT", "Need product information to proceed"
        
        if any(re.search(pattern, response_lower) for pattern in billing_patterns):
            return True, "CUSTOMER_SERVICE", "Billing or account related issue"
            
        return False, "", ""
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory with conversation history
            self.update_memory(messages)
            
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(
                    context=state.get("context", "No additional context provided")
                )
            )
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize, but I'm having trouble processing your request. "
                         "Please try again or contact customer service for assistance.")
                    ],
                    "requires_action": True,
                    "next": "CUSTOMER_SERVICE",
                    "error": "LLM call failed"
                }
            
            # Check if we need to escalate
            needs_escalation, next_dept, reason = self._needs_escalation(response)
            
            # Add response to state
            updated_messages = state["messages"] + [("assistant", response)]
            
            # Track conversation in state
            dialog_state = state.get("dialog_state", [])
            if "TECHNICAL" not in dialog_state:
                dialog_state.append("TECHNICAL")
            
            return {
                "messages": updated_messages,
                "requires_action": needs_escalation,
                "next": next_dept if needs_escalation else None,
                "action_type": "ESCALATE" if needs_escalation else None,
                "reason": reason if needs_escalation else None,
                "dialog_state": dialog_state
            }
            
        except Exception as e:
            logger.error(f"Error in TechnicalAgent.process: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but an error occurred. "
                     "Please try again or contact customer service.")
                ],
                "requires_action": True,
                "next": "CUSTOMER_SERVICE",
                "error": str(e)
            } 