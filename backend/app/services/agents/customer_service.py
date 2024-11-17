from typing import Dict, Any
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class CustomerServiceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a customer service representative who helps with:
            - General inquiries
            - Account management
            - Billing questions
            - Service issues
            Be friendly, helpful, and empathetic in your responses."""
        )
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory
            self.update_memory(messages)
            
            # Get response from LLM
            response = await self._safe_llm_call(messages)
            
            if not response:
                return {
                    "messages": state["messages"] + [
                        ("assistant", "I apologize, but I'm having trouble assisting you. Let me connect you with a specialist.")
                    ],
                    "next": "HUMAN",
                    "error": "LLM call failed"
                }
            
            # Add response to messages
            updated_messages = state["messages"] + [
                ("assistant", response)
            ]
            
            # Check if we need to escalate
            needs_escalation = any(keyword in response.lower() 
                                 for keyword in ["manager", "supervisor", "specialist", "human"])
            
            return {
                "messages": updated_messages,
                "next": "HUMAN" if needs_escalation else "ROUTER",
                "context": state.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Error in customer service agent: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize for the difficulty. Let me connect you with a specialist.")
                ],
                "next": "HUMAN",
                "error": str(e)
            } 