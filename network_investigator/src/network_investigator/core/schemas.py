"""Pydantic schemas for structured output in network investigation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ===== CONTEXT ENHANCEMENT SCHEMAS =====

class ContextAssessment(BaseModel):
    """LLM assessment of whether we have enough context for investigation."""
    
    has_sufficient_context: bool = Field(
        description="Whether we have enough information to proceed with network investigation"
    )
    clarification_question: str = Field(
        description="Question to ask user for missing context, empty if sufficient context"
    )
    reasoning: str = Field(
        description="Brief explanation of why more context is or isn't needed"
    )


class EnhancedNetworkQuery(BaseModel):
    """Enhanced network investigation query ready for orchestrator."""
    
    investigation_summary: str = Field(
        description="Clear summary of what needs to be investigated"
    )
    devices_mentioned: List[str] = Field(
        description="Network devices, IPs, or systems mentioned in the conversation",
        default=[]
    )
    time_context: Optional[str] = Field(
        description="When the issue occurred or time range for investigation"
    )
    incident_details: str = Field(
        description="Detailed description of symptoms, impact, and context"
    )
    investigation_priority: str = Field(
        description="Priority level: low, medium, high, critical",
        default="medium"
    )


# ===== TIME WINDOW SCHEMA =====

class TimeWindow(BaseModel):
    """Time window for investigation."""
    
    start: datetime = Field(description="Investigation start time")
    end: datetime = Field(description="Investigation end time")
    timezone: str = Field(description="Timezone for investigation", default="UTC")


# ===== FINAL CONTEXT FOR ORCHESTRATOR =====

class InvestigationContext(BaseModel):
    """Complete investigation context ready for orchestrator handoff."""
    
    original_query: str = Field(description="User's original query")
    enhanced_query: EnhancedNetworkQuery = Field(description="Enhanced investigation details")
    conversation_history: List[str] = Field(
        description="Full conversation history during enhancement",
        default=[]
    )
    enhancement_iterations: int = Field(
        description="Number of clarification rounds conducted",
        default=0
    )
    ready_for_investigation: bool = Field(
        description="Whether context is sufficient to begin investigation",
        default=True
    )