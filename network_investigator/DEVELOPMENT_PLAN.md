# Network Investigator Development Plan

## Overview
Building a multi-agent Network Investigator system that uses MCP servers for Prometheus, Graylog, and Infrahub integration. The system follows a phase-by-phase approach with incremental testing.

## Architecture Decisions
- **MCP Integration**: Use existing MCP servers for all three network tools
- **Context Enhancement**: Human-in-the-loop iterative clarification
- **Multi-Agent Coordination**: Parallel investigation for complex incidents
- **Safety First**: Tool budgets, timeouts, and graceful failure handling

---

## Phase 1: Context Enhancement Loop (Week 1)
**Goal**: Build the human-in-the-loop context enhancement system

### Step 1.1: Project Setup & Basic Structure
- Create repository structure
- Set up basic dependencies (LangGraph, LangChain, MCP adapters)
- Create initial state definitions for context enhancement
- **Test**: Basic project runs without errors

### Step 1.2: Query Classification System
```python
class NetworkQuery(BaseModel):
    raw_query: str
    devices_mentioned: List[str]
    timeframe_mentioned: Optional[str]
    additional_remarks: Optional[str]  # Extra context, not hints

class ContextEnhancementDecision(BaseModel):
    needs_clarification: bool
    missing_info: List[str]  # ["timeframe", "specific_devices", "incident_details"]
    clarification_question: str
    confidence: float
```
- **Test**: Classification correctly identifies missing information from sample queries

### Step 1.3: Context Enhancement Agent
- Build the LangGraph workflow for iterative clarification
- Implement the enhancement loop with exit conditions
- Add structured output for decision making
- **Test**: Agent correctly asks follow-up questions and knows when to stop

### Step 1.4: Enhanced Context Output
```python
class EnhancedInvestigationContext(BaseModel):
    original_query: str
    enhanced_description: str
    time_window: TimeWindow
    target_devices: List[str]
    additional_context: str  # Any extra remarks or context
```
- **Test**: Complete context enhancement flow produces structured output

---

## Phase 2: MCP Tool Integration (Week 2)
**Goal**: Set up and test all three MCP tool connections

### Step 2.1: MCP Client Configuration
```python
mcp_config = {
    "prometheus": {
        "command": "mcp-server-prometheus",
        "args": ["--config", "/path/to/prometheus-config.json"],
        "transport": "stdio"
    },
    "graylog": {
        "command": "mcp-server-graylog", 
        "args": ["--config", "/path/to/graylog-config.json"],
        "transport": "stdio"
    },
    "infrahub": {
        "command": "mcp-server-infrahub",
        "args": ["--config", "/path/to/infrahub-config.json"], 
        "transport": "stdio"
    }
}
```
- Set up MCP client connections to all three servers
- **Test**: Can successfully connect and list available tools from each server

### Step 2.2: Tool Integration Testing
- Create test queries for each tool type
- Implement basic tool response parsing
- Add error handling for tool failures
- **Test**: Each MCP tool returns expected data format

### Step 2.3: Tool Budget & Safety Mechanisms
- Implement tool call limits per investigation
- Add timeout handling for slow MCP responses
- Create tool result compression helpers
- **Test**: Tools respect budgets and handle failures gracefully

---

## Phase 3: Single Investigation Agent (Week 3)
**Goal**: Build a single agent that can investigate using MCP tools

### Step 3.1: Investigation Agent Core
```python
class InvestigationAgent:
    def __init__(self, investigation_context: EnhancedInvestigationContext):
        self.context = investigation_context
        self.evidence_collected = []
        self.tool_call_count = 0
        self.max_tool_calls = 8
```
- Build basic agent structure with LangGraph
- Implement tool selection logic based on investigation type
- **Test**: Agent can make appropriate tool choices

### Step 3.2: Evidence Collection Loop
- Implement iterative investigation pattern (Query → Think → Analyze → Continue/Stop)
- Add evidence compression after each tool call
- Implement termination conditions
- **Test**: Agent collects sufficient evidence and stops appropriately

### Step 3.3: Evidence Synthesis
```python
class EvidenceSummary(BaseModel):
    timeline: List[TimelineEvent]
    key_findings: List[str]
    confidence_score: float
    evidence_sources: List[str]
    investigation_complete: bool
```
- Build evidence summarization logic
- Create structured output for investigation results
- **Test**: Agent produces coherent evidence summaries

---

## Phase 4: Lead Orchestrator (Week 4)
**Goal**: Build the orchestrator that receives enhanced context and coordinates investigation

### Step 4.1: Investigation Planning
```python
class InvestigationPlan(BaseModel):
    investigation_strategy: str  # "single_agent" or "multi_agent"
    required_evidence_types: List[str]  # ["metrics", "logs", "topology"]
    subagent_tasks: List[SubagentTask]
    estimated_complexity: str
```
- Build planning logic that decides investigation approach
- Implement task decomposition for complex incidents
- **Test**: Orchestrator creates appropriate investigation plans

### Step 4.2: Single Agent Coordination
- Integrate Phase 3 investigation agent with orchestrator
- Handle simple incidents with single agent
- Pass enhanced context properly to investigation agent
- **Test**: End-to-end flow from context enhancement → orchestration → investigation

### Step 4.3: Investigation Result Processing
- Collect results from investigation agent
- Implement basic result validation
- Create investigation status tracking
- **Test**: Orchestrator properly handles investigation completion

---

## Phase 5: Multi-Agent Coordination (Week 5)
**Goal**: Enable parallel investigation for complex incidents

### Step 5.1: Subagent Task Definition
```python
class SubagentTask(BaseModel):
    task_id: str
    objective: str
    evidence_type: str  # "metrics", "logs", "topology"
    tools_allowed: List[str]
    tool_budget: int
    time_priority: bool  # high priority for time-sensitive evidence
```
- Define task structure for subagents
- Implement task allocation logic
- **Test**: Complex incidents generate appropriate subtasks

### Step 5.2: Parallel Agent Execution
- Implement async coordination of multiple investigation agents
- Add agent pool management
- Handle partial failures gracefully
- **Test**: Multiple agents execute in parallel and return results

### Step 5.3: Evidence Correlation
- Build evidence correlation logic across multiple agents
- Implement timeline alignment for events from different sources
- Add confidence scoring for correlated evidence
- **Test**: Multi-agent evidence gets properly correlated

---

## Phase 6: Integration & Testing (Week 6)
**Goal**: Complete end-to-end system with comprehensive testing

### Step 6.1: Complete Workflow Integration
- Connect all phases into single workflow
- Implement proper state transitions
- Add comprehensive error handling
- **Test**: Full system handles various incident types correctly

### Step 6.2: Mock Data & Test Scenarios
```python
test_scenarios = [
    {
        "name": "Simple Device Down", 
        "query": "Router X is down",
        "expected_agents": 1,
        "expected_tools": ["infrahub", "prometheus"]
    },
    {
        "name": "Complex Multi-Site Issue",
        "query": "Connectivity problems between sites A and B", 
        "expected_agents": 3,
        "expected_tools": ["prometheus", "graylog", "infrahub"]
    }
]
```
- Create comprehensive test scenarios
- Build mock MCP responses for testing
- Implement evaluation metrics
- **Test**: System passes all scenario tests

### Step 6.3: Performance & Safety Validation
- Test tool budget compliance
- Validate MCP connection handling
- Test timeout and error scenarios
- **Test**: System behaves safely under various failure conditions

---

## Testing Strategy Per Phase

### Unit Tests: Each component in isolation
- State transitions work correctly
- Tool integrations return expected formats
- Agent decision making follows logic

### Integration Tests: Component interactions
- Context enhancement → orchestrator handoff
- Orchestrator → agent coordination  
- Agent → MCP tool communication

### End-to-End Tests: Complete workflows
- Simple incident investigation
- Complex multi-agent investigation
- Error handling and recovery

### Safety Tests: Production readiness
- Tool budget enforcement
- MCP connection failure handling
- Investigation timeout scenarios

---

## Current Status
- **Phase 1**: In Progress
- **Next Steps**: Complete context enhancement loop implementation