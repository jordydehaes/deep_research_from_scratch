# Network Investigator

Multi-agent network troubleshooting system using LangGraph and MCP servers.

## Setup

### 1. Install Dependencies

```bash
# Basic installation (for structure testing)
pip install -e .

# Full installation with LLM dependencies (for actual testing)
pip install -e .[llm]

# Development installation
pip install -e .[llm,dev]
```

### 2. Environment Variables

Create `.env` file (at least one API key required):

```env
# LLM API Keys - Choose one or more
OPENAI_API_KEY=your_openai_api_key_here          # For GPT models
ANTHROPIC_API_KEY=your_anthropic_api_key_here    # For Claude models
GOOGLE_API_KEY=your_google_api_key_here          # For Gemini models

# Optional: For tracing and evaluation
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=network_investigator
```

### Supported Models

The system supports multiple LLM providers via LangChain's `init_chat_model`:

**OpenAI Models:**
- `openai:gpt-4` - Most capable, higher cost
- `openai:gpt-4o` - Balanced performance and speed
- `openai:gpt-4o-mini` - Fast and cost-effective (current default)
- `openai:gpt-3.5-turbo` - Budget option

**Anthropic Models:**
- `anthropic:claude-3-5-sonnet-20241022` - Excellent reasoning
- `anthropic:claude-3-haiku-20240307` - Fast and economical

**Google AI Models:**
- `google_ai:gemini-1.5-pro` - High capability, longer context
- `google_ai:gemini-1.5-flash` - Fast and efficient
- `google_ai:gemini-2.0-flash-exp` - Latest experimental version

To change models, edit line 38 in `src/network_investigator/agents/context_enhancer.py`

### 3. Test the Implementation

```bash
# Test architecture without LLM calls (works without API keys)
python test_llm_context_enhancer.py

# Test with actual LLM (requires API keys and pip install -e .[llm])
python examples/test_context_enhancement.py
```

## Phase 1: Context Enhancement

The context enhancement system follows the deep research patterns:

- **LLM-based decision making**: Agent decides when enough context is gathered
- **LangGraph workflow**: Command routing with structured output
- **Human-in-the-loop**: Iterative clarification until LLM satisfaction
- **Structured output**: Pydantic schemas for deterministic workflow

### Workflow

```
User Query → assess_context → [sufficient?] → generate_final_context → Orchestrator
                    ↓ [insufficient]
            enhance_context → [user response] → loop back
```

### Example Usage

```python
from network_investigator.agents.context_enhancer import context_enhancement_workflow
from langchain_core.messages import HumanMessage

# Start enhancement
result = context_enhancement_workflow.invoke({
    "messages": [HumanMessage(content="Router is down")],
    "original_query": "Router is down",
    "enhancement_iteration": 0,
    "enhancement_complete": False
})

# Check if needs clarification
if not result.get("enhancement_complete"):
    print("Agent asks:", result["messages"][-1].content)
    # User responds, workflow continues...
else:
    print("Context complete:", result.get("investigation_context"))
```

## File Structure

```
network_investigator/
├── src/network_investigator/
│   ├── core/
│   │   ├── schemas.py          # Pydantic models for structured output
│   │   ├── state.py           # LangGraph state definitions
│   │   └── prompts.py         # LLM prompts for network ops
│   ├── agents/
│   │   └── context_enhancer.py # LLM-based LangGraph workflow
│   └── utils/
│       └── helpers.py         # Utility functions
├── examples/
│   └── test_context_enhancement.py # Working example
└── test_llm_context_enhancer.py   # Architecture validation
```