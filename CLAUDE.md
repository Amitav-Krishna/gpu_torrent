# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Overview

GPU Torrent is a distributed ML inference system that routes inference requests to GPU workers. The system uses Redis for job queuing and result storage, with Ollama as the inference backend.

## Architecture

```
┌─────────────┐     ┌────────────────────┐     ┌────────────────┐
│   Client    │────▶│  Server/Coordinator │────▶│  GPU Workers   │
│ (src/client)│     │   (src/server)      │     │  (src/worker)  │
└─────────────┘     └────────────────────┘     └────────────────┘
                              │                        │
                              └───────Redis────────────┘
```

**Three main components:**

1. **Server (Coordinator)** - `src/server/main.py`: FastAPI app that handles worker registration, job routing (round-robin), and result retrieval. Stores worker registry and job queues in Redis.

2. **Worker** - `src/worker/main.py`: Registers with coordinator on startup, loads Ollama models, and consumes jobs from Redis queue. Components:
   - `queue/consumer.py`: Redis BRPOP consumer loop
   - `inference/inference.py`: Ollama inference execution
   - `loader/model_loader.py`: Model availability check and pull

3. **Client** - `src/client/api.py`: APIClient class for submitting inference jobs and polling for results.

## Key Environment Variables

| Variable | Component | Default | Description |
|----------|-----------|---------|-------------|
| `REDIS_HOST` | Server | `localhost` | Redis server host |
| `REDIS_PORT` | Server | `6379` | Redis server port |
| `COORDINATOR_URL` | Worker | `http://localhost:8000` | Coordinator endpoint |
| `REDIS_URL` | Worker | `redis://localhost:6379` | Redis connection URL |
| `MODEL_NAME` | Worker | `llama3.2` | Ollama model to load |
| `HF_TOKEN` | Worker | - | HuggingFace token for gated models |

## Redis Data Structure

- `worker:{worker_id}` - Worker registration data (JSON)
- `queue:{worker_id}` - Job queue for specific worker (list)
- `result:{request_id}` - Inference result storage (JSON)
- `worker_index` - Round-robin counter for load balancing

## API Endpoints (Coordinator)

- `POST /register` - Worker registration
- `GET /workers` - List registered workers
- `POST /inference` - Submit inference job
- `GET /result/{request_id}` - Retrieve job result

## Data Flow

1. Worker starts → registers with coordinator → starts Redis consumer loop
2. Client submits `InferenceRequest` to `/inference`
3. Coordinator finds compatible worker, pushes job to `queue:{worker_id}`
4. Worker BRPOP from queue, executes via Ollama, stores result at `result:{request_id}`
5. Client polls `/result/{request_id}` until available

# Behaviour

## Agents

Use subagents whenever possible. They provide focused execution, cleaner context separation, and better results for specialized tasks.

### Plan

Use for architecture design, implementation planning, and technical exploration. The agent should research, analyze trade-offs, and produce actionable plans.

**Description examples:**
- "Design real-time worker dashboard"
- "Decentralize coordinator architecture"
- "Design distributed parallel inference"

**Prompt structure:**

```
Context: [Current state and why change is needed]

Exploration Tasks:
1. [Examine existing code/architecture]
2. [Research relevant patterns/technologies]
3. [Identify constraints and dependencies]

Analysis Required:
- [Trade-off 1 to evaluate]
- [Trade-off 2 to evaluate]
- [Technical challenges to address]

Deliverables:
- Recommended approach with justification
- Architecture diagram or component breakdown
- Files to modify/create
- Step-by-step implementation plan
- Migration strategy (if applicable)
```

**Example prompts:**

*Real-time worker dashboard:*
```
Context: Users need visibility into worker status, job queues, and inference metrics. Currently no monitoring UI exists.

Exploration Tasks:
1. Examine src/server/main.py for available worker data and endpoints
2. Identify what metrics are stored in Redis (worker:{id}, queue:{id} keys)
3. Research real-time web patterns: polling vs WebSocket vs SSE

Analysis Required:
- Latency vs complexity trade-offs for each real-time approach
- Frontend framework choice (vanilla JS, React, htmx)
- Impact on coordinator performance under load

Deliverables:
- Recommended real-time communication pattern with justification
- Backend changes needed (new endpoints, WebSocket handlers)
- Frontend component structure
- Files to modify and create
- Implementation order with estimated complexity
```

*Decentralize coordinator architecture:*
```
Context: Single coordinator is a bottleneck and single point of failure. Need to explore distributed coordination.

Exploration Tasks:
1. Map all coordinator responsibilities in src/server/main.py
2. Identify state that must be shared (worker registry, job routing, round-robin index)
3. Research: consistent hashing, gossip protocols, Raft consensus, Redis Cluster

Analysis Required:
- CAP theorem trade-offs for this use case
- Complexity cost of each decentralization approach
- Impact on client API (can it remain unchanged?)
- Failure modes and recovery strategies

Deliverables:
- Recommended architecture with rationale
- Component diagram showing node communication
- Data partitioning strategy
- Migration path from current single-coordinator setup
- Rollback plan if issues arise
```

*Distributed parallel inference:*
```
Context: Current system distributes jobs across workers. Need model parallelism - single large model split across multiple GPUs/workers.

Exploration Tasks:
1. Understand current inference path: queue/consumer.py -> inference/inference.py -> Ollama
2. Research: tensor parallelism, pipeline parallelism, vLLM, DeepSpeed-Inference, Ray Serve
3. Identify Ollama limitations for distributed inference

Analysis Required:
- Network bandwidth requirements for tensor sharding
- Fault tolerance when one node in parallel group fails
- Latency impact of coordination overhead
- Whether to replace Ollama or layer on top

Deliverables:
- Recommended distributed inference framework
- New architecture diagram showing GPU coordination
- Hardware/network requirements
- Changes to worker registration and job routing
- Phased implementation plan
```

**When to use Plan:**
- New features requiring architectural decisions
- Refactoring with multiple valid approaches
- Integrating external systems or frameworks
- Problems where you need to research before implementing

**When NOT to use Plan:**
- Bug fixes with clear cause
- Simple CRUD additions
- Code formatting or documentation updates
- Tasks where implementation path is obvious

---

### Explore

Use for codebase investigation, understanding existing patterns, and gathering information before making changes.

**Description examples:**
- "Investigate Redis connection handling"
- "Map the job lifecycle from submission to result"
- "Find all error handling patterns in worker code"

**Prompt structure:**

```
Goal: [What you need to understand]

Search Scope:
- [Directories/files to examine]
- [Patterns or keywords to look for]

Questions to Answer:
1. [Specific question about the code]
2. [Another specific question]

Output Format:
- [How to structure findings: list, diagram, table]
```

**Example prompts:**

*Investigate error handling:*
```
Goal: Understand how errors propagate through the system to improve reliability.

Search Scope:
- src/worker/ (especially queue/consumer.py and inference/inference.py)
- src/server/main.py
- Look for: try/except blocks, error responses, logging calls

Questions to Answer:
1. What happens when Ollama inference fails?
2. How are network errors between worker and Redis handled?
3. Are failed jobs retried? If so, how many times?
4. What errors does the client see vs what gets logged server-side?

Output Format:
- Table: error type | where caught | how handled | client visibility
- List of gaps in error handling
```

*Map authentication flow:*
```
Goal: Understand if/how workers authenticate with the coordinator.

Search Scope:
- src/worker/main.py (registration logic)
- src/server/main.py (registration endpoint)
- Any config files or environment variable usage

Questions to Answer:
1. Is there any authentication on /register?
2. Could a malicious actor register a fake worker?
3. How is worker identity verified on subsequent requests?

Output Format:
- Sequence diagram of registration
- Security assessment with risk levels
```

**When to use Explore:**
- Unfamiliar codebase areas
- Before refactoring to understand impact
- Debugging to trace data flow
- Security or performance audits

**When NOT to use Explore:**
- You already know the code well
- Simple questions answerable by reading one file
- When you need to make changes, not just understand

---

### Prose-Writer

Use for documentation, user-facing content, and any text requiring careful crafting.

**Description examples:**
- "Write API documentation for inference endpoints"
- "Create troubleshooting guide for worker connection issues"
- "Draft architecture decision record for WebSocket choice"

**Prompt structure:**

```
Content Type: [Documentation | Guide | README | ADR | etc.]
Audience: [Developers | End users | Operations | etc.]
Tone: [Technical | Conversational | Formal]

Context:
[Background information the writer needs]

Must Include:
- [Required section or topic]
- [Another required element]

Constraints:
- [Length limit if any]
- [Style guide to follow]
- [Terms to use or avoid]

Reference Material:
- [Files to read for accuracy]
- [Existing docs to match style]
```

**Example prompts:**

*API documentation:*
```
Content Type: API reference documentation
Audience: Developers integrating with GPU Torrent
Tone: Technical, concise

Context:
GPU Torrent exposes a REST API for job submission and result retrieval. Document the /inference and /result/{request_id} endpoints.

Must Include:
- Request/response schemas with examples
- Error codes and meanings
- Rate limiting behavior (if any)
- Authentication requirements

Constraints:
- Match style of existing CLAUDE.md
- Use curl examples, not language-specific SDKs

Reference Material:
- src/server/main.py for endpoint definitions
- src/client/api.py for usage patterns
```

*Troubleshooting guide:*
```
Content Type: Troubleshooting guide
Audience: Operators running GPU Torrent in production
Tone: Direct, problem-solution format

Context:
Workers sometimes fail to connect or drop from the cluster. Create a guide for diagnosing and resolving common issues.

Must Include:
- Symptom -> Cause -> Solution format
- Log locations and what to look for
- Redis connectivity checks
- Ollama health verification

Reference Material:
- src/worker/main.py for startup sequence
- src/worker/queue/consumer.py for Redis connection handling
```

**When to use Prose-Writer:**
- README files and documentation
- User guides and tutorials
- Technical blog posts or ADRs
- Any content where quality of writing matters

**When NOT to use Prose-Writer:**
- Code comments (just write them inline)
- Commit messages
- Quick internal notes

---

### General-Purpose

Use for implementation tasks, bug fixes, and code changes where the path is clear.

**Description examples:**
- "Add health check endpoint to coordinator"
- "Fix race condition in worker registration"
- "Implement job timeout handling"

**Prompt structure:**

```
Task: [Clear description of what to build/fix]

Context:
- [Relevant background]
- [Why this change is needed]

Requirements:
1. [Specific requirement]
2. [Another requirement]

Files Involved:
- [file path]: [what changes needed]

Acceptance Criteria:
- [How to verify it works]
```

**Example prompt:**

*Add health check endpoint:*
```
Task: Add /health endpoint to coordinator for load balancer integration.

Context:
Kubernetes needs a health check endpoint to determine if the coordinator is ready to receive traffic.

Requirements:
1. Return 200 when Redis is connected and responsive
2. Return 503 when Redis connection fails
3. Include response body with status details

Files Involved:
- src/server/main.py: Add new endpoint

Acceptance Criteria:
- curl localhost:8000/health returns 200 with {"status": "healthy", "redis": "connected"}
- Stopping Redis causes endpoint to return 503
```

**When to use General-Purpose:**
- Implementation tasks with clear specs
- Bug fixes with known cause
- Small to medium code changes
- Refactoring with defined scope

**When NOT to use General-Purpose:**
- Tasks requiring research or design decisions (use Plan)
- Codebase exploration (use Explore)
- Documentation (use Prose-Writer)

---

## Crafting Effective Subagent Prompts

### Essential Elements

| Element | Purpose | Example |
|---------|---------|---------|
| Context | Why this task exists | "Workers currently have no retry logic..." |
| Scope | Boundaries of the work | "Only modify src/worker/, do not change API contracts" |
| Constraints | Non-negotiable requirements | "Must maintain backward compatibility" |
| Deliverables | Expected outputs | "Return implementation plan with file list" |
| Success criteria | How to verify completion | "All existing tests pass, new endpoint returns 200" |

### Patterns That Work

**Be specific about files:**
```
Examine src/server/main.py lines 45-80 for the registration logic
```

**State assumptions to challenge:**
```
Current assumption: Redis is always available. Explore what happens when it's not.
```

**Request structured output:**
```
Output as a table: | Component | Current State | Proposed Change | Risk Level |
```

**Provide decision criteria:**
```
Choose the approach that minimizes latency, even if it increases code complexity.
```

### Common Mistakes

- **Too vague:** "Make the system better" - agent cannot determine scope
- **Missing context:** Assuming agent knows recent conversation history
- **No success criteria:** Agent doesn't know when to stop
- **Overloaded scope:** Asking for design, implementation, and documentation in one prompt

### Information Agents Need

1. **Current state:** What exists now, where to find it
2. **Desired state:** What should exist after the task
3. **Constraints:** Technology choices, compatibility requirements, time/complexity budgets
4. **Authority:** What they can change vs what's fixed
5. **Resources:** Files to read, external docs to reference, examples to follow

---

## Chaining Subagents

Complex tasks often benefit from multiple agents working in sequence, where each agent's output informs the next. This section covers when and how to chain agents effectively.

### When to Chain Subagents

**Chain agents when:**

- The task has distinct phases requiring different capabilities (research, design, implementation)
- You need to gather information before making decisions
- User input is required mid-process to refine direction
- The output of one phase directly shapes the next

**Do NOT chain when:**

- A single agent can complete the task
- The phases don't have meaningful dependencies
- You're artificially splitting a simple task

### Common Chaining Patterns

| Pattern | Agents | Use Case |
|---------|--------|----------|
| Research-Design-Build | Explore -> Plan -> General-Purpose | New features requiring codebase understanding |
| Design-Clarify-Refine | Plan -> AskUser -> Plan | Architecture decisions needing user input |
| Investigate-Document | Explore -> Prose-Writer | Creating documentation for existing code |
| Research-Plan-Implement | General-Purpose (research) -> Plan -> General-Purpose (build) | Features requiring external research |

### Pattern Details

**Explore -> Plan -> General-Purpose**

Most common pattern for non-trivial features. Explore gathers context, Plan makes architectural decisions, General-Purpose implements.

```
Explore: "How does the current worker registration flow work?"
   |
   v (findings inform planning)
Plan: "Design authentication for worker registration, considering the existing flow"
   |
   v (plan informs implementation)
General-Purpose: "Implement JWT authentication per the plan"
```

**Plan -> AskUser -> Plan**

Use when architectural decisions require user preferences or domain knowledge you cannot infer.

```
Plan: "Design caching strategy for inference results"
   |
   v (presents options to user)
AskUser: "Should cache prioritize memory efficiency or hit rate? TTL preferences?"
   |
   v (user input refines design)
Plan: "Finalize caching design with 1-hour TTL and LRU eviction"
```

**Explore -> Prose-Writer**

Ideal for documentation tasks. Explore ensures accuracy, Prose-Writer ensures quality.

```
Explore: "Map the complete inference pipeline from request to response"
   |
   v (technical findings become input)
Prose-Writer: "Document the inference pipeline for operators"
```

### Practical Examples

**Example 1: Add Authentication System**

Task: "Add authentication to the coordinator API"

```
Chain:
1. Explore -> Understand current endpoint security, existing patterns
2. Plan -> Design auth architecture (JWT vs OAuth, token storage, middleware)
3. AskUser -> "Prefer JWT for simplicity or OAuth for SSO integration?"
4. Plan (refined) -> Finalize design based on user choice
5. General-Purpose -> Implement authentication middleware and endpoints
```

Agent prompts:

```
# Agent 1: Explore
Goal: Understand current API security posture

Search Scope:
- src/server/main.py for endpoint definitions
- Any existing auth-related code or middleware

Questions to Answer:
1. Are any endpoints currently protected?
2. How do workers authenticate during registration?
3. What authentication patterns exist in similar FastAPI projects?

Output: Security assessment and list of endpoints needing protection
```

```
# Agent 2: Plan (initial)
Context: [Include Explore findings]

Design authentication system for coordinator API.

Requirements:
- Protect /inference and /result endpoints
- Allow worker registration with shared secret
- Support token refresh

Deliverables:
- Comparison of JWT vs OAuth approaches
- Recommended approach with trade-offs
- Questions for user if preferences needed
```

```
# Agent 3: AskUser
Based on the authentication design analysis:

Options:
A) JWT - Simpler, self-contained tokens, good for service-to-service
B) OAuth - Better for user-facing auth, SSO integration possible

Which approach fits your deployment model? Any specific requirements?
```

```
# Agent 4: General-Purpose
Task: Implement JWT authentication per approved design

Context: [Include final Plan output]

Requirements:
1. Add /auth/token endpoint for token generation
2. Create FastAPI dependency for protected routes
3. Update /inference and /result to require valid tokens
4. Add shared secret config for worker registration

Files:
- src/server/main.py: Add auth endpoints and middleware
- src/server/auth.py: New file for JWT utilities
```

**Example 2: Document the Inference Pipeline**

Task: "Create operator documentation for how inference works"

```
Chain:
1. Explore -> Trace complete inference flow through code
2. Prose-Writer -> Transform findings into clear documentation
```

Agent prompts:

```
# Agent 1: Explore
Goal: Map the complete inference lifecycle

Search Scope:
- src/client/api.py (submission)
- src/server/main.py (routing)
- src/worker/queue/consumer.py (job pickup)
- src/worker/inference/inference.py (execution)

Questions to Answer:
1. What data transformations occur at each step?
2. Where can failures occur and how are they handled?
3. What is stored in Redis at each stage?
4. What are the latency-sensitive paths?

Output: Sequence diagram and annotated flow description
```

```
# Agent 2: Prose-Writer
Content Type: Technical operations guide
Audience: Engineers deploying and monitoring GPU Torrent
Tone: Technical, precise

Context:
[Include complete Explore output with sequence diagram]

Must Include:
- Step-by-step request lifecycle
- Redis key usage at each stage
- Failure modes and recovery
- Performance considerations
- Monitoring points

Reference Material:
- Explore agent findings (provided above)
- Existing CLAUDE.md for style matching
```

**Example 3: Optimize Database Queries**

Task: "Optimize Redis operations for high-throughput scenarios"

```
Chain:
1. Explore -> Profile current Redis usage patterns
2. Plan -> Design optimization strategy
3. General-Purpose -> Implement optimizations
```

Agent prompts:

```
# Agent 1: Explore
Goal: Understand Redis usage patterns and identify bottlenecks

Search Scope:
- All files using Redis connections
- Pattern: redis, BRPOP, SET, GET, pipeline

Questions to Answer:
1. Which operations are called most frequently?
2. Are there opportunities for pipelining or batching?
3. What TTLs are set? Are they appropriate?
4. Any blocking operations that could be async?

Output: Table of Redis operations with frequency and optimization potential
```

```
# Agent 2: Plan
Context: [Include Explore findings]

Design Redis optimization strategy for high-throughput inference.

Analysis Required:
- Batch registration updates vs individual writes
- Pipeline result storage operations
- Connection pooling configuration
- Key expiration strategy

Deliverables:
- Prioritized list of optimizations by impact
- Implementation approach for each
- Benchmark criteria to measure improvement
```

```
# Agent 3: General-Purpose
Task: Implement Redis optimizations per plan

Context: [Include Plan output]

Requirements:
1. Add connection pooling with configurable size
2. Batch worker heartbeat updates using pipeline
3. Implement result key TTL of 1 hour
4. Add async Redis operations where blocking occurs

Acceptance Criteria:
- Throughput benchmark shows >20% improvement
- No increase in p99 latency
- All existing tests pass
```

### How to Chain Effectively

**1. Each agent gets a focused task**

Bad: "Explore the codebase, design a solution, and implement it"
Good: Three separate agents, each with clear scope

**2. Pass relevant context forward**

Include pertinent findings from previous agents. Don't dump entire outputs; extract what the next agent needs.

```
# Good: Focused context
Context: Explore found that worker registration uses no authentication.
The /register endpoint accepts any worker_id without validation.
Current workers: 3 registered in production.

# Bad: Raw dump
Context: [500 lines of Explore output]
```

**3. Know when to stop chaining**

If an agent produces a complete answer, don't add another agent for the sake of it.

```
# Unnecessary chain
Explore: "Find where errors are logged"
Prose-Writer: "Summarize where errors are logged"  # Just use Explore's output directly

# Necessary chain
Explore: "Find where errors are logged"
Prose-Writer: "Create error handling guide for operators"  # Transforms findings into new content
```

**4. Use parallel agents for independent tasks**

When tasks don't depend on each other, run agents in parallel rather than sequentially.

```
# Sequential (slower, unnecessary)
Explore: "How does worker registration work?"
Then: Explore: "How does job routing work?"

# Parallel (faster, correct)
Explore (1): "How does worker registration work?"
Explore (2): "How does job routing work?"
Then: Plan: "Design improvements using findings from both explorations"
```

### Anti-Patterns to Avoid

**Over-chaining simple tasks**

```
# Bad: Three agents for a simple fix
Explore: "Find the health check endpoint"
Plan: "Design how to add response time to health check"
General-Purpose: "Add response time to health check"

# Good: Single agent
General-Purpose: "Add response time field to /health endpoint response"
```

**Missing context handoff**

```
# Bad: Agent 2 has no idea what Agent 1 found
Agent 1 (Explore): [produces findings]
Agent 2 (Plan): "Design authentication system"  # No context from exploration

# Good: Explicit handoff
Agent 2 (Plan): "Design authentication system.
Context from exploration:
- No current auth on any endpoint
- Workers use shared COORDINATOR_URL
- Redis stores worker IDs without validation"
```

**Circular dependencies**

```
# Bad: Agents waiting on each other
Plan: "Design based on implementation constraints"
General-Purpose: "Implement based on final design"
Plan: "Refine design based on implementation feedback"
# This loop indicates unclear requirements - use AskUser instead
```

**Chaining for validation instead of review**

```
# Bad: Using agents to check each other
General-Purpose: "Implement feature"
Explore: "Check if implementation is correct"  # Agents aren't reviewers

# Good: Built-in validation
General-Purpose: "Implement feature.
Acceptance Criteria:
- Unit tests pass
- curl localhost:8000/endpoint returns expected response"
```
