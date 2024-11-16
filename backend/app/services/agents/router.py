from typing import Dict, Any, List, Tuple, Optional
from .base import BaseAgent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import re
import logging

logger = logging.getLogger(__name__)

class RouterAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a routing agent for a customer service system. 
    Analyze the customer's query and determine which specialist should handle it:
    
    PRODUCT: For product-specific questions about:
    - Features and specifications
    - Pricing and availability
    - Product comparisons
    - New product information
    - Purchase inquiries
    
    TECHNICAL: For technical issues including:
    - Bug reports and errors
    - Installation problems
    - Performance issues
    - Technical specifications
    - Integration questions
    - Troubleshooting
    
    CUSTOMER_SERVICE: For general inquiries about:
    - Account management
    - Billing and payments
    - General policies
    - Non-technical support
    - Refunds and returns
    - General assistance
    
    Previous routing: {routing_history}
    Current context: {context}
    
    Respond with:
    1. The appropriate department (PRODUCT, TECHNICAL, or CUSTOMER_SERVICE)
    2. A brief explanation of why this department is best suited
    3. Any relevant context that should be passed to the specialist
    """
    
    def _format_routing_history(self, dialog_state: List[str]) -> str:
        """Format routing history for context."""
        if not dialog_state:
            return "No previous routing"
        
        transitions = []
        for i in range(len(dialog_state) - 1):
            transitions.append(f"{dialog_state[i]} → {dialog_state[i+1]}")
        
        return "Routing history: " + " | ".join(transitions)
    
    def _analyze_intent(self, message: str, context: Dict[str, Any]) -> Tuple[str, float]:
        """Analyze message content to determine likely intent with confidence score."""
        
        patterns = {
            "PRODUCT": [
                (r"(feature|spec|price|cost|compare|new|available|buy)", 0.4),
                (r"(what.*product|which.*product|tell me about)", 0.3),
                (r"(looking.*for|interested.*in)", 0.2),
                (r"(purchase|order|delivery|shipping)", 0.4),
                (r"(warranty|guarantee)", 0.3)
            ],
            "TECHNICAL": [
                (r"(error|bug|issue|problem|not working|failed)", 0.5),
                (r"(how.*to|can.*t|doesn.*t)", 0.3),
                (r"(install|setup|configure|update|upgrade)", 0.4),
                (r"(crash|freeze|slow|broken)", 0.4),
                (r"(integration|api|code|database)", 0.5)
            ],
            "CUSTOMER_SERVICE": [
                (r"(account|bill|payment|policy|cancel)", 0.4),
                (r"(help.*with|support.*for)", 0.2),
                (r"(refund|return|exchange)", 0.4),
                (r"(speak.*to|talk.*to|contact)", 0.3),
                (r"(complaint|dissatisfied|unhappy)", 0.4)
            ]
        }
        
        message = message.lower()
        scores = {"PRODUCT": 0.0, "TECHNICAL": 0.0, "CUSTOMER_SERVICE": 0.0}
        
        # Calculate weighted scores for each category
        for dept, pattern_list in patterns.items():
            for pattern, weight in pattern_list:
                if re.search(pattern, message):
                    scores[dept] += weight
        
        # Apply context-based adjustments
        if context.get("previous_department"):
            prev_dept = context["previous_department"]
            scores[prev_dept] += 0.1  # Slight bias toward previous department
        
        if context.get("error_count", 0) > 2:
            scores["CUSTOMER_SERVICE"] += 0.2  # Bias toward CS if multiple errors
        
        # Get highest scoring department
        max_dept = max(scores.items(), key=lambda x: x[1])
        return max_dept[0], max_dept[1]
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            messages = self.format_messages(state["messages"])
            
            # Update memory with conversation history
            self.update_memory(messages)
            
            # Get the latest user message
            latest_msg = next((msg for msg in reversed(messages) 
                             if isinstance(msg, HumanMessage)), None)
            
            if not latest_msg:
                logger.warning("No user message found in state")
                return {
                    "messages": state["messages"],
                    "next": "CUSTOMER_SERVICE",
                    "context": {**state.get("context", {}), "routing_error": "no_message"}
                }
            
            # Format context for the LLM
            context = {
                "routing_history": self._format_routing_history(
                    state.get("dialog_state", [])
                ),
                "context": self.format_context(state.get("context", {}))
            }
            
            # First try using the LLM for routing
            response = await self._safe_llm_call(
                messages,
                system_override=self.SYSTEM_PROMPT.format(**context)
            )
            
            if not response:
                # Fallback to pattern matching if LLM fails
                dept, confidence = self._analyze_intent(
                    latest_msg.content,
                    state.get("context", {})
                )
                logger.info(f"Pattern matching routing: {dept} (confidence: {confidence})")
                return {
                    "messages": state["messages"],
                    "next": dept,
                    "context": {
                        **state.get("context", {}),
                        "routing_method": "pattern_matching",
                        "routing_confidence": confidence
                    }
                }
            
            # Extract department from LLM response
            dept_match = re.search(r"(PRODUCT|TECHNICAL|CUSTOMER_SERVICE)", response)
            
            if dept_match:
                routed_dept = dept_match.group(1)
                logger.info(f"LLM routing decision: {routed_dept}")
            else:
                # Fallback to pattern matching if LLM response unclear
                routed_dept, confidence = self._analyze_intent(
                    latest_msg.content,
                    state.get("context", {})
                )
                logger.warning(f"LLM routing unclear, using pattern matching: {routed_dept}")
            
            return {
                "messages": state["messages"] + [("assistant", response)],
                "next": routed_dept,
                "context": {
                    **state.get("context", {}),
                    "previous_department": routed_dept,
                    "routing_method": "llm" if dept_match else "pattern_matching"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RouterAgent.process: {e}")
            return {
                "messages": state["messages"],
                "next": "CUSTOMER_SERVICE",
                "error": str(e),
                "context": {**state.get("context", {}), "routing_error": str(e)}
            } 