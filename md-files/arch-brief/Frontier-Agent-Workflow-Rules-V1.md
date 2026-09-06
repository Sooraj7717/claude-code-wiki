# Frontier — Agent Workflow Construction Rules

**Document Type:** Normative Implementation Rules  
**Audience:** Claude Code / implementation agent  
**Status:** Prototype V1  
**Purpose:** Remove ambiguity about how Frontier creates, invokes, constrains, observes, and terminates agent work.

---

## 1. Purpose

This document defines the **agentic workflow construction rules** for Frontier.

The other Frontier documents define:

- what Frontier is,
- which agent roles exist,
- project and task states,
- workflows,
- capabilities/toolsets,
- contracts,
- verification,
- recovery,
- persistence.

This document adds the missing implementation-level rule:

> **How Claude Code must construct an executable workflow that actually uses agents while keeping Frontier in control of the workflow.**

The implementation must not interpret "agent" as an unrestricted autonomous process.

An agent is a **bounded execution role** invoked by Frontier for a specific operation.

The canonical lifecycle is:

```text
Agent Definition
      ↓
Agent Invocation
      ↓
Bound Execution Context
      ↓
Agent Execution
      ↓
Agent Result
      ↓
Frontier Validation
      ↓
State Transition
      ↓
Next Workflow Operation
```

Only Frontier controls the transitions between these stages.

---

# 2. Core Rule

> **Agents perform bounded work. Frontier controls when they are invoked, what they are allowed to do, what they receive, what they return, and what happens next.**

Claude Code must not implement a generic autonomous-agent framework.

Do not introduce:

- free-form agent spawning,
- agent-to-agent delegation,
- agent-controlled workflow transitions,
- autonomous task discovery,
- unrestricted tool access,
- automatic scope expansion,
- persistent autonomous agent loops,
- agent-owned project state,
- hidden inter-agent communication.

The implementation should contain only the agent roles explicitly defined by Frontier.

---

# 3. Agentic Vocabulary

Use the following terms consistently.

| Term | Meaning |
|---|---|
| **Agent Definition** | Static definition of an allowed agent role |
| **Agent Role** | Planner or Worker in Frontier V1 |
| **Agent Invocation** | One bounded execution of an agent role |
| **Invocation Context** | Context assembled by Frontier for the invocation |
| **Capability Binding** | Tools/capabilities made available to the invocation |
| **Authorization Scope** | What the invocation is allowed to read/write |
| **Agent Result** | Structured output returned by the invocation |
| **Evidence** | Observable facts supporting the result |
| **Frontier Validation** | Deterministic validation performed after invocation |
| **State Transition** | Workflow transition decided by Frontier |
| **Recovery Operation** | Retry, repair, replan, block, human gate, or fail |

Avoid vague phrases such as:

- "the agent handles the workflow"
- "the agent decides what happens next"
- "agents communicate"
- "the system creates an autonomous agent"
- "the worker can do anything necessary"

Replace them with explicit statements describing the invocation, authorization, result, and Frontier decision.

---

# 4. Agent Definitions

An Agent Definition describes an allowed role.

It is not an active process.

Example:

```yaml
agent:
  id: worker
  role: WORKER
  purpose: Execute one bounded modernization task
  input: WorkerContext
  output: WorkerResult
  capabilities:
    - git
    - java-build
    - openrewrite
  state_authority: none
```

The definition must specify:

1. role,
2. purpose,
3. input contract,
4. output contract,
5. allowed capabilities,
6. state authority,
7. authorization constraints.

### V1 Agent Roles

Frontier V1 has two reasoning-oriented agent roles:

```text
Planner
Worker
```

The following are not general-purpose autonomous agents:

```text
RepositoryInspector
Verifier
RecoveryPolicy
ProjectStore
```

They are deterministic capabilities/control components unless a later design explicitly promotes a capability to an agent role.

---

# 5. Agent Invocation

An Agent Invocation is the runtime execution unit.

Every invocation must have an explicit identity.

Example:

```yaml
id: task-007-attempt-01
agent: worker
task_id: task-007
```

An invocation must not exist without:

- an agent role,
- an invocation ID,
- an operation/task,
- an execution context,
- authorization scope,
- capability bindings,
- an expected result contract.

The invocation is created by Frontier.

The agent does not create its own invocation.

---

# 6. Invocation Lifecycle

Claude Code must implement the following lifecycle explicitly.

```text
1. Workflow reaches an agent-executable operation
2. Frontier identifies the eligible agent role
3. Frontier loads authoritative task state
4. Frontier assembles invocation context
5. Frontier binds required capabilities
6. Frontier binds authorization scope
7. Frontier creates invocation identity
8. Frontier invokes the agent
9. Agent performs bounded work
10. Agent returns structured result
11. Frontier inspects actual workspace state
12. Frontier performs deterministic validation
13. Verifier runs when required
14. Frontier decides the state transition
15. Frontier applies recovery if required
16. Frontier persists the result
17. Frontier selects the next workflow operation
```

The agent must not skip directly from step 9 to step 17.

---

# 7. Agent Creation vs Agent Invocation

Do not confuse these concepts.

### Agent creation

Defines what an agent role is.

```text
Worker Definition
Planner Definition
```

### Agent invocation

Runs that role for one bounded operation.

```text
Worker Invocation → task-007
Worker Invocation → task-008
Planner Invocation → project-001
```

A prototype implementation may represent agent definitions as code/configuration and invocations as ordinary in-process execution objects.

No distributed agent runtime is required.

---

# 8. Invocation Context

Frontier assembles the context before invoking an agent.

The context should be sufficient for the agent to perform its assigned operation without repeatedly rediscovering repository information.

A Worker context may contain:

```yaml
context:
  project:
    id: project-001

  task:
    id: task-007
    objective: Migrate deprecated Spring Security configuration

  dependencies:
    - task-003

  repository:
    root: /workspace/project
    source_level: Java 8
    target_level: Java 21

  relevant_files:
    - src/main/java/com/example/security/SecurityConfig.java

  verification_requirements:
    - compile
    - targeted-tests
```

The context must be:

- explicit,
- bounded,
- reproducible,
- derived from authoritative Frontier state and repository evidence.

Do not rely on hidden conversational history as the authoritative task context.

---

# 9. Context Authority

Different information has different authority.

### Authoritative

- Frontier project state
- Frontier task state
- approved plan
- task dependencies
- authorized write scope
- actual workspace
- actual Git state
- persisted verification results

### Agent-generated

- reasoning
- proposed approach
- implementation result
- warnings
- recommendations
- reported changed files

Agent-generated information is evidence, not workflow authority.

For example:

```text
Worker says: "I changed three files."
```

This does not establish the actual change set.

Frontier must inspect the workspace/Git diff.

---

# 10. Capability Binding

An agent receives only the capabilities required for its invocation.

Example:

```yaml
capabilities:
  - git
  - java-build
  - openrewrite
```

Capability binding is controlled by Frontier.

The agent must not dynamically acquire arbitrary capabilities.

The agent must not invoke an unavailable capability by inventing its interface.

V1 does not implement:

- capability marketplaces,
- capability negotiation,
- dynamic tool discovery,
- capability-to-capability delegation.

If a required capability is unavailable, the invocation returns a structured failure or capability request according to the applicable contract. Frontier decides the next operation.

---

# 11. Authorization Scope

Every Worker invocation must have an explicit write scope.

Example:

```yaml
authorization:
  read_scope: repository
  write_scope:
    - src/main/java/com/example/security/**
```

The Worker may inspect broadly when necessary.

The Worker may modify only authorized paths.

The Worker must not:

- expand its own write scope,
- modify unrelated files,
- modify Frontier's state files,
- modify another task's protected scope,
- treat a discovered dependency as permission to edit it.

If additional changes are required outside the authorized scope:

```text
Worker → reports requirement
Frontier → does not automatically expand scope
Frontier → may trigger REPLAN
Planner → proposes revised plan/scope
Frontier → validates revised plan
```

Scope expansion is therefore a workflow decision, not an agent decision.

---

# 12. Agent Isolation

Agents are logically isolated.

The preferred V1 model is:

```text
Frontier
   │
   ├── Planner Invocation
   │
   └── Worker Invocation
```

Not:

```text
Planner → Worker
Worker → Planner
Worker → Verifier
```

Agents do not directly control one another.

If one agent needs information produced by another agent, Frontier passes the relevant result/evidence through the workflow context.

This makes the hand-off explicit and testable.

---

# 13. Agent-to-Agent Communication

Do not implement direct agent messaging in V1.

Avoid:

```text
agent.send(...)
agent.delegate(...)
agent.spawn(...)
agent.ask_other_agent(...)
```

Instead use:

```text
Agent Result
      ↓
Frontier
      ↓
Next Invocation Context
      ↓
Next Agent
```

This is the required communication pattern.

---

# 14. Planner Invocation

The Planner is invoked when Frontier requires planning or replanning.

The Planner:

- reads repository/project context,
- interprets modernization requirements,
- proposes tasks,
- proposes dependencies,
- proposes write scopes,
- proposes verification requirements,
- may identify risks.

The Planner does not:

- mutate the repository,
- change Frontier state,
- execute Worker tasks,
- approve its own plan,
- expand execution scope during Worker execution.

The Planner returns a structured plan.

Frontier validates the plan before it becomes executable.

Canonical flow:

```text
Repository Context
        ↓
Planner Invocation
        ↓
Plan Result
        ↓
Frontier Plan Validation
        ↓
Approved Plan
```

---

# 15. Worker Invocation

The Worker is invoked for one bounded executable task.

A Worker invocation must have:

```text
Task
+
Context
+
Capabilities
+
Write Scope
+
Constraints
+
Expected Result
```

The Worker:

1. understands the assigned task,
2. inspects relevant code,
3. performs the authorized modification,
4. runs appropriate local checks where available,
5. reports the result.

The Worker does not:

- select the next task,
- alter task dependencies,
- modify project state,
- change authorization scope,
- invoke another agent,
- declare the project complete.

---

# 16. Worker Result

A Worker Result should distinguish between:

### What the Worker reports

```yaml
result:
  outcome: SUCCESS
  summary: Updated security configuration
  reported_changed_files:
    - src/main/java/com/example/security/SecurityConfig.java
  warnings: []
```

### What Frontier observes

```text
actual Git diff
actual files
actual build/test result
actual verification result
```

The second category has higher authority for workflow decisions.

A Worker cannot establish success merely by returning:

```yaml
outcome: SUCCESS
```

Frontier must evaluate the completion gate.

---

# 17. Workspace Authority

The workspace and Git state are authoritative for actual source changes.

Use this rule:

> **Agent-reported changes are claims. Workspace/Git inspection is evidence.**

After a Worker invocation:

```text
Worker Result
      ↓
Inspect actual workspace/Git diff
      ↓
Compare against authorized scope
      ↓
Reject or accept scope compliance
```

If a Worker reports:

```text
changed_files:
  - A.java
```

but Git shows:

```text
A.java
B.java
```

then Frontier must treat `B.java` as an actual change regardless of the Worker report.

---

# 18. Frontier Must Own Workflow Decisions

After every agent invocation, Frontier decides what happens next.

Possible outcomes include:

```text
CONTINUE
COMPLETE
RETRY
REPAIR
REPLAN
BLOCK
HUMAN_GATE
FAIL
```

The agent may recommend one of these outcomes.

The agent does not execute the transition.

For example:

```yaml
worker_recommendation:
  action: REPLAN
  reason: Required migration affects a file outside current scope
```

Frontier then evaluates the recommendation against deterministic rules and workflow state.

---

# 19. State Transition Rule

Agents must never mutate project or task state directly.

Incorrect:

```text
Worker → task.state = COMPLETE
```

Correct:

```text
Worker → WorkerResult
        ↓
Frontier validation
        ↓
Frontier decides task state
        ↓
ProjectStore persists state
```

Only Frontier may transition:

- project state,
- task state,
- recovery state,
- human-gate state.

---

# 20. Task Execution Workflow

The canonical Worker workflow is:

```text
READY
  ↓
Frontier creates Worker Invocation
  ↓
Context assembled
  ↓
Capabilities bound
  ↓
Write scope bound
  ↓
Worker executes
  ↓
Worker Result
  ↓
VERIFYING
  ↓
Actual workspace/Git inspection
  ↓
Deterministic verification
  ↓
Optional semantic verification
  ↓
Completion Gate
  ├── PASS → COMPLETE
  └── FAIL → RecoveryPolicy
```

The Worker does not determine whether the task is COMPLETE.

---

# 21. Completion Gate

A task is not complete because the Worker says it is complete.

The completion gate should evaluate:

```text
Worker result exists
AND
actual diff is within authorized scope
AND
required deterministic checks pass
AND
required verification supports success
AND
task acceptance criteria are satisfied
```

Only then may Frontier transition:

```text
VERIFYING → COMPLETE
```

---

# 22. Recovery Workflow

Recovery is controlled by Frontier.

A Worker or Verifier may provide evidence and recommendations.

Frontier selects the recovery operation.

Example:

```text
Worker failure
      ↓
Verifier / evidence
      ↓
Frontier classification
      ↓
RecoveryPolicy
      ↓
RETRY / REPAIR / REPLAN / BLOCK / HUMAN_GATE / FAIL
```

### Retry

Repeat the same invocation with bounded attempts.

### Repair

Invoke the Worker again against the same authoritative task and scope with additional failure context.

### Replan

Return control to the Planner because the approved plan is insufficient.

### Block

Stop because required progress cannot safely continue.

### Human Gate

Persist a decision request requiring human intervention.

### Fail

Terminate the workflow as unsuccessful.

---

# 23. Repair vs Replan

This distinction must be explicit.

### Repair

Use when:

```text
The task is still valid.
The scope is still valid.
The plan is still valid.
The implementation attempt needs correction.
```

Flow:

```text
Failure
  ↓
Repair context
  ↓
Worker Invocation
  ↓
Verify
```

### Replan

Use when:

```text
The task definition is insufficient.
The dependency graph is wrong/incomplete.
The required scope must materially change.
The modernization approach is no longer valid.
```

Flow:

```text
Failure
  ↓
Replan request
  ↓
Planner Invocation
  ↓
Plan validation
  ↓
Continue execution
```

Never use replan as a generic retry mechanism.

---

# 24. Human Gate

A human gate is a Frontier workflow state, not an agent request loop.

Example:

```yaml
human_gate:
  reason: Required change exceeds approved modernization scope
  requested_at: "..."
  decision: null
```

The Worker cannot approve the gate.

The Planner cannot approve the gate.

The gate is resolved externally and Frontier resumes the workflow using the recorded decision.

---

# 25. Agent Termination

Every invocation has a defined end.

An agent invocation terminates when:

1. the agent returns a structured result,
2. the agent encounters a terminal execution failure,
3. the configured execution boundary is reached,
4. Frontier cancels/abandons the invocation according to workflow rules.

Do not implement indefinite agent loops.

An agent does not remain alive waiting for another task.

A new task creates a new invocation.

---

# 26. No Autonomous Next-Step Selection

This is a critical implementation rule.

Do not implement:

```text
Worker finishes task
↓
Worker chooses another task
↓
Worker executes another task
```

Implement:

```text
Worker finishes task
↓
Frontier validates result
↓
Frontier updates task state
↓
Frontier evaluates DAG
↓
Frontier selects next READY task
↓
Frontier creates next Worker Invocation
```

This keeps the workflow deterministic.

---

# 27. Bounded Agent Loops

Agent loops are permitted only where explicitly defined by a Frontier workflow.

For example:

```text
Worker
  ↓
Verify
  ↓
Repair
  ↓
Worker
```

This loop must have:

- a defined reason,
- a bounded attempt count,
- explicit state transitions,
- persisted history.

Do not implement an unrestricted:

```text
while agent.is_not_done():
    agent.run()
```

style autonomous loop.

---

# 28. Planner Context Requests

The Planner should receive rich initial context.

A bounded additional-context request may be supported if required.

The flow is:

```text
Frontier
  ↓
Planner
  ↓
Context Request
  ↓
Frontier validates request
  ↓
RepositoryInspector
  ↓
Additional Context
  ↓
Planner
```

This is an exception path, not the normal planning model.

Do not create an open-ended Planner ↔ RepositoryInspector conversation.

V1 should use a bounded request count.

---

# 29. Worker Context Requests

A Worker may encounter missing information.

A bounded context request may be supported.

The request must specify what information is needed.

Example:

```yaml
context_request:
  type: REPOSITORY_CONTEXT
  reason: Need callers of deprecated configuration API
```

Frontier decides whether the request can be satisfied.

The Worker must not automatically obtain unrestricted additional context.

---

# 30. Capability Requests

Capability requests must remain bounded.

Example:

```yaml
capability_request:
  capability: java-build
  reason: Required to validate compilation
```

Frontier determines whether the capability is authorized and available.

Do not implement dynamic capability discovery or negotiation in V1.

---

# 31. Workflow Construction Pattern

Every executable agent workflow should be expressible using this pattern:

```text
ENTRY CONDITION
      ↓
FRONTIER STATE
      ↓
ELIGIBILITY CHECK
      ↓
AGENT SELECTION
      ↓
CONTEXT ASSEMBLY
      ↓
CAPABILITY BINDING
      ↓
AUTHORIZATION BINDING
      ↓
AGENT INVOCATION
      ↓
STRUCTURED RESULT
      ↓
WORKSPACE / EVIDENCE INSPECTION
      ↓
DETERMINISTIC VALIDATION
      ↓
VERIFICATION
      ↓
FRONTIER DECISION
      ↓
STATE TRANSITION
      ↓
PERSISTENCE
      ↓
NEXT WORKFLOW OPERATION
```

Claude Code should use this pattern whenever adding a new agent-backed workflow.

---

# 32. Workflow Definition Template

New agent-backed workflows should document at least:

```markdown
## Workflow

### Entry Condition
When does the workflow begin?

### Frontier State
What project/task state must exist?

### Eligible Agent
Which defined agent role may execute?

### Invocation Context
What authoritative information is supplied?

### Capabilities
Which capabilities are bound?

### Authorization Scope
What may the invocation read/write?

### Agent Operation
What bounded work does the agent perform?

### Agent Result
What structured result is returned?

### Evidence
What observable evidence is collected?

### Validation
What deterministic checks are applied?

### Verification
What verification is required?

### State Transition
Which Frontier transitions are possible?

### Recovery
What happens on failure?

### Persistence
What must be persisted?

### Next Operation
How does Frontier select the next operation?
```

A workflow that cannot answer these questions is underspecified.

---

# 33. Agent Invocation Object

A V1 implementation should use an explicit invocation model, whether represented as a class, record, or equivalent structure.

Example:

```yaml
id: task-007-attempt-01
agent: worker
task_id: task-007

objective: >
  Migrate deprecated Spring Security configuration.

context:
  repository:
    root: /workspace/project
  task:
    objective: ...
  dependencies:
    - task-003
  verification_requirements:
    - compile
    - targeted-tests

authorization:
  read_scope: repository
  write_scope:
    - src/main/java/com/example/security/**

capabilities:
  - git
  - java-build
  - openrewrite

constraints:
  - no_frontier_state_mutation
  - no_agent_to_agent_calls
  - no_scope_expansion

expected_output:
  type: WorkerResult
```

The exact implementation representation may differ, but these semantic fields must remain explicit.

---

# 34. Invocation Constraints

Every agent invocation should enforce, as applicable:

```text
no_frontier_state_mutation
no_agent_to_agent_calls
no_scope_expansion
bounded_execution
structured_output
explicit_capabilities
explicit_authorization
```

Additional constraints may be added by specific workflows.

---

# 35. Error Handling

Agent errors must become structured workflow evidence.

Do not allow an exception or free-form agent message to implicitly control the workflow.

Example:

```yaml
agent_error:
  category: EXECUTION_FAILURE
  message: Build command failed
  retryable: true
```

Frontier maps the error and evidence to a workflow outcome.

Possible classification:

```text
IMPLEMENTATION_ISSUE
PLAN_ISSUE
DEPENDENCY_ISSUE
ENVIRONMENT_ISSUE
CAPABILITY_ISSUE
```

Classification is advisory unless a deterministic rule explicitly defines the transition.

---

# 36. Agent Result Is Not State

Keep these concepts separate.

Bad:

```yaml
worker:
  state: COMPLETE
```

Good:

```yaml
worker_result:
  outcome: SUCCESS
  summary: ...
```

Then:

```text
Frontier evaluates WorkerResult
        +
actual workspace
        +
verification
        +
task acceptance
        ↓
Frontier Task State = COMPLETE
```

This separation is essential for deterministic orchestration.

---

# 37. Agent Result Is Not Approval

Likewise:

```text
Planner → proposes plan
```

does not mean:

```text
Planner → approves plan
```

And:

```text
Worker → reports success
```

does not mean:

```text
Worker → approves completion
```

And:

```text
Verifier → reports verification outcome
```

does not mean:

```text
Verifier → controls recovery
```

Frontier owns the decision boundary.

---

# 38. Agent Workflow vs Tool Workflow

Not every operation needs an agent.

Use deterministic capability execution when the operation is deterministic.

Examples:

```text
Repository inspection → RepositoryInspector
Git diff → Git capability
Compilation → Java Build capability
OpenRewrite execution → OpenRewrite capability
Scope comparison → deterministic validation
DAG validation → deterministic validation
Persistence → ProjectStore
```

Use an agent when interpretation or semantic reasoning is required.

Examples:

```text
Repository modernization planning → Planner
Semantic code modification → Worker
```

Do not create an agent simply because an operation is part of a workflow.

---

# 39. Minimal Agent Architecture

The preferred V1 execution architecture is:

```text
                    ┌─────────────────────┐
                    │      Frontier       │
                    │  Workflow Control   │
                    └─────────┬───────────┘
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
      ┌──────────────┐                  ┌──────────────┐
      │    Planner   │                  │    Worker    │
      │    Agent     │                  │    Agent     │
      └──────┬───────┘                  └──────┬───────┘
             │                                 │
             └──────────────┬──────────────────┘
                            ▼
                 ┌────────────────────┐
                 │  Deterministic     │
                 │  Capabilities      │
                 │                    │
                 │ Inspector / Git    │
                 │ Build / Rewrite    │
                 │ Verification       │
                 └────────────────────┘
```

This is intentionally small.

---

# 40. What Claude Code Must NOT Infer

Claude Code must not infer additional agent architecture merely from the word "agent".

Do not automatically introduce:

- Supervisor Agent
- Discovery Agent
- Review Agent
- QA Agent
- Security Agent
- Dependency Agent
- Coordinator Agent
- Communication Agent
- Memory Agent
- Tool Agent
- Agent Manager
- Agent Registry
- Agent Pool
- Agent Scheduler

unless a later requirement explicitly defines one.

A role should become an agent only when its responsibilities require bounded reasoning and its contract is explicitly defined.

---

# 41. Implementation Rule for New Agents

If a future feature appears to require a new agent, define the following before implementing it:

```text
1. Why deterministic logic is insufficient
2. What reasoning the agent performs
3. What input context it receives
4. What capabilities it requires
5. What it is authorized to change
6. What structured result it returns
7. What evidence supports the result
8. Which Frontier workflow invokes it
9. Which Frontier state precedes the invocation
10. Which Frontier state may follow it
11. How failure is classified
12. How recovery works
13. How invocation history is persisted
```

If these cannot be defined clearly, the new agent is probably not sufficiently scoped.

---

# 42. Implementation Rule for New Agent Workflows

Before adding an agent-backed workflow, verify:

```text
[ ] Entry condition is explicit
[ ] Frontier state is explicit
[ ] Agent role already exists or is explicitly defined
[ ] Invocation identity is explicit
[ ] Context is explicit
[ ] Capabilities are explicit
[ ] Write scope is explicit
[ ] Agent result is structured
[ ] Actual workspace changes are inspected
[ ] Deterministic validation exists
[ ] Verification requirements are explicit
[ ] Frontier owns the resulting state transition
[ ] Recovery is explicit
[ ] Persistence boundary is explicit
[ ] Next operation is selected by Frontier
[ ] No direct agent-to-agent control exists
[ ] No autonomous unbounded loop exists
```

---

# 43. Canonical End-to-End Example

For a modernization task:

```text
Task becomes READY
        ↓
Frontier selects Worker
        ↓
Frontier creates invocation:
    task = task-007
    scope = security package
    capabilities = git + java-build + openrewrite
        ↓
Frontier assembles WorkerContext
        ↓
Worker executes bounded modernization
        ↓
Worker returns WorkerResult
        ↓
Frontier inspects actual Git diff
        ↓
Frontier checks write scope
        ↓
Java build runs
        ↓
Verifier evaluates required checks
        ↓
Completion Gate
        │
        ├── PASS
        │     ↓
        │   Task COMPLETE
        │
        └── FAIL
              ↓
          RecoveryPolicy
              │
              ├── RETRY
              ├── REPAIR
              ├── REPLAN
              ├── BLOCK
              ├── HUMAN_GATE
              └── FAIL
```

The Worker never decides which branch is taken.

---

# 44. Canonical Language for Documentation

Use wording such as:

> Frontier invokes the Worker for a bounded task using an explicit context, capability set, and authorization scope.

> The Worker performs the assigned operation and returns a structured WorkerResult.

> Frontier inspects the actual workspace and Git diff after the invocation.

> Frontier validates the result and determines the resulting task state.

> If the task cannot safely continue, Frontier applies the configured recovery policy.

> The Planner proposes a plan; Frontier validates and adopts the plan.

> Agents do not communicate directly. Results are passed through Frontier-controlled workflow state and invocation context.

Avoid wording such as:

> The Worker manages the task.

> The agents coordinate with each other.

> The Worker decides whether to retry.

> The Planner sends work to the Worker.

> The Verifier tells the system what to do next.

These statements blur control ownership.

---

# 45. Relationship to Existing Frontier Documents

This document does not replace the existing architecture, state, workflow, contract, or toolset documents.

It fills the implementation gap between:

```text
Agent Roles
```

and:

```text
Executable Agent Workflow
```

Use the documents together:

```text
IMPLEMENTATION-SPEC
        ↓
defines architecture and constraints

AGENT-WORKFLOW-RULES
        ↓
defines executable agent invocation semantics

states/
        ↓
defines legal states

workflows/
        ↓
defines workflow sequences

agents/
        ↓
defines agent roles and contracts

toolsets/
        ↓
defines deterministic capabilities

contracts/
        ↓
defines structured inputs/outputs

orchestrator/
        ↓
implements Frontier control

ProjectStore
        ↓
persists authoritative state
```

---

# 46. Final Implementation Principle

The most important rule is:

> **Do not build "an AI system that happens to have agents." Build a deterministic workflow engine that invokes bounded reasoning agents at explicit points.**

The architecture should therefore remain:

```text
Deterministic Frontier
        +
Explicit Agent Definitions
        +
Explicit Agent Invocations
        +
Bounded Context
        +
Bounded Capabilities
        +
Explicit Authorization
        +
Structured Results
        +
Workspace/Git Authority
        +
Deterministic Validation
        +
Explicit State Transitions
        +
Bounded Recovery
        +
Persisted History
```

This is the intended meaning of an **agentic workflow** in Frontier V1.
