from typing import Dict, Any
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a routing agent that directs user queries to the appropriate specialist agent.
            - PRODUCT: For product information, pricing, and availability
            - TECHNICAL: For technical support and troubleshooting
            - CUSTOMER_SERVICE: For general inquiries, billing, and account issues
            - HUMAN: For complex issues requiring human intervention"""
        )
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory
            self.update_memory(messages)
            
            # Get latest message
            latest_message = messages[-1].content if messages else ""
            
            # Determine which agent should handle this
            response = await self._safe_llm_call(
                messages,
                system_override="""Analyze the user's message and respond with only one of: 
                PRODUCT, TECHNICAL, CUSTOMER_SERVICE, or HUMAN. Choose based on these criteria:
                - PRODUCT: Product inquiries, pricing, availability
                - TECHNICAL: Technical issues, troubleshooting
                - CUSTOMER_SERVICE: General support, billing, accounts
                - HUMAN: Complex issues needing human help"""
            )
            
            if not response:
                return {
                    "messages": state["messages"],
                    "next": "CUSTOMER_SERVICE",
                    "error": "Failed to route message"
                }
            
            # Clean up response to get just the agent type
            next_agent = response.strip().upper()
            if next_agent not in ["PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", "HUMAN"]:
                next_agent = "CUSTOMER_SERVICE"
            
            return {
                "messages": state["messages"],
                "next": next_agent,
                "context": {
                    **state.get("context", {}),
                    "routing_reason": response
                }
            }
            
        except Exception as e:
            logger.error(f"Error in router agent: {e}")
            return {
                "messages": state["messages"],
                "next": "CUSTOMER_SERVICE",
                "error": str(e)
            } 