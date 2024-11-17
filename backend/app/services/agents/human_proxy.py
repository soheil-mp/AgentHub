from typing import Dict, Any
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class HumanProxyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a human handoff specialist who:
            - Prepares cases for human review
            - Collects relevant information
            - Explains the handoff process to users
            - Ensures a smooth transition to human support"""
        )
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory
            self.update_memory(messages)
            
            # Prepare handoff message
            handoff_message = (
                "I understand this requires human assistance. "
                "I've documented your case and will connect you with a specialist. "
                "Please allow some time for a human agent to review your case and respond."
            )
            
            # Add handoff message to state
            updated_messages = state["messages"] + [
                ("assistant", handoff_message)
            ]
            
            return {
                "messages": updated_messages,
                "next": "ROUTER",  # Return to router after handoff
                "requires_action": True,
                "action_type": "HUMAN_HANDOFF",
                "context": {
                    **state.get("context", {}),
                    "needs_human_review": True,
                    "handoff_reason": "Escalated to human support"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in human proxy agent: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize for the difficulty in connecting you with a specialist. Please try again shortly.")
                ],
                "next": "ROUTER",
                "error": str(e)
            } 