# Frontier — Agent Harness Report V1

**Assessment Type:** Agent Harness / Orchestration Readiness  
**Design Assessed:** Frontier V1 Prototype  
**Primary Source:** Frontier — Prototype Implementation Specification & Architecture Brief  
**Assessment Status:** Architecture Review  
**Overall Harness Rating:** **8.8 / 10**

---

# 1. Executive Summary

Frontier V1 is a strong foundation for an **agent execution harness for software modernization**.

Its most important architectural decision is correct:

> **Frontier decides what is legal. Agents decide how to perform the work.**

Frontier is deliberately positioned as a deterministic workflow controller rather than another LLM agent. Agents provide reasoning and execution; Frontier owns workflow state, validation, gates, transitions, recovery, persistence, and completion. This separation is explicitly defined in the specification. 

The design therefore has the characteristics of a good harness:

```text
Agent
  ↓
Bound execution context
  ↓
Authorized task
  ↓
Workspace
  ↓
Agent result / evidence
  ↓
Frontier validation
  ↓
Verification
  ↓
Completion / Recovery
```

The design is particularly strong in:

- deterministic orchestration
- explicit state ownership
- bounded agent authority
- file-scope enforcement
- workspace/Git truth
- verification gates
- recovery decisions
- agent isolation
- testability
- low infrastructure overhead

The main limitation is not the control model.

The main limitation is that the V1 harness is intentionally **single-worker and sequential**, with relatively lightweight execution-context management. This is appropriate for proving the workflow but leaves significant future capability on the table.

---

# 2. Harness Definition

For this report, a **harness** means the infrastructure surrounding an agent that controls:

1. what the agent is asked to do
2. what context the agent receives
3. what tools/resources it can access
4. what files it may modify
5. how its execution is bounded
6. what result it must return
7. how its result is validated
8. how actual workspace changes are inspected
9. whether the work is accepted
10. what happens when execution fails

Under this definition, Frontier is not merely an orchestrator.

It is fundamentally an **agent governance and execution harness**.

---

# 3. Harness Architecture

The proposed architecture is:

```text
                         FRONTIER
                 Deterministic Harness
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
     Inspector        Planner         Worker
          │              │              │
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    Verifier
                         │
                         ▼
                     Workspace
```

The critical property is that the agents do not control one another.

The specification explicitly prohibits:

```text
Planner → Worker
Worker → Planner
Worker → Verifier
Verifier → Worker
```

Instead:

```text
Agent → Frontier → Agent
```

All control interactions are mediated by Frontier.

This is exactly the right shape for a controlled agent harness.

---

# 4. Harness Capability Assessment

| Harness Capability | V1 Assessment | Rating |
|---|---|---:|
| Agent isolation | Strong | 9.5 |
| Execution boundaries | Strong | 9 |
| State ownership | Excellent | 10 |
| Tool/resource governance | Good | 8 |
| File/write authorization | Excellent | 9.5 |
| Context management | Good | 8 |
| Agent result contract | Strong | 9 |
| Workspace observation | Excellent | 9.5 |
| Verification | Strong | 9 |
| Completion gating | Excellent | 10 |
| Recovery | Strong | 8.5 |
| Human intervention | Strong | 8.5 |
| Persistence/resume | Good | 8 |
| Parallel execution | Intentionally limited | 5 |
| Observability/evidence | Good | 8 |
| Testability | Excellent | 9.5 |

**Overall: 8.8 / 10**

---

# 5. Agent Invocation Model

A good harness should make an agent invocation explicit.

Frontier's architecture naturally supports the following conceptual object:

```text
AgentInvocation
│
├── projectId
├── taskId
├── agentType
├── taskObjective
├── repositoryContext
├── authorizedReadScope
├── authorizedWriteScope
├── availableTools
├── verificationRequirements
├── executionLimits
└── attemptId
```

The agent then operates inside this bounded context.

The important distinction is:

```text
Task
  ≠
Agent Prompt
```

The Task is Frontier's authoritative unit of work.

The prompt is merely the mechanism through which the agent is instructed to perform that work.

This distinction should remain explicit in implementation.

---

# 6. Context Harness

The specification favors supplying a sufficiently rich `RepositoryContext` up front and keeping additional context requests bounded and exceptional. It also explicitly recommends avoiding repeated context requests.

This is a good V1 decision.

Recommended conceptual structure:

```text
RepositoryContext
│
├── repository metadata
├── build metadata
├── technology versions
├── relevant files
├── relevant symbols
├── relevant configuration
├── existing tests
├── Git state
└── task-specific context
```

The harness should avoid becoming a conversational memory manager.

Prefer:

```text
one strong context package
        ↓
bounded agent execution
```

over:

```text
agent
 ↓
request context
 ↓
agent
 ↓
request more context
 ↓
agent
 ↓
request more context
```

The latter creates unnecessary LLM latency and cost.

---

# 7. Tool Harness

The Worker should not receive unrestricted environmental authority merely because it can access the repository.

The effective capability should be:

```text
Worker
 ├── read repository
 ├── inspect relevant files
 ├── invoke approved tools
 ├── modify authorized files
 └── execute approved commands
```

rather than:

```text
Worker
 └── unrestricted shell
```

The existing specification already establishes the critical write-scope rule: workers may read broadly but are constrained to an authorized write scope, with actual workspace/Git state treated as authoritative. 

This should remain one of the strongest harness boundaries.

---

# 8. Workspace Harness

This is one of Frontier's strongest characteristics.

The harness does not simply trust:

```text
WorkerResult.changedFiles
```

Instead:

```text
Worker
  ↓
claims changes
  ↓
Frontier inspects workspace
  ↓
actual diff
  ↓
scope validation
```

The specification explicitly states that the actual workspace/Git diff is authoritative for source modifications and Worker-reported changes are evidence only.

This prevents a particularly dangerous class of agent failure:

```text
Agent says:
"I only modified A.java"

Reality:
A.java
B.java
pom.xml
application.yml
```

The harness trusts the workspace, not the model.

That is exactly the correct security boundary.

---

# 9. Agent Result Contract

The Worker should return a structured result rather than arbitrary natural language.

Conceptually:

```text
WorkerResult
│
├── outcome
├── summary
├── evidence[]
├── artifacts[]
├── capabilityRequests[]
└── recoveryRecommendation
```

However:

```text
WorkerResult.outcome = SUCCESS
```

must never mean:

```text
Task = COMPLETE
```

The specification makes this explicit:

> Worker success alone never completes a Task.

Completion requires workspace validation and verification in addition to the Worker result.

This is a fundamental harness property.

---

# 10. Completion Gate

The completion gate is arguably the strongest part of the design.

Conceptually:

```text
Worker result exists
        AND
actual changes are within scope
        AND
deterministic checks pass
        AND
Verifier supports success
        ↓
      COMPLETE
```

Otherwise:

```text
NOT COMPLETE
```

This prevents the harness from becoming an agent-driven workflow.

The agent supplies evidence.

Frontier makes the decision.

This is the correct control model.

---

# 11. Verification Harness

Verification is layered appropriately:

```text
                    Verification
                         │
             ┌───────────┴───────────┐
             │                       │
       Deterministic            Semantic
         checks                  checks
             │                       │
       build/tests             LLM reasoning
       compilation             when required
       static checks
```

The design correctly favors deterministic verification and invokes semantic verification only when required. The implementation milestones explicitly recommend starting with deterministic verification before introducing semantic verification.

This is important because otherwise the harness becomes:

```text
Agent says it worked
        ↓
LLM says it worked
        ↓
COMPLETE
```

which provides very weak guarantees.

Frontier instead aims for:

```text
Agent evidence
      +
Actual workspace
      +
Deterministic validation
      +
Semantic validation when necessary
      ↓
Completion decision
```

---

# 12. Recovery Harness

Frontier has a meaningful recovery model:

```text
Failure
  │
  ├── Retry
  │
  ├── Repair
  │
  ├── Replan
  │
  ├── Human Gate
  │
  ├── Block
  │
  └── Fail
```

The important point is that the agent may **recommend** recovery, but does not select or execute the recovery transition itself.

The recovery invariant explicitly preserves Frontier's authority.

This creates:

```text
Agent:
"Retry may help."

Frontier:
"Retry is permitted."

```

rather than:

```text
Agent:
"I failed, so I'll restart myself."
```

That distinction matters considerably once real repositories are involved.

---

# 13. Replanning Harness

Replanning is handled as a workflow capability rather than allowing agents to continuously rewrite their own objectives.

This is important.

A dangerous design would be:

```text
Planner
 ↓
Worker
 ↓
Worker decides task is wrong
 ↓
Worker changes plan
 ↓
Worker executes new plan
```

Frontier instead keeps plan changes under orchestration control.

The history invariant also prevents completed work from being silently rewritten during replanning.

This is a strong property for modernization workflows.

---

# 14. Agent Communication Model

### Rating: 10/10

The design strongly avoids emergent agent networks.

There is no:

```text
Agent A ↔ Agent B
```

Instead:

```text
                 Frontier
                /   |   \
               /    |    \
              ↓     ↓     ↓
         Planner  Worker  Verifier
```

This produces a much more observable system.

The harness knows:

```text
who ran
why they ran
what task they ran
what authority they had
what they returned
what changed
what verification occurred
what decision Frontier made
```

That is much easier to debug than autonomous agent-to-agent communication.

---

# 15. Deterministic Control Plane

Frontier's control plane is appropriately deterministic.

It owns:

```text
Project state
Task state
Task readiness
DAG validation
Dependency validation
Scope validation
Conflict validation
Worker invocation
Verifier invocation
Completion gates
Recovery decisions
Replanning
Human gates
Persistence
Evidence recording
```

These responsibilities are explicitly assigned to Frontier in the specification.

This creates a useful division:

```text
┌──────────────────────────────┐
│       CONTROL PLANE          │
│                              │
│ Frontier                     │
│ deterministic                │
│ authoritative                │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       EXECUTION PLANE        │
│                              │
│ Planner / Worker / Verifier  │
│ probabilistic                │
│ bounded                      │
└──────────────────────────────┘
```

That separation should be preserved.

---

# 16. Harness State Machine

The Worker lifecycle is appropriately bounded:

```text
READY
  │
  ▼
EXECUTING
  │
  ▼
VERIFYING
  │
  ├─────────────── success ──────────────► COMPLETE
  │
  └────────────── failure
                     │
                     ▼
                  RECOVERY
                 /    |    \
              retry repair replan
```

The test specification explicitly expects:

```text
READY → EXECUTING → VERIFYING → COMPLETE
```

and requires this to be testable using Mock Worker and Mock Verifier without external LLMs.

This is excellent harness design.

---

# 17. Parallelism Assessment

### V1 effective parallelism: **1**

The current harness intentionally assumes:

```text
1 project
1 workspace
1 active execution context
1 Worker
```

The specification explicitly excludes worker pools, sophisticated scheduling, speculative parallelism, and distributed execution.

This is not an architectural weakness for V1.

It is a deliberate simplification.

However, the harness has a future path toward:

```text
                 Frontier
               /    |    \
              ↓     ↓     ↓
           Worker Worker Worker
              │     │     │
              └──┬──┴──┬──┘
                 ↓
             Verification
```

provided that:

```text
dependencies satisfied
AND
write scopes disjoint
AND
workspace isolation is safe
```

The existing DAG and resource-conflict model provides the conceptual foundation for this future extension.

---

# 18. Persistence Harness

The persistence design is intentionally lightweight.

The current model is:

```text
ProjectStore
   │
   ├── load(projectId)
   └── save(project)
```

with persistence at meaningful workflow boundaries such as:

```text
state transition
Worker execution
verification
recovery decision
plan update
human decision
```

The specification explicitly allows active state to remain in memory while persisting at workflow boundaries.

For a prototype harness this is appropriate.

It provides:

- resume capability
- failure recovery
- diagnostic history
- deterministic state reconstruction

without introducing an unnecessary database or event-sourcing system.

---

# 19. Evidence Harness

The evidence model is appropriately lightweight:

```text
Evidence
 ├── source
 ├── type
 ├── summary
 ├── timestamp
 └── artifact/reference
```

Potential sources include:

```text
DISCOVERY
PLANNER
WORKER
VERIFIER
SYSTEM
HUMAN
```

Evidence is append-oriented and does not itself mutate workflow state.

This is a good foundation for future observability without prematurely building a generalized evidence platform.

---

# 20. Security / Safety Boundary

For a modernization harness, the most important security boundary is not authentication.

It is **agent authority**.

Frontier currently provides several strong boundaries:

### State authority

Only Frontier mutates workflow state.

### File authority

Worker writes are restricted by task scope.

### Workspace authority

Actual repository state is authoritative.

### Verification authority

Agents cannot declare completion.

### Communication authority

Agents cannot directly control other agents.

### Recovery authority

Agents can recommend recovery but cannot decide it.

These invariants are explicitly defined by the specification.

This is an unusually good set of prototype-level guarantees.

---

# 21. Test Harness Quality

The architecture is highly testable because the core workflow does not depend on LLM execution.

The recommended testing approach is:

```text
Mock Planner
Mock Worker
Mock Verifier
      ↓
Deterministic Frontier
```

This allows testing of:

```text
state transitions
DAG validation
scope enforcement
completion gates
recovery
replanning
human gates
persistence
resume
project completion
```

without spending tokens or introducing nondeterminism.

The implementation specification explicitly requires behavior-focused tests covering legal behavior, transitions, invariants, contracts, and workflow outcomes.

This should remain a core development strategy.

---

# 22. What the Harness Gets Right

## 22.1 Frontier is not an agent

This is probably the single most important architectural decision.

Do not weaken it.

---

## 22.2 Agents are untrusted executors

The architecture implicitly treats agent output as evidence rather than truth.

That is exactly the correct model.

```text
Agent output
     ≠
system truth
```

---

## 22.3 Workspace is the source of truth

This avoids trusting model-generated descriptions of modifications.

---

## 22.4 Completion is a deterministic decision

The agent cannot talk itself into completion.

---

## 22.5 Recovery is externalized

The agent cannot recursively redefine its own mission.

---

## 22.6 Scope is explicit

The Worker cannot silently expand its authority.

---

## 22.7 Agent communication is centralized

This keeps the system observable and debuggable.

---

## 22.8 The harness is cheap

The prototype deliberately favors in-process orchestration, in-memory active state, local persistence, deterministic validation, minimal serialization, and adapter-based external calls.

This is appropriate because the expensive component is likely to be:

```text
LLM reasoning
repository transformation
build/test execution
```

not the orchestration kernel.

---

# 23. Harness Weaknesses

The following are real limitations, but most are appropriate V1 trade-offs.

## 23.1 Execution isolation is not deeply specified

The design establishes task and file boundaries, but does not fully specify:

- process isolation
- command allowlists
- environment-variable restrictions
- network access
- credential exposure
- timeout enforcement
- CPU/memory limits
- process-tree cleanup

For a local prototype this may be acceptable.

For production this becomes important.

**Recommendation:** do not build a sandbox platform for V1, but define the boundary explicitly.

---

## 23.2 Tool permissions need to become explicit

The specification defines interfaces and scope well, but a mature harness should eventually model:

```text
Capability
  ├── tool
  ├── operation
  ├── authorization
  └── constraints
```

For example:

```text
read_file        ALLOW
write_file       ALLOW within scope
git_status       ALLOW
git_diff         ALLOW
mvn test         ALLOW
network_request  DENY
delete_repository DENY
```

This does not need to become a capability registry.

A simple task-level capability set is sufficient.

---

## 23.3 Timeouts should be first-class

A bounded agent execution should have:

```text
maxDuration
```

and ideally:

```text
maxAttempts
```

The recovery model already implies bounded attempts; execution-time bounds should be made equally explicit.

---

## 23.4 Token/cost budgets are not yet first-class

A production harness should eventually track:

```text
input tokens
output tokens
LLM calls
elapsed time
tool calls
```

at:

```text
project
task
attempt
agent invocation
```

This is especially important because Frontier explicitly aims to be frugal with LLM calls.

---

## 23.5 Parallelism is intentionally absent

This is the largest performance limitation.

V1 is effectively:

```text
concurrency = 1
```

That is acceptable for proving correctness but will eventually constrain throughput.

---

# 24. Recommended V1 Harness Contract

The implementation should converge toward one conceptual invocation boundary:

```text
invoke(agent, context)
        ↓
AgentResult
```

with Frontier surrounding it:

```text
┌─────────────────────────────────────────────┐
│                  FRONTIER                   │
│                                             │
│  authorize                                  │
│      ↓                                      │
│  construct context                          │
│      ↓                                      │
│  invoke agent                               │
│      ↓                                      │
│  collect result                             │
│      ↓                                      │
│  inspect workspace                          │
│      ↓                                      │
│  validate scope                             │
│      ↓                                      │
│  verify                                     │
│      ↓                                      │
│  decide completion/recovery                 │
│      ↓                                      │
│  persist                                    │
│                                             │
└─────────────────────────────────────────────┘
```

This should be the conceptual center of the implementation.

---

# 25. Harness Anti-Patterns to Prevent

The following should be explicitly prohibited.

### Agent-owned state

```text
Worker.setTaskComplete()
```

No.

---

### Agent-owned workflow

```text
Worker → nextTask()
```

No.

---

### Agent-controlled recovery

```text
Worker → retry itself indefinitely
```

No.

---

### Agent-controlled scope

```text
Worker → modify additional files because required
```

No.

---

### Agent-to-agent orchestration

```text
Planner → invoke Worker
```

No.

---

### LLM-based deterministic decisions

```text
LLM → "Is this file within scope?"
```

No.

Use code/Git/path validation.

---

### Self-reported completion

```text
Worker says SUCCESS
       ↓
COMPLETE
```

No.

---

### Verification by another opinionated LLM only

```text
Worker says success
       ↓
Verifier LLM agrees
       ↓
COMPLETE
```

Insufficient.

---

### Infinite agent loops

```text
execute
 ↓
repair
 ↓
execute
 ↓
repair
 ↓
...
```

No.

Frontier must impose bounded recovery.

---

# 26. Harness Maturity Model

Frontier currently sits approximately here:

```text
Level 0
Raw LLM
   ↓
Level 1
Agent + tools
   ↓
Level 2
Bounded agent harness
   ↓
Level 3
Deterministic orchestration harness  ← FRONTIER V1
   ↓
Level 4
Parallel / production execution harness
   ↓
Level 5
Distributed modernization platform
```

Frontier V1 should **not** attempt to jump directly to Level 4 or Level 5.

The implementation specification explicitly says to prove the workflow before introducing production infrastructure.

---

# 27. Recommended Implementation Priority

If the objective is to build the harness correctly, priority should be:

```text
P0
Deterministic kernel
        ↓
P0
Agent invocation boundary
        ↓
P0
Task-scoped context
        ↓
P0
Write-scope enforcement
        ↓
P0
Workspace diff inspection
        ↓
P0
Verification gate
        ↓
P0
Recovery decision
        ↓
P1
Timeout / attempt limits
        ↓
P1
Capability/tool restrictions
        ↓
P1
Invocation telemetry
        ↓
P2
Cost/token accounting
        ↓
P2
Parallel Workers
```

Do not reverse this order.

---

# 28. Harness Acceptance Tests

A Frontier harness should be considered functionally sound when these scenarios work.

### Agent success

```text
Worker success
+ valid diff
+ verification success
→ COMPLETE
```

### Scope violation

```text
Worker success
+ out-of-scope modification
→ NOT COMPLETE
→ recovery
```

### Verification failure

```text
Worker success
+ valid scope
+ verification failure
→ NOT COMPLETE
→ recovery
```

### False success

```text
Worker claims success
+ no valid workspace change
→ NOT COMPLETE
```

### Agent failure

```text
Worker failure
→ Frontier recovery decision
```

### Replanning

```text
Task failure
→ replan
→ validate new DAG
→ preserve completed history
→ continue
```

### Human gate

```text
risk condition
→ HUMAN_GATE
→ no autonomous continuation
```

### Exhaustion

```text
repeated failure
→ attempts exhausted
→ FAILED / BLOCKED
```

These align directly with the prototype's existing definition of done and test requirements.

---

# 29. Overall Assessment

## Harness Strength

**8.8 / 10**

### Excellent

- deterministic control plane
- agent isolation
- state ownership
- scope enforcement
- workspace truth
- completion gate
- recovery ownership
- testability
- minimal infrastructure

### Good

- context management
- evidence
- persistence
- verification
- human gates

### Intentionally immature

- execution sandboxing
- tool permission model
- resource budgets
- telemetry
- parallel execution
- distributed execution

---

# 30. Final Recommendation

**Proceed with the current architecture.**

Do not add another orchestration abstraction.

Do not introduce an "AgentManager", "AgentSupervisor", "CapabilityRegistry", "AgentBus", or similar layer merely to make the architecture look more agentic.

The existing model is already sufficient:

```text
                 FRONTIER
            deterministic harness
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
   Inspector     Planner       Worker
                                │
                                ↓
                             Workspace
                                │
                                ↓
                            Verifier
                                │
                                ↓
                             Frontier
```

The most important thing to prove now is not whether Frontier can support more agents.

It is whether the harness can reliably turn:

```text
LLM reasoning
     +
bounded execution
     +
actual repository changes
     +
deterministic validation
     +
verification
     +
controlled recovery
```

into:

```text
safe, repeatable modernization outcomes.
```

That is the real Frontier experiment.

The specification's final architectural principle captures this correctly:

> **Frontier decides what is legal. Agents decide how to perform the work.**

The prototype should preserve that boundary while remaining small.