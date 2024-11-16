from typing import Dict, Any, Annotated, List, Literal, Optional, Union, Tuple
from typing_extensions import TypedDict
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from langgraph.graph.message import AnyMessage, add_messages
from .agents import (
    RouterAgent,
    FlightBookingAgent, HotelBookingAgent, CarRentalAgent, ExcursionAgent,
    ProductAgent, TechnicalAgent, CustomerServiceAgent, HumanProxyAgent
)
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    if right == "clear":
        return []
    return left + [right]

class State(TypedDict):
    """The state of our application."""
    messages: Annotated[List[AnyMessage], add_messages]
    next: str
    context: Dict[str, Any]
    dialog_state: Annotated[
        list[Literal[
            "ROUTER", "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", 
            "HUMAN_PROXY", "FLIGHT_BOOKING", "HOTEL_BOOKING",
            "CAR_RENTAL", "EXCURSION"
        ]],
        update_dialog_stack,
    ]
    requires_action: bool
    action_type: Optional[str]
    error: Optional[str]

def create_graph() -> Graph:
    # Initialize agents
    router = RouterAgent()
    product = ProductAgent()
    technical = TechnicalAgent()
    customer_service = CustomerServiceAgent()
    human_proxy = HumanProxyAgent()
    flight_booking = FlightBookingAgent()
    hotel_booking = HotelBookingAgent()
    car_rental = CarRentalAgent()
    excursion = ExcursionAgent()
    
    # Create workflow graph
    workflow = StateGraph(State)
    
    # Add nodes for all agents
    workflow.add_node("ROUTER", router.process)
    workflow.add_node("PRODUCT", product.process)
    workflow.add_node("TECHNICAL", technical.process)
    workflow.add_node("CUSTOMER_SERVICE", customer_service.process)
    workflow.add_node("HUMAN_PROXY", human_proxy.process)
    workflow.add_node("FLIGHT_BOOKING", flight_booking.process)
    workflow.add_node("HOTEL_BOOKING", hotel_booking.process)
    workflow.add_node("CAR_RENTAL", car_rental.process)
    workflow.add_node("EXCURSION", excursion.process)
    
    def should_escalate(state: State) -> bool:
        """Enhanced escalation logic."""
        context = state.get("context", {})
        
        # Check error count
        if context.get("error_count", 0) >= 3:
            return True
            
        # Check conversation length
        if len(state.get("messages", [])) > 15:  # Long conversations
            return True
            
        # Check routing loops
        dialog_state = state.get("dialog_state", [])
        if len(dialog_state) > 5:  # Too many transfers
            return True
            
        # Check user frustration signals
        recent_messages = state.get("messages", [])[-3:]
        frustration_keywords = [
            "frustrated", "angry", "upset", "unhelpful", "human",
            "supervisor", "manager", "terrible", "waste", "useless"
        ]
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                if any(keyword in msg.content.lower() for keyword in frustration_keywords):
                    return True
        
        # Check for repeated failed attempts
        if context.get("failed_attempts", 0) >= 2:
            return True
            
        # Check for sensitive topics
        sensitive_keywords = ["complaint", "legal", "lawsuit", "compensation", "GDPR", "data breach"]
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                if any(keyword in msg.content.lower() for keyword in sensitive_keywords):
                    return True
        
        return False

    def route_message(state: State) -> str:
        """Enhanced routing logic with specialized conditions."""
        try:
            # Check for immediate escalation conditions
            if should_escalate(state):
                return "HUMAN_PROXY"
            
            # Check for errors
            if state.get("error"):
                error_count = state.get("context", {}).get("error_count", 0)
                return "HUMAN_PROXY" if error_count > 2 else "CUSTOMER_SERVICE"
            
            # Check for explicit human escalation
            if state.get("action_type") == "HUMAN_ESCALATION":
                return "HUMAN_PROXY"
            
            # Get latest message
            latest_msg = next((msg for msg in reversed(state["messages"]) 
                             if isinstance(msg, HumanMessage)), None)
            if not latest_msg:
                return "CUSTOMER_SERVICE"
                
            message_lower = latest_msg.content.lower()
            
            # Check for booking-related intents with more specific patterns
            booking_patterns = {
                "FLIGHT_BOOKING": [
                    r"(book|change|cancel|modify)\s+.*flight",
                    r"(flight|plane|travel)\s+(schedule|booking|reservation)",
                    r"(departure|arrival)\s+time",
                    r"check.*in.*flight",
                    r"baggage.*flight"
                ],
                "HOTEL_BOOKING": [
                    r"(book|change|cancel)\s+.*hotel",
                    r"(hotel|room|accommodation)\s+(reservation|booking)",
                    r"check.*in.*hotel",
                    r"hotel.*availability",
                    r"place\s+to\s+stay"
                ],
                "CAR_RENTAL": [
                    r"(rent|book|reserve)\s+.*car",
                    r"(car|vehicle)\s+(rental|reservation)",
                    r"transportation.*options",
                    r"driving.*rental",
                    r"pickup.*location"
                ],
                "EXCURSION": [
                    r"(book|plan|organize)\s+.*tour",
                    r"(excursion|activity|sightseeing)",
                    r"things\s+to\s+do",
                    r"local.*attractions",
                    r"guided\s+tour"
                ]
            }
            
            # Check patterns for each booking type
            for booking_type, patterns in booking_patterns.items():
                if any(re.search(pattern, message_lower) for pattern in patterns):
                    return booking_type
            
            # Check context for ongoing booking process
            if state.get("context", {}).get("booking_intent"):
                booking_intent = state["context"]["booking_intent"]
                intent_mapping = {
                    "flight": "FLIGHT_BOOKING",
                    "hotel": "HOTEL_BOOKING",
                    "car": "CAR_RENTAL",
                    "excursion": "EXCURSION"
                }
                if booking_intent in intent_mapping:
                    return intent_mapping[booking_intent]
            
            # Check for technical support patterns
            technical_patterns = [
                r"(error|bug|issue|problem|not working)",
                r"(crash|freeze|slow|broken)",
                r"(install|setup|configure|update)",
                r"(integration|api|code|database)",
                r"(troubleshoot|debug|fix)"
            ]
            if any(re.search(pattern, message_lower) for pattern in technical_patterns):
                return "TECHNICAL"
            
            # Check for product-related patterns
            product_patterns = [
                r"(feature|spec|price|cost|compare)",
                r"(what.*product|which.*product)",
                r"(looking.*for|interested.*in)",
                r"(purchase|order|delivery)",
                r"(warranty|guarantee)"
            ]
            if any(re.search(pattern, message_lower) for pattern in product_patterns):
                return "PRODUCT"
            
            # Normal routing based on next state
            if state.get("requires_action"):
                return state.get("next", "CUSTOMER_SERVICE")
            
            return state.get("next", "CUSTOMER_SERVICE")
            
        except Exception as e:
            logger.error(f"Error in route_message: {e}")
            return "CUSTOMER_SERVICE"
    
    # Add conditional edges from router to all specialists
    workflow.add_conditional_edges(
        "ROUTER",
        route_message,
        {
            "PRODUCT": "PRODUCT",
            "TECHNICAL": "TECHNICAL",
            "CUSTOMER_SERVICE": "CUSTOMER_SERVICE",
            "HUMAN_PROXY": "HUMAN_PROXY",
            "FLIGHT_BOOKING": "FLIGHT_BOOKING",
            "HOTEL_BOOKING": "HOTEL_BOOKING",
            "CAR_RENTAL": "CAR_RENTAL",
            "EXCURSION": "EXCURSION"
        }
    )
    
    # Add edges from all specialists back to router
    specialist_nodes = [
        "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE",
        "FLIGHT_BOOKING", "HOTEL_BOOKING", "CAR_RENTAL", "EXCURSION"
    ]
    
    for node in specialist_nodes:
        workflow.add_edge(
            node, 
            "ROUTER",
            condition=lambda x: x.get("requires_action") and not should_escalate(x)
        )
        # Add direct escalation path to human proxy
        workflow.add_edge(
            node,
            "HUMAN_PROXY",
            condition=should_escalate
        )
    
    # Add edge from human proxy to end state
    workflow.add_edge("HUMAN_PROXY", "END")
    
    # Set entry point
    workflow.set_entry_point("ROUTER")
    
    return workflow.compile()

_graph_instance = None

def get_chat_graph() -> Graph:
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = create_graph()
    return _graph_instance 