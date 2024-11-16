from typing import Dict, Any, List
from ..base import BaseAgent
from langchain_core.messages import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class HumanProxyAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a human support coordinator.
    Your role is to:
    1. Prepare cases for human agent review
    2. Collect all relevant information
    3. Summarize the issue clearly
    4. Flag urgent or critical issues
    5. Track human agent availability
    
    Current context:
    User ID: {user_id}
    Previous interactions: {interaction_history}
    Additional context: {additional_context}
    Escalation reason: {escalation_reason}
    Priority level: {priority_level}
    """
    
    def _format_case_summary(self, messages: List[Any], context: Dict[str, Any]) -> str:
        """Format a summary for human agents."""
        try:
            recent_messages = messages[-5:] if len(messages) > 5 else messages
            summary_parts = [
                "=== Case Summary ===",
                f"User ID: {context.get('user_id', 'Unknown')}",
                f"Priority: {context.get('priority_level', 'Normal')}",
                f"Escalation Reason: {context.get('escalation_reason', 'Not specified')}",
                "\n=== Recent Conversation ===",
            ]
            
            for msg in recent_messages:
                role = "Customer" if isinstance(msg, HumanMessage) else "AI"
                summary_parts.append(f"{role}: {msg.content}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error formatting case summary: {e}")
            return "Error creating case summary"
    
    def _assess_priority(self, state: Dict[str, Any]) -> str:
        """Assess case priority based on context and conversation."""
        try:
            context = state.get("context", {})
            messages = state.get("messages", [])
            
            # Default to normal priority
            priority = "NORMAL"
            
            # Check for urgent keywords in recent messages
            urgent_keywords = ["urgent", "emergency", "critical", "immediately", "asap"]
            recent_messages = messages[-3:] if len(messages) > 3 else messages
            
            for msg in recent_messages:
                if any(keyword in msg[1].lower() for keyword in urgent_keywords):
                    priority = "HIGH"
                    break
            
            # Check error count
            if context.get("error_count", 0) > 2:
                priority = "HIGH"
            
            # Check escalation history
            dialog_state = state.get("dialog_state", [])
            if len(dialog_state) > 4:  # Multiple transfers
                priority = "HIGH"
            
            return priority
            
        except Exception as e:
            logger.error(f"Error assessing priority: {e}")
            return "NORMAL"
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory
            self.update_memory(messages)
            
            # Assess priority
            priority = self._assess_priority(state)
            
            # Prepare context for prompt
            context = {
                "user_id": state.get("context", {}).get("user_id", "Unknown"),
                "interaction_history": self._format_interaction_history(messages),
                "additional_context": self.format_context(state.get("context", {})),
                "escalation_reason": state.get("reason", "Not specified"),
                "priority_level": priority
            }
            
            # Generate case summary
            case_summary = self._format_case_summary(messages, context)
            
            # Prepare handoff message
            handoff_message = (
                f"I'll connect you with a human agent who can better assist you. "
                f"Priority level: {priority}\n"
                f"A support representative will review your case and respond shortly."
            )
            
            return {
                "messages": state["messages"] + [("assistant", handoff_message)],
                "requires_action": True,
                "next": "HUMAN_AGENT",
                "action_type": "HUMAN_ESCALATION",
                "priority": priority,
                "case_summary": case_summary,
                "dialog_state": state.get("dialog_state", []) + ["HUMAN_PROXY"],
                "context": {
                    **state.get("context", {}),
                    "priority_level": priority,
                    "case_summary": case_summary,
                    "needs_human_review": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in HumanProxyAgent.process: {e}")
            return {
                "messages": state["messages"] + [
                    ("assistant", "I apologize, but I'm having trouble processing your request. "
                     "Please try again or contact customer service directly.")
                ],
                "requires_action": True,
                "next": "CUSTOMER_SERVICE",
                "action_type": "ERROR_RECOVERY",
                "error": str(e)
            } 