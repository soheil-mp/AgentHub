from typing import Dict, Any
from langgraph.graph import StateGraph
from app.services.agents.router import RouterAgent
from app.services.agents.product import ProductAgent
from app.services.agents.technical import TechnicalAgent
from app.services.agents.customer_service import CustomerServiceAgent
from app.services.agents.human_proxy import HumanProxyAgent

def get_chat_graph() -> StateGraph:
    # Initialize agents
    router = RouterAgent()
    product = ProductAgent()
    technical = TechnicalAgent()
    customer_service = CustomerServiceAgent()
    human_proxy = HumanProxyAgent()

    # Create state graph
    workflow = StateGraph(name="Customer Support Workflow")

    # Add nodes
    workflow.add_node("ROUTER", router.invoke)
    workflow.add_node("PRODUCT", product.invoke)
    workflow.add_node("TECHNICAL", technical.invoke)
    workflow.add_node("CUSTOMER_SERVICE", customer_service.invoke)
    workflow.add_node("HUMAN", human_proxy.invoke)

    # Define conditional routing
    def should_route(state: Dict[str, Any]) -> str:
        return state.get("next", "ROUTER")

    # Add edges with conditional routing
    workflow.add_edge("ROUTER", should_route)
    workflow.add_edge("PRODUCT", should_route)
    workflow.add_edge("TECHNICAL", should_route)
    workflow.add_edge("CUSTOMER_SERVICE", should_route)
    workflow.add_edge("HUMAN", should_route)

    # Set entry point
    workflow.set_entry_point("ROUTER")

    return workflow.compile()

class State(Dict[str, Any]):
    """Type hint for state dictionary"""
    pass 