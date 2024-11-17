from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, system_prompt: str = None):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE
        )
        
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

    def format_messages(self, messages: List[tuple[str, str]]) -> List[BaseMessage]:
        """Convert message tuples to LangChain message objects."""
        formatted_messages = []
        for role, content in messages:
            if role == "user":
                formatted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted_messages.append(AIMessage(content=content))
            elif role == "system":
                formatted_messages.append(SystemMessage(content=content))
        return formatted_messages

    def update_memory(self, messages: List[BaseMessage]) -> None:
        """Update conversation memory with new messages."""
        for message in messages:
            if isinstance(message, (HumanMessage, AIMessage)):
                self.memory.chat_memory.add_message(message)

    def format_context(self, context: Dict[str, Any]) -> str:
        """Format additional context for the prompt."""
        if not context:
            return "No additional context."
        return "\n".join(f"{k}: {v}" for k, v in context.items())

    async def _safe_llm_call(
        self, 
        messages: List[BaseMessage], 
        system_override: Optional[str] = None
    ) -> Optional[str]:
        """Make a safe call to the LLM with retries and error handling."""
        try:
            # Add system message at the start
            system_msg = SystemMessage(content=system_override or self.system_prompt)
            full_messages = [system_msg] + messages

            # Call LLM
            response = await self.llm.ainvoke(full_messages)
            return response.content

        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            return None

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return updated state."""
        raise NotImplementedError("Subclasses must implement process method")

    def determine_next_agent(self, response: str) -> str:
        """Determine which agent should handle the next interaction."""
        return "ROUTER"  # Default to router, override in specific agents