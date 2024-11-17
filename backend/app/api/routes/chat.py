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

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rate_limit: bool = Depends(rate_limiter.check_rate_limit)
):
    try:
        # Initialize chat model
        chat_model = get_chat_model()

        # Validate messages
        if not request.messages:
            raise ValidationError(
                message="No messages provided",
                details={"code": "NO_MESSAGES"}
            )

        # Convert messages to LangChain format
        langchain_messages = []
        for msg in request.messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))

        # Get response from model
        response = await chat_model.ainvoke(langchain_messages)

        # Format response
        result = {
            "messages": [
                *request.messages,
                ChatMessage(role="assistant", content=response.content)
            ],
            "requires_action": False
        }

        # Store in state if needed
        state_manager = StateManager(request.user_id)
        await state_manager.update_state({
            "messages": [(msg.role, msg.content) for msg in result["messages"]],
            "context": request.context
        })

        return result

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": str(e), **e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)}
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