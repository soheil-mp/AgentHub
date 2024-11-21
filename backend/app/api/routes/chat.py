from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from app.services.graph import get_chat_graph, State, visualize_graph
from app.services.state import StateManager
from app.core.config import get_settings, settings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.core.exceptions import ValidationError, AgentError
from app.services.rate_limit import RateLimiter
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
rate_limiter = RateLimiter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GraphState(BaseModel):
    current_node: str
    next_node: str
    nodes: List[str]
    edges: List[Tuple[str, str]]
    requires_action: bool

class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    requires_action: Optional[bool] = False
    action_type: Optional[str] = None
    graph_state: Optional[GraphState] = None

def get_chat_model():
    """Initialize and return the chat model."""
    try:
        model = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        return model
    except Exception as e:
        logger.error(f"Error initializing chat model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "MODEL_INITIALIZATION_ERROR",
                "message": "Failed to initialize chat model"
            }
        )

@router.get("/graph/structure")
async def get_graph_structure():
    """Get the graph structure for visualization"""
    try:
        # Create a static graph structure
        graph_state = GraphState(
            current_node="ROUTER",
            next_node="",
            nodes=["ROUTER", "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", "HUMAN"],
            edges=[
                ["ROUTER", "PRODUCT"],
                ["ROUTER", "TECHNICAL"],
                ["ROUTER", "CUSTOMER_SERVICE"],
                ["ROUTER", "HUMAN"],
                ["PRODUCT", "CUSTOMER_SERVICE"],
                ["PRODUCT", "TECHNICAL"],
                ["TECHNICAL", "PRODUCT"],
                ["TECHNICAL", "HUMAN"],
                ["CUSTOMER_SERVICE", "HUMAN"],
                ["CUSTOMER_SERVICE", "PRODUCT"],
                ["HUMAN", "ROUTER"]
            ],
            requires_action=False
        )

        # Log the response for debugging
        logger.debug(f"Graph structure response: {graph_state.model_dump()}")

        # Return the Pydantic model
        return graph_state

    except Exception as e:
        logger.error(f"Error getting graph structure: {e}", exc_info=True)  # Added exc_info for full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get graph structure"
        )

@router.post("/")
async def chat(request: ChatRequest):
    """Process chat messages and return response"""
    try:
        # Log the incoming request for debugging
        logger.debug(f"Received chat request: {request}")
        
        # Initialize chat model
        chat_model = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )

        # Validate messages
        if not request.messages:
            raise ValidationError(
                message="No messages provided",
                details={"code": "NO_MESSAGES"}
            )

        # Get the last message only
        last_message = request.messages[-1]
        
        # Convert to LangChain format
        langchain_messages = [HumanMessage(content=last_message.content)]

        # Get response from model
        response = await chat_model.ainvoke(langchain_messages)

        # Format response
        result = {
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in request.messages
            ] + [{"role": "assistant", "content": response.content}],
            "requires_action": False,
            "graph_state": {
                "current_node": "ROUTER",
                "next_node": "",
                "nodes": ["ROUTER", "PRODUCT", "TECHNICAL", "CUSTOMER_SERVICE", "HUMAN"],
                "edges": [
                    ["ROUTER", "PRODUCT"],
                    ["ROUTER", "TECHNICAL"],
                    ["ROUTER", "CUSTOMER_SERVICE"],
                    ["ROUTER", "HUMAN"]
                ],
                "requires_action": False
            }
        }

        # Log the response for debugging
        logger.debug(f"Chat response: {result}")

        return JSONResponse(content=result)

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"code": e.code, "message": str(e), **e.details}}
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )

@router.get("/visualization")
async def get_graph_visualization():
    """Get the current graph visualization"""
    try:
        dot = visualize_graph()
        return JSONResponse({
            "dot": dot.source,
            "format": "dot"
        })
    except Exception as e:
        logger.error(f"Error generating graph visualization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate graph visualization"
        ) 