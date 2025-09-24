"""Interactive test - try your own network queries!"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

# Import our context enhancement workflow
from network_investigator.agents.context_enhancer import context_enhancement_workflow


def interactive_context_enhancement():
    """Interactive test where you can input your own queries."""
    
    print("🚀 INTERACTIVE NETWORK INVESTIGATION CONTEXT ENHANCEMENT")
    print("=" * 60)
    print("Enter a network query and watch the LLM enhancement process!")
    print("Examples:")
    print("  - 'Network is slow'")
    print("  - 'Router down'") 
    print("  - 'Router core-01 went down 2 hours ago'")
    print("  - 'Issues'")
    print()
    
    # Get user input
    query = input("Enter your network query: ").strip()
    
    if not query:
        print("No query entered. Exiting.")
        return
    
    print(f"\n🔍 Processing: '{query}'")
    print("=" * 50)
    
    # Use checkpointer for conversation continuity
    checkpointer = InMemorySaver()
    from network_investigator.agents.context_enhancer import build_context_enhancement_graph
    workflow_with_memory = build_context_enhancement_graph().compile(checkpointer=checkpointer)
    
    thread = {"configurable": {"thread_id": "interactive_test"}}
    
    # Start the enhancement process
    result = workflow_with_memory.invoke({
        "messages": [HumanMessage(content=query)],
        "original_query": query,
        "enhancement_iteration": 0,
        "enhancement_complete": False
    }, config=thread)
    
    print(f"🤖 Agent Response: {result['messages'][-1].content}")
    
    # Check if enhancement is complete
    if result.get("enhancement_complete"):
        print("\n✅ Context is sufficient! Here's the final investigation context:")
        if result.get("investigation_context"):
            context = result["investigation_context"]
            enhanced = context['enhanced_query']
            
            print(f"\n📋 INVESTIGATION SUMMARY:")
            print(f"   {enhanced['investigation_summary']}")
            print(f"\n🎯 DETAILS:")
            print(f"   Devices: {enhanced['devices_mentioned']}")
            print(f"   Timeline: {enhanced.get('time_context', 'Not specified')}")  
            print(f"   Priority: {enhanced['investigation_priority']}")
            print(f"\n📝 INCIDENT DETAILS:")
            print(f"   {enhanced['incident_details']}")
            
        print(f"\n🚀 Ready to hand off to orchestrator!")
        return
    
    # If not complete, continue the conversation
    iteration = 1
    max_iterations = 5
    
    while not result.get("enhancement_complete") and iteration < max_iterations:
        print(f"\n--- Iteration {iteration} ---")
        
        # Get user response
        user_response = input("👤 Your response: ").strip()
        
        if not user_response:
            print("No response provided. Ending conversation.")
            break
            
        # Continue conversation
        result = workflow_with_memory.invoke({
            "messages": [HumanMessage(content=user_response)]
        }, config=thread)
        
        print(f"🤖 Agent: {result['messages'][-1].content}")
        
        # Check if complete now
        if result.get("enhancement_complete"):
            print("\n✅ Context enhancement complete!")
            if result.get("investigation_context"):
                context = result["investigation_context"]
                enhanced = context['enhanced_query']
                
                print(f"\n📋 FINAL INVESTIGATION CONTEXT:")
                print(f"   Summary: {enhanced['investigation_summary']}")
                print(f"   Devices: {enhanced['devices_mentioned']}")
                print(f"   Timeline: {enhanced.get('time_context', 'Not specified')}")
                print(f"   Priority: {enhanced['investigation_priority']}")
                print(f"   Iterations: {context['enhancement_iterations']}")
            
            print(f"\n🚀 Ready for orchestrator!")
            break
            
        iteration += 1
    
    if iteration >= max_iterations:
        print(f"\n⏰ Reached maximum iterations ({max_iterations})")
        print("Enhancement process would continue with available context.")


if __name__ == "__main__":
    # Check for API key
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ No LLM API keys found!")
        print("Please set one of these in your .env file:")
        print("  - OPENAI_API_KEY (for OpenAI models)")
        print("  - ANTHROPIC_API_KEY (for Claude models)")  
        print("  - GOOGLE_API_KEY (for Gemini models)")
        exit(1)
    
    try:
        interactive_context_enhancement()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you've installed LLM dependencies: pip3 install -e .[llm]")