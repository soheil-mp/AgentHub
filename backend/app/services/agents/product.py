from typing import Dict, Any
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a product specialist who helps customers with:
            - Product information and specifications
            - Pricing and availability
            - Product comparisons
            - Purchase recommendations
            Always be helpful and accurate with product information."""
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
                        ("assistant", "I apologize, but I'm having trouble accessing product information. Let me connect you with customer service.")
                    ],
                    "next": "CUSTOMER_SERVICE",
                    "error": "LLM call failed"
                }
            
            # Add response to messages
            updated_messages = state["messages"] + [
                ("assistant", response)
            ]
            
            # Check if we need to escalate
            needs_escalation = any(keyword in response.lower() 
                                 for keyword in ["specialist", "manager", "human", "complex"])
            
            return {
                "messages": updated_messages,
                "next": "HUMAN" if needs_escalation else "ROUTER",
                "context": state.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Error in product agent: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize for the technical difficulty. Let me connect you with customer service.")
                ],
                "next": "CUSTOMER_SERVICE",
                "error": str(e)
            } 