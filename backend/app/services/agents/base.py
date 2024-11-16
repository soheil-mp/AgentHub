from typing import Dict, Any, List, Tuple, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.cache import InMemoryCache
from app.core.config import settings
import logging
import asyncio
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = datetime.now()
            # Remove calls older than 1 minute
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < timedelta(minutes=1)]
            
            if len(self.calls) >= self.calls_per_minute:
                sleep_time = 60 - (now - self.calls[0]).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.calls.append(now)

class BaseAgent:
    # Shared rate limiter for all instances
    _rate_limiter = RateLimiter(calls_per_minute=60)
    # Shared LLM cache
    _llm_cache = InMemoryCache()
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_retries: int = 3,
        system_prompt: Optional[str] = None,
        cache_ttl: int = 3600  # Cache TTL in seconds
    ):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY,
            max_retries=max_retries,
            cache=self._llm_cache
        )
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )
        self.system_prompt = system_prompt
        self.cache_ttl = cache_ttl
        
    @lru_cache(maxsize=1000)
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available."""
        return None  # Implement actual cache lookup
        
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache response for future use."""
        pass  # Implement actual caching
        
    def format_messages(self, messages: List[Tuple[str, str]]) -> List[BaseMessage]:
        """Format messages for the LLM with proper message types."""
        formatted_messages = []
        
        # Add system prompt if available
        if self.system_prompt:
            formatted_messages.append(SystemMessage(content=self.system_prompt))
        
        # Add conversation history
        for role, content in messages:
            try:
                if role == "user":
                    formatted_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    formatted_messages.append(AIMessage(content=content))
                elif role == "system":
                    formatted_messages.append(SystemMessage(content=content))
                else:
                    logger.warning(f"Unknown message role: {role}")
            except Exception as e:
                logger.error(f"Error formatting message: {e}")
                continue
                
        return formatted_messages

    def update_memory(self, messages: List[BaseMessage]) -> None:
        """Update conversation memory with new messages."""
        try:
            for message in messages:
                if isinstance(message, (HumanMessage, AIMessage)):
                    self.memory.chat_memory.add_message(message)
        except Exception as e:
            logger.error(f"Error updating memory: {e}")

    def get_memory_messages(self) -> List[BaseMessage]:
        """Retrieve messages from memory."""
        try:
            return self.memory.chat_memory.messages
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return []

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        try:
            self.memory.clear()
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return updated state."""
        raise NotImplementedError("Subclasses must implement process method")

    async def _safe_llm_call(
        self,
        messages: List[BaseMessage],
        system_override: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """Safely make LLM API calls with error handling, rate limiting, and caching."""
        try:
            # Generate cache key
            cache_key = str(hash(str(messages) + str(system_override)))
            
            # Check cache first if enabled
            if use_cache:
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    logger.debug("Cache hit for key: %s", cache_key)
                    return cached_response
            
            # Apply rate limiting
            await self._rate_limiter.acquire()
            
            if system_override:
                messages = [SystemMessage(content=system_override)] + messages

            response = await self.llm.ainvoke(messages)
            
            # Cache the response if enabled
            if use_cache:
                self._cache_response(cache_key, response.content)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            return None

    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string."""
        try:
            return "\n".join(f"{k}: {v}" for k, v in context.items())
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return "No additional context provided"