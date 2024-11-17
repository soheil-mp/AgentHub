from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1)
    user_id: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    messages: List[Message]
    next: Optional[str] = None
    requires_action: bool = False
    dialog_state: List[str] = Field(default_factory=list) 