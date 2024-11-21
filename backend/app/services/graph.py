from typing import Dict, Any, List, Tuple
from langgraph.graph import StateGraph
from app.services.agents import (
    AssistantAgent,
    FlightBookingAgent,
    HotelBookingAgent,
    CarRentalAgent,
    ExcursionAgent,
    SensitiveWorkflowAgent
)
from graphviz import Digraph
import json

def get_node_connections() -> List[Tuple[str, str]]:
    """Get the list of node connections for visualization"""
    return [
        ("ASSISTANT", "FLIGHT"),
        ("ASSISTANT", "HOTEL"),
        ("ASSISTANT", "CAR_RENTAL"),
        ("ASSISTANT", "EXCURSION"),
        ("ASSISTANT", "SENSITIVE"),
        ("FLIGHT", "ASSISTANT"),
        ("HOTEL", "ASSISTANT"),
        ("CAR_RENTAL", "ASSISTANT"),
        ("EXCURSION", "ASSISTANT"),
        ("SENSITIVE", "ASSISTANT")
    ]

def get_chat_graph() -> StateGraph:
    # Initialize agents
    assistant = AssistantAgent()
    flight = FlightBookingAgent()
    hotel = HotelBookingAgent()
    car_rental = CarRentalAgent()
    excursion = ExcursionAgent()
    sensitive = SensitiveWorkflowAgent()

    # Create state graph
    workflow = StateGraph(name="Travel Assistant Workflow")

    # Add nodes
    workflow.add_node("ASSISTANT", assistant.invoke)
    workflow.add_node("FLIGHT", flight.invoke)
    workflow.add_node("HOTEL", hotel.invoke)
    workflow.add_node("CAR_RENTAL", car_rental.invoke)
    workflow.add_node("EXCURSION", excursion.invoke)
    workflow.add_node("SENSITIVE", sensitive.invoke)

    # Define conditional routing
    def should_route(state: Dict[str, Any]) -> str:
        next_agent = state.get("next", "ASSISTANT")
        # If no specific next agent is set, return to assistant
        return next_agent if next_agent != "NONE" else "ASSISTANT"

    # Add edges with conditional routing
    workflow.add_edge("ASSISTANT", should_route)
    workflow.add_edge("FLIGHT", should_route)
    workflow.add_edge("HOTEL", should_route)
    workflow.add_edge("CAR_RENTAL", should_route)
    workflow.add_edge("EXCURSION", should_route)
    workflow.add_edge("SENSITIVE", should_route)

    # Set entry point
    workflow.set_entry_point("ASSISTANT")

    return workflow.compile()

def export_graph_visualization(filepath: str = "agent_workflow.gv") -> None:
    """Export the graph visualization to a file"""
    dot = visualize_graph()
    dot.render(filepath, view=True, format='png')

def visualize_graph() -> Digraph:
    """Create a visualization of the agent workflow"""
    dot = Digraph(comment='Agent Workflow')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Add nodes
    dot.node('ASSISTANT', 'Assistant\nAgent', shape='circle')
    dot.node('FLIGHT', 'Flight\nBooking', shape='box')
    dot.node('HOTEL', 'Hotel\nBooking', shape='box')
    dot.node('CAR_RENTAL', 'Car\nRental', shape='box')
    dot.node('EXCURSION', 'Excursion\nBooking', shape='box')
    dot.node('SENSITIVE', 'Sensitive\nWorkflow', shape='diamond')
    
    # Add edges
    for source, target in get_node_connections():
        dot.edge(source, target)
    
    return dot

class State(Dict[str, Any]):
    """Type hint for state dictionary"""
    pass 