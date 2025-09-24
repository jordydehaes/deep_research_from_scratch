"""State definitions for LangGraph workflows."""

import operator
from typing import Annotated, List, Optional, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# ===== CONTEXT ENHANCEMENT STATES =====

class ContextEnhancementState(TypedDict):
    """State for the context enhancement workflow."""
    
    # Message history for conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Original user query
    original_query: str
    
    # Current enhancement iteration
    enhancement_iteration: int
    
    # Whether enhancement is complete
    enhancement_complete: bool
    
    # Final enhanced context when complete
    investigation_context: Optional[dict]


class ContextInputState(TypedDict):
    """Input state - just the initial user query."""
    
    messages: Annotated[Sequence[BaseMessage], add_messages]