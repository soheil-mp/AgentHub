from typing import Dict, Any, List, Tuple
from langgraph.graph import StateGraph
from app.services.agents.router import RouterAgent
from app.services.agents.product import ProductAgent
from app.services.agents.technical import TechnicalAgent
from app.services.agents.customer_service import CustomerServiceAgent
from app.services.agents.human_proxy import HumanProxyAgent
from graphviz import Digraph
import json

def get_node_connections() -> List[Tuple[str, str]]:
    """Get the list of node connections for visualization"""
    return [
        ("ROUTER", "PRODUCT"),
        ("ROUTER", "TECHNICAL"),
        ("ROUTER", "CUSTOMER_SERVICE"),
        ("ROUTER", "HUMAN"),
        ("PRODUCT", "CUSTOMER_SERVICE"),
        ("PRODUCT", "TECHNICAL"),
        ("TECHNICAL", "PRODUCT"),
        ("TECHNICAL", "HUMAN"),
        ("CUSTOMER_SERVICE", "HUMAN"),
        ("CUSTOMER_SERVICE", "PRODUCT"),
        ("HUMAN", "ROUTER")
    ]

def visualize_graph() -> Digraph:
    """Generate a Graphviz visualization of the agent workflow"""
    dot = Digraph(comment='Agent Workflow')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Define node styles
    dot.attr('node', shape='box', style='rounded')
    
    # Add nodes
    nodes = ["ROUTER", "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", "HUMAN"]
    for node in nodes:
        dot.node(node, node)
    
    # Add edges from node connections
    for source, target in get_node_connections():
        dot.edge(source, target)
    
    return dot

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

    # Add method to get visualization
    def get_visualization(state: Dict[str, Any]) -> Dict[str, Any]:
        dot = visualize_graph()
        # Highlight current and next nodes
        current = state.get("dialog_state", "ROUTER")
        next_node = state.get("next", "ROUTER")
        
        # Update node styles based on state
        dot.node(current, current, style='filled', fillcolor='lightblue')
        if next_node != current:
            dot.node(next_node, next_node, style='filled', fillcolor='lightgreen')
        
        return {
            "dot": dot.source,
            "current_node": current,
            "next_node": next_node
        }
    
    workflow.add_node("GET_VISUALIZATION", get_visualization)

    # Set entry point
    workflow.set_entry_point("ROUTER")

    # Add method to get current graph state
    def get_graph_state(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "current_node": state.get("dialog_state", "ROUTER"),
            "next_node": state.get("next", "ROUTER"),
            "nodes": ["ROUTER", "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", "HUMAN"],
            "edges": get_node_connections(),
            "requires_action": state.get("requires_action", False)
        }

    workflow.add_node("GET_GRAPH_STATE", get_graph_state)

    return workflow.compile()

def export_graph_visualization(filepath: str = "agent_workflow.gv") -> None:
    """Export the graph visualization to a file"""
    dot = visualize_graph()
    dot.render(filepath, view=True, format='png')

class State(Dict[str, Any]):
    """Type hint for state dictionary"""
    pass 