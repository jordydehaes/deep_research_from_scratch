## Narrative overview
In this system, we build a multi-agent “Network Investigator” designed to answer questions about outages, performance degradations, and network topology. The architecture is inspired by Anthropic’s multi-agent research model, but adapted to the unique constraints of our network  environment.

At a high level, the system transforms a user query into a structured investigation. The process flows through several distinct phases, each with a clear responsibility and boundary.

---

## Process description
### 1. User Query Intake
A user submits a free-form query, such as:

>  “Routers X and Y went down at timestamp Z, what happened?” 

The query can be vague, incomplete, or contain ambiguous device names. The system must refine this into a clear investigation plan. Crucially, the Lead agent does not jump straight into metrics or logs at this stage.

---

### 2. Context Building with Human-In-The-Loop
The first step after parsing the query is **context building**, which is handled by a a human-in-the-loop. This part is responsible for constructing the needed network context for the query, by makin sure we have a time frame, roughly devices or more details if possible.

This ensures that the lead orchestrator is better informed and works with good information

---

### 3. Planning (Lead Orchestrator)
Once the query has been enhanced, it is handed off to the **Lead Orchestrator** agent.

Using the context, the Lead performs several tasks:

- Classifies the type of query (simple fact, local incident, or complex multi-site issue)
- Sets a time window for investigation (from query timestamps or recent alerts)
- Decides how many subagents to spawn in and what tasks they should perform
- Allocates budgets (tool call limits)
The Lead then writes **detailed subagent task descriptions**, specifying:

- Objective (one clear goal per subagent)
- Relevant selectors
- Allowed tools (Prometheus, Graylog, or Infrahub)
- Expected outputs (summaries, artifacts, confidence)
The Lead itself never performs deep research; it only plans and later synthesizes.

---

### 4. Parallel Subagent Execution
The Lead launches multiple subagents in parallel to collect evidence, they have access to pre-defined tools such as Prometheus, Graylog and Infrahub to collect information.

Subagents are generalist agents, but they operate within strict, clear task instructions and may call their tools multiple times. They use **interleaved thinking, **after each tool result, they reflect, adjust, and refine their queries until they reach sufficient confidence or exhaust their budget.

Each subagent returns:

- A concise textual summary
- A confidence score
- A list of artifacts possibly
---

### 5. Synthesis and RCA Generation
When the subagents complete their tasks, the Lead collects all results and synthesizes them. It compares metrics and logs:

- If both point to the same fault, it compiles a timeline and root cause hypothesis.
- If they conflict or are uncertain, it may spawn a targeted follow-up Probe subagent to collect additional evidence.
Finally, the Lead writes the investigation report:

- A human-readable timeline of events
- The most likely root cause and impact
- Supporting evidence and artifacts
- Confidence estimate
- Recommended next steps
---

### 6. Output and Persistence
The completed report, along with all artifact references, is stored as a **case record**. This enables follow-up queries to reuse the context without repeating the Infrahub discovery step.
---

## Summary
This design enforces a clean separation of concerns:

- **Context Enhancer with Human in the loop**: enhances and makes the initial query complete
- **Lead**: plans, orchestrates, and synthesizes (no raw data collection)
- **Subagents**: execute iterative evidence collection (Prometheus, Graylog, Infrahub)
By ensuring every investigation begins with a solid understanding of the query, we minimize wasted tool calls, align all subagents on the same identifiers, and produce accurate, auditable RCA reports. This architecture scales from small one-device checks to wide multi-site incidents with clear guardrails and modularity.

