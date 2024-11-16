from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.graph import get_chat_graph, State
from app.services.state import StateManager
from app.core.config import get_settings
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    requires_action: Optional[bool] = False
    action_type: Optional[str] = None

class DetailedError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, settings = Depends(get_settings)):
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DetailedError(
                code="NO_MESSAGES",
                message="At least one message is required"
            ).dict()
        )
    
    try:
        # Initialize state manager
        state_manager = StateManager(request.user_id)
        
        # Get current state
        current_state = await state_manager.get_state()
        
        # Convert new messages to LangChain format
        new_messages = []
        for msg in request.messages:
            if msg.role == "user":
                new_messages.append(HumanMessage(content=msg.content))
            else:
                new_messages.append(AIMessage(content=msg.content))
        
        # Update state with new messages
        current_state["messages"].extend(new_messages)
        current_state["context"].update(request.context)
        
        # Get graph and process
        graph = get_chat_graph()
        result = await graph.ainvoke(current_state)
        
        # Save updated state
        await state_manager.update_state(result)
        
        # Convert result back to API format
        response_messages = []
        for msg in result["messages"]:
            if isinstance(msg, (HumanMessage, AIMessage)):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                response_messages.append(
                    ChatMessage(role=role, content=msg.content)
                )
        
        return ChatResponse(
            messages=response_messages,
            requires_action=result.get("requires_action", False),
            action_type=result.get("action_type")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=DetailedError(
                code="PROCESSING_ERROR",
                message="Error processing chat request",
                details={"error": str(e)}
            ).dict()
        ) 