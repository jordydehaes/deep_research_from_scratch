"""LLM-based context enhancement agent using LangGraph."""

from datetime import datetime
from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from ..core.schemas import ContextAssessment, EnhancedNetworkQuery, InvestigationContext
from ..core.state import ContextEnhancementState, ContextInputState
from ..core.prompts import (
    context_assessment_prompt, 
    final_context_generation_prompt
)


# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")


def get_conversation_history(messages) -> str:
    """Format message history for prompts."""
    return get_buffer_string(messages)


# ===== CONFIGURATION =====

# Initialize LLM model for context enhancement
# Options:
# OpenAI: "openai:gpt-4", "openai:gpt-4o", "openai:gpt-4o-mini", "openai:gpt-3.5-turbo"  
# Anthropic: "anthropic:claude-3-5-sonnet-20241022", "anthropic:claude-3-haiku-20240307"
# Google AI: "google_ai:gemini-1.5-pro", "google_ai:gemini-1.5-flash", "google_ai:gemini-2.0-flash-exp"
model = init_chat_model(model="google_genai:gemini-2.5-flash", temperature=0.1)

# Maximum enhancement iterations to prevent infinite loops
MAX_ENHANCEMENT_ITERATIONS = 5


# ===== LANGGRAPH WORKFLOW NODES =====

def assess_context(state: ContextEnhancementState) -> Command[Literal["enhance_context", "generate_final_context"]]:
    """Assess if we have sufficient context for investigation.
    
    Uses structured output to make a deterministic decision about whether
    to continue gathering context or proceed to final context generation.
    
    Args:
        state: Current context enhancement state
        
    Returns:
        Command routing to either enhancement or final context generation
    """
    # Set up structured output model for context assessment
    structured_model = model.with_structured_output(ContextAssessment)
    
    # Get conversation history for assessment
    conversation_history = get_conversation_history(state["messages"])
    
    # Assess current context completeness
    assessment = structured_model.invoke([
        HumanMessage(content=context_assessment_prompt.format(
            conversation_history=conversation_history
        ))
    ])
    
    # Route based on assessment
    if assessment.has_sufficient_context:
        # Sufficient context - proceed to final generation
        return Command(
            goto="generate_final_context",
            update={
                "messages": [AIMessage(content=f"I have sufficient context to proceed. {assessment.reasoning}")],
                "enhancement_complete": True
            }
        )
    else:
        # Need more context - continue enhancement loop
        return Command(
            goto="enhance_context", 
            update={
                "messages": [AIMessage(content=assessment.clarification_question)],
                "enhancement_iteration": state.get("enhancement_iteration", 0) + 1
            }
        )


def enhance_context(state: ContextEnhancementState) -> Command[Literal["__end__"]]:
    """Wait for user response and prepare for next assessment.
    
    This node represents the human-in-the-loop interaction point.
    In practice, this would pause the workflow for user input.
    
    Args:
        state: Current context enhancement state
        
    Returns:
        Command to end workflow (user response triggers restart)
    """
    # Check if we've exceeded maximum iterations
    current_iteration = state.get("enhancement_iteration", 0)
    
    if current_iteration >= MAX_ENHANCEMENT_ITERATIONS:
        return Command(
            goto=END,
            update={
                "messages": [AIMessage(content="I'll proceed with the context we have gathered so far.")],
                "enhancement_complete": True
            }
        )
    
    # In a real implementation, this would pause for user input
    # For now, we end here and expect the user to provide more input
    return Command(goto=END, update={})


def generate_final_context(state: ContextEnhancementState):
    """Generate final investigation context from complete conversation.
    
    Uses structured output to create comprehensive investigation context
    that will be passed to the orchestrator.
    
    Args:
        state: Current context enhancement state
        
    Returns:
        Updated state with final investigation context
    """
    # Set up structured output model for final context
    enhanced_query_model = model.with_structured_output(EnhancedNetworkQuery)
    
    # Get complete conversation history
    conversation_history = get_conversation_history(state["messages"])
    
    # Generate enhanced query structure
    enhanced_query = enhanced_query_model.invoke([
        HumanMessage(content=final_context_generation_prompt.format(
            conversation_history=conversation_history
        ))
    ])
    
    # Create final investigation context
    investigation_context = InvestigationContext(
        original_query=state.get("original_query", ""),
        enhanced_query=enhanced_query,
        conversation_history=[msg.content for msg in state["messages"] if msg.content],
        enhancement_iterations=state.get("enhancement_iteration", 0),
        ready_for_investigation=True
    )
    
    return {
        "investigation_context": investigation_context.model_dump(),
        "enhancement_complete": True,
        "messages": [AIMessage(content="Context enhancement complete. Ready to begin network investigation.")]
    }


# ===== ROUTING LOGIC =====

def should_continue_enhancement(state: ContextEnhancementState) -> Literal["assess_context", "__end__"]:
    """Determine whether to continue enhancement loop or end.
    
    Args:
        state: Current context enhancement state
        
    Returns:
        Next node to execute or END
    """
    # If enhancement is complete, end the workflow
    if state.get("enhancement_complete", False):
        return END
    
    # Continue to context assessment
    return "assess_context"


# ===== GRAPH CONSTRUCTION =====

def build_context_enhancement_graph():
    """Build the LangGraph workflow for context enhancement.
    
    Returns:
        Compiled LangGraph for context enhancement
    """
    # Build the context enhancement workflow
    builder = StateGraph(ContextEnhancementState, input_schema=ContextInputState)
    
    # Add workflow nodes
    builder.add_node("assess_context", assess_context)
    builder.add_node("enhance_context", enhance_context) 
    builder.add_node("generate_final_context", generate_final_context)
    
    # Add workflow edges
    builder.add_edge(START, "assess_context")
    builder.add_edge("enhance_context", END)  # Pauses for user input
    builder.add_edge("generate_final_context", END)
    
    # Return the builder (not compiled) so it can be compiled with different options
    return builder

def build_context_enhancement_graph_compiled():
    """Build and compile the LangGraph workflow for context enhancement.
    
    Returns:
        Compiled LangGraph for context enhancement
    """
    return build_context_enhancement_graph().compile()


# Create the context enhancement workflow
context_enhancement_workflow = build_context_enhancement_graph_compiled()