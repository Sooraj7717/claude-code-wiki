# Frontier — Claude Code Implementation Brief

## Objective

Build **Frontier**, a working prototype of the Uplift Orchestrator for Java modernization.

Initial modernization scenario:

- Source: Java 8
- Spring Boot: 1.5.x
- Target: Java 21
- Spring Boot: 3.5.x

Frontier is a **deterministic workflow controller**.

> Agents reason and execute work.  
> Frontier owns workflow state, validation, gates, and transitions.

Frontier itself must **not become an LLM agent**.

The goal of Frontier is to prove the orchestration model on a real repository while keeping the implementation small, fast, deterministic, and easy to evolve into a production implementation later.

---

# 1. Prototype Philosophy

Frontier deliberately implements the **control model**, not the complete production orchestration platform.

The prototype should favor:

```text
small deterministic core
+
explicit contracts
+
real repository execution
+
simple persistence
+
replaceable adapters
+
strong validation
```

over:

```text
distributed orchestration
event sourcing
complex scheduling
worker pools
load balancing
microservices
agent-to-agent communication
workflow optimization
```

The prototype must still enforce the architectural boundaries that are difficult to retrofit later.

---

# 2. Frontier Architecture

```text
                         FRONTIER
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                Deterministic Workflow Kernel                │
│                                                             │
│   ┌─────────────┐                                           │
│   │ Project     │                                           │
│   │ State       │                                           │
│   └──────┬──────┘                                           │
│          │                                                  │
│   ┌──────▼──────┐                                           │
│   │ Task Graph  │                                           │
│   │ / DAG       │                                           │
│   └──────┬──────┘                                           │
│          │                                                  │
│   ┌──────▼──────────────────────────────────────────────┐    │
│   │ Deterministic Kernel                                │    │
│   │                                                    │    │
│   │ • state transitions                                │    │
│   │ • dependency validation                            │    │
│   │ • scope validation                                 │    │
│   │ • conflict validation                              │    │
│   │ • completion gate                                  │    │
│   │ • recovery policy                                  │    │
│   └──────┬─────────────────────────────────────────────┘    │
│          │                                                  │
│          ▼                                                  │
│      Simple Task Runner                                     │
│          │                                                  │
│     ┌────┼───────────┐                                      │
│     ▼    ▼           ▼                                      │
│ Discovery Planner   Worker                                  │
│ Adapter   Adapter  Adapter                                  │
│                       │                                     │
│                       ▼                                     │
│                    Verifier                                 │
│                    Adapter                                  │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    Repository Workspace
```

Agents/capabilities communicate **only through Frontier contracts**.

There must be no direct Planner → Worker, Worker → Planner, or Worker → Verifier control flow.

---

# 3. Core Domain Model

Frontier uses:

```text
Project
  └── Tasks
        └── Files
```

### Project

The Project is the workflow container.

It owns:

- project state
- modernization objective
- repository/workspace information
- task collection
- workflow metadata
- project evidence
- acceptance criteria

### Task

A Task is the primary executable unit.

A Task owns:

- objective
- dependencies
- authorized write scope
- required context
- constraints
- capability requirements
- preferred Worker
- verification strategy
- execution attempts
- evidence
- current state

### File

Files are resources touched by Tasks.

Files are **not** the primary workflow unit.

---

# 4. Project State Model

Frontier implements:

```text
INITIALIZING
    ↓
DISCOVERING
    ↓
PLANNING
    ↓
EXECUTING
    ↓
COMPLETING
    ↓
COMPLETE
```

Control/recovery states:

```text
BLOCKED
HUMAN_GATE
FAILED
```

Frontier does **not** require a persistent `REPLANNING` project state.

Replanning is treated as an orchestration operation:

```text
EXECUTING
    ↓
Planner
    ↓
validate revised plan
    ↓
EXECUTING
```

This keeps the project state machine small without removing replanning capability.

---

# 5. Project State Semantics

### INITIALIZING

Establish:

- project identity
- repository/workspace
- Frontier workspace
- initial configuration

No modernization work is performed.

### DISCOVERING

Collect baseline modernization evidence.

Discovery is strictly read-only.

### PLANNING

Planner generates the initial execution plan.

### EXECUTING

Tasks are executed and verified.

### BLOCKED

Execution cannot safely continue until a blocking condition is resolved.

### HUMAN_GATE

Human decision is required.

### COMPLETING

All required Tasks are complete and project-level acceptance is being performed.

### COMPLETE

Modernization objectives have been accepted.

### FAILED

The workflow cannot safely continue.

`FAILED` is terminal.

---

# 6. Task State Model

Frontier uses the following Task states:

```text
BLOCKED
   ↓
READY
   ↓
EXECUTING
   ↓
VERIFYING
   ├── success → COMPLETE
   └── failure → recovery
                    │
                    ├── retry
                    ├── repair
                    ├── replan
                    ├── human gate
                    └── FAILED
```

Frontier does not require persistent `REPAIRING` or `REPLANNING` Task states.

Repair is another execution cycle:

```text
VERIFYING
    ↓
repair decision
    ↓
EXECUTING
```

Replanning is an orchestration operation.

---

# 7. State Transition Rules

The state machine must be deterministic.

Agents cannot directly change Project or Task state.

Only Frontier may perform transitions.

Examples:

```text
INITIALIZING → DISCOVERING
DISCOVERING → PLANNING
PLANNING → EXECUTING
EXECUTING → COMPLETING
COMPLETING → COMPLETE
```

Recovery:

```text
EXECUTING → BLOCKED
EXECUTING → HUMAN_GATE
EXECUTING → FAILED

VERIFYING → EXECUTING
VERIFYING → HUMAN_GATE
VERIFYING → FAILED
```

Invalid transitions must be rejected.

Completed Tasks are immutable by default.

If completed work must change:

```text
preferred:
    create superseding Task
```

Explicit reopening may be supported later but is not required for Frontier.

---

# 8. Task DAG

Task dependencies form a strict directed acyclic graph.

If:

```text
Task B depends on Task A
```

then:

```text
A must be COMPLETE
before B becomes READY
```

Dependencies must be explicit.

Frontier must never infer dependencies automatically.

---

# 9. DAG Validation

Whenever a plan is created or changed, Frontier must validate:

```text
Task IDs are unique
        +
all referenced dependencies exist
        +
no dependency cycles
        +
dependency relationships are valid
```

Example:

```text
A → B → C
      └→ D
```

is valid.

```text
A → B → C → A
```

must be rejected.

DAG validation is mandatory before execution begins and after replanning.

---

# 10. Task Readiness

A Task becomes `READY` only when:

```text
Task is not COMPLETE
        AND
all dependencies are COMPLETE
        AND
Task is not blocked
        AND
required project conditions are satisfied
```

Frontier should reconcile readiness deterministically.

No LLM should decide whether a Task is READY.

---

# 11. File Scope

Every executable Task has an explicit authorized write scope.

Example:

```text
Task:
  authorized_write_files:
    - pom.xml
    - src/main/java/com/example/Foo.java
```

Workers may:

```text
READ broadly
```

but may only:

```text
WRITE within authorized scope
```

The Worker must never expand its own scope.

---

# 12. Scope Enforcement

Worker-reported changes are evidence only.

After Worker execution Frontier must inspect the actual workspace changes.

Conceptually:

```text
Worker execution
      ↓
workspace diff
      ↓
actual changed files
      ↓
scope validator
```

Completion is rejected if:

```text
actual_changed_files
    ⊄
authorized_write_files
```

An out-of-scope modification must trigger recovery.

The Worker cannot self-authorize additional files.

---

# 13. Resource Conflicts

Frontier must prevent unsafe concurrent modifications.

For the prototype, execution may be **sequential by default**.

This means runtime conflict management can remain extremely simple.

However, the plan validator must still detect unsafe overlapping scopes.

Example:

```text
Task A writes Foo.java
Task B writes Foo.java
```

If there is no explicit dependency:

```text
INVALID PLAN
```

Frontier must not invent a dependency automatically.

The same principle applies to overlapping directories or other explicitly modeled write resources if Frontier supports them.

---

# 14. Prototype Execution Model

Frontier should initially use a simple task runner:

```text
find READY task
      ↓
execute Worker
      ↓
inspect actual diff
      ↓
verify
      ↓
completion gate
      ↓
update state
      ↓
persist
      ↓
repeat
```

Single-task execution is acceptable for the prototype.

The domain model should not prevent future parallel execution, but Frontier should not implement a sophisticated scheduler.

---

# 15. Task Runner

The Task Runner is deterministic.

Conceptually:

```text
while project is executable:

    reconcile task readiness

    select a READY task

    execute Worker

    validate actual changes

    execute Verifier

    evaluate completion gate

    apply recovery policy if necessary

    persist state
```

The Task Runner must never ask an LLM to determine basic workflow legality.

---

# 16. Discovery

Discovery is first-class but deliberately lightweight.

Discovery is:

```text
READ-ONLY
```

It may use:

```text
Maven / Gradle
Java parsing
dependency analysis
Git inspection
OpenRewrite analysis
static analysis
LLM repository exploration
```

Frontier should expose Discovery through an adapter.

Example:

```text
Discovery
    discover(ProjectContext)
        →
    DiscoveryResult
```

DiscoveryResult should contain:

```text
artifacts
evidence
issues
recommendations
```

Baseline Discovery completion must be determined by the workflow definition, not simply by whether every discovery tool ran.

---

# 17. Planner

The Planner is an LLM-based modernization strategist.

The Planner is:

```text
READ-ONLY with respect to the repository
```

The Planner may:

- inspect repository information
- interpret Discovery evidence
- request additional context
- propose Tasks
- define dependencies
- define file scopes
- define verification strategy
- recommend capabilities
- recommend Workers
- propose plan changes

The Planner may **not**:

- mutate Project state
- directly execute Workers
- directly execute Verifiers
- bypass scope validation
- bypass DAG validation
- override Frontier policy
- mark Tasks complete

---

# 18. Planner Contract

Planner input:

```text
Project Context
+
Discovery Evidence
+
Existing Task State
+
Existing Project State
```

Planner output:

```text
ExecutionPlan
    └── tasks[]
```

Each Task must contain:

```text
task_id
objective
dependencies
required_context
authorized_write_files
constraints
capability_requirements
preferred_worker
verification_strategy
```

Frontier validates the returned plan before accepting it.

---

# 19. Replanning

Replanning is evidence-driven.

It may be triggered by:

```text
Discovery evidence
Worker evidence
Verifier evidence
dependency analysis
repository conditions
```

A failure does not automatically imply replanning.

When replanning is required, the Planner receives:

```text
complete current project state
+
complete task state
+
existing evidence
+
triggering evidence
```

The Planner may revise the remaining plan.

Completed work/history must be preserved.

Unaffected Tasks should be preserved where possible.

Affected Tasks may be revised or replaced.

Frontier determines the affected execution boundary.

After planning:

```text
Planner
   ↓
DAG validation
   ↓
scope/conflict validation
   ↓
policy validation
   ↓
EXECUTING
```

---

# 20. Worker Model

Workers perform actual modernization work.

A Worker is an adapter/capability.

Potential implementations include:

```text
Claude
Codex
OpenRewrite
other deterministic capability
```

OpenRewrite should be treated as a deterministic modernization capability rather than forcing it into an agent abstraction.

For Frontier, only a small number of concrete Worker implementations are required.

At minimum:

```text
one real Worker
+
one Mock Worker
```

The Mock Worker is important for testing the orchestration kernel without invoking an LLM.

---

# 21. Worker Contract

Worker input:

```text
Task Contract
  ├── task_id
  ├── objective
  ├── authorized_write_files
  ├── required_context
  ├── constraints
  ├── capability_requirements
  ├── preferred_worker
  └── verification_strategy
```

Worker output:

```text
WorkerResult
  ├── outcome
  ├── changes
  ├── evidence
  ├── issues
  └── requests
        ├── context_request
        └── capability_request
```

Worker results are evidence.

The Worker cannot declare the Task complete.

Frontier determines completion.

---

# 22. Verifier

Every executable Task requires verification.

Verifier is:

```text
READ-ONLY
```

Verifier may:

- build
- test
- analyze
- inspect repository state
- inspect generated changes

Verifier must never modify source code.

---

# 23. Verifier Contract

Verifier input:

```text
Task
+
verification_strategy
+
required_context
```

Verifier output:

```text
VerificationResult
  ├── outcome
  ├── checks_performed
  ├── evidence
  ├── failures
  └── advisory_classification
```

Classification:

```text
IMPLEMENTATION_ISSUE
PLAN_ISSUE
DEPENDENCY_ISSUE
ENVIRONMENT_ISSUE
```

These classifications are advisory.

Frontier owns the actual recovery decision.

---

# 24. Task Completion Gate

A Task can become `COMPLETE` only when:

```text
Worker result exists
        AND
actual workspace diff is within authorized scope
        AND
required deterministic checks pass
        AND
Verifier evidence supports success
```

Therefore:

```text
Worker success ≠ Task completion
```

The core Frontier rule is:

> **Agents provide evidence. Frontier owns state.**

---

# 25. Recovery Policy

Frontier should implement a small deterministic recovery policy.

Supported decisions:

```text
RETRY
REPAIR
REPLAN
BLOCK
HUMAN_GATE
FAIL
```

Example initial policy:

```text
transient execution problem
        → RETRY

implementation/code failure
        → REPAIR

planning/dependency problem
        → REPLAN

unsafe/unresolved situation
        → HUMAN_GATE

retry/recovery exhausted
        → FAILED
```

The policy should remain deterministic.

Agents may recommend a recovery action, but Frontier decides.

---

# 26. Retry

Retries must be bounded.

Each Task should track:

```text
attempt_count
```

Frontier configuration should define a small retry limit.

Example:

```text
max_attempts = 2
```

Do not implement sophisticated exponential backoff, distributed retry queues, or retry scheduling in Frontier.

---

# 27. Repair

Repair means another Worker execution against the same Task.

The original Task scope remains authoritative.

```text
VERIFYING
    ↓
REPAIR
    ↓
EXECUTING
```

A Worker cannot use repair as a mechanism to expand its write scope.

If additional files are required:

```text
request
   ↓
Planner
   ↓
revised Task/plan
```

---

# 28. Human Gate

Frontier supports a basic human gate.

A human gate is required when:

```text
workflow policy requires it
OR
automation cannot safely resolve the issue
```

Agents may recommend a human gate.

Only Frontier creates the actual gate.

Human decision:

```text
APPROVE
    ↓
legal Frontier transition

REJECT
    ↓
replan
```

For Frontier, human-gate persistence may simply be represented in project state.

No separate approval service is required.

---

# 29. Project Completion

When all required executable Tasks are:

```text
COMPLETE
```

Frontier transitions:

```text
EXECUTING
    ↓
COMPLETING
```

During `COMPLETING`:

1. run required project-level verification
2. assess modernization objectives
3. validate acceptance criteria

Then:

```text
COMPLETING → COMPLETE
```

The Planner may provide an assessment, but Frontier validates completion against explicit acceptance criteria.

---

# 30. Persistence

Frontier should use simple local persistence.

Do **not** implement:

```text
event sourcing
distributed database
message broker
workflow database
```

Recommended initial structure:

```text
.frontier/
├── project.json
├── tasks.json
└── evidence/
    ├── task-001.json
    ├── task-002.json
    └── ...
```

Persistence must occur at meaningful workflow boundaries.

At minimum persist after:

```text
state transition
Worker execution
verification
recovery decision
plan update
human decision
```

The persistence implementation should be behind a simple interface so it can later be replaced.

Example:

```text
ProjectStore
    load(projectId)
    save(project)
```

---

# 31. Evidence Model

Evidence should remain lightweight.

Suggested model:

```text
Evidence
  ├── id
  ├── source
  ├── type
  ├── summary
  ├── timestamp
  └── artifact/reference
```

Possible sources:

```text
DISCOVERY
PLANNER
WORKER
VERIFIER
SYSTEM
HUMAN
```

Evidence is append-oriented.

Evidence does not itself change workflow state.

---

# 32. Workspace Model

Frontier operates against a repository workspace.

The prototype should assume:

```text
one project
one workspace
one active execution context
```

Do not build workspace clusters, distributed locks, remote execution pools, or sandbox orchestration.

Workers should execute within the workspace abstraction exposed by Frontier.

---

# 33. Agent Interaction Rule

There must be no direct agent-to-agent control flow.

Correct:

```text
              ┌──────────────┐
              │   Frontier   │
              └──────┬───────┘
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    Planner        Worker       Verifier
       │             │             │
       └─────────────┴─────────────┘
                     │
               Result/Evidence
                     ↓
                  Frontier
```

Incorrect:

```text
Planner → Worker
Worker → Planner
Worker → Verifier
Verifier → Worker
```

All interactions go through Frontier.

---

# 34. Frontier Responsibilities

Frontier owns:

```text
Project state
Task state
State transitions
Task readiness
DAG validation
Dependency validation
File-scope enforcement
Conflict validation
Worker routing
Verifier routing
Completion gates
Retry decisions
Recovery decisions
Replanning orchestration
Human gates
Project completion
Persistence
Evidence recording
```

---

# 35. Frontier Non-Responsibilities

Frontier must NOT:

```text
reason about source code as an LLM
modify source code
perform modernization itself
allow agents to mutate workflow state
infer unsafe dependencies
allow Workers to expand scope
allow Workers to declare completion
allow Verifiers to modify source
implement agent-to-agent communication
```

---

# 36. Prototype Non-Goals

The following are explicitly **out of scope for Frontier**:

```text
distributed execution
worker pools
load balancing
event sourcing
message brokers
microservices
remote worker orchestration
persistent agent sessions
dynamic dependency inference
automatic scope expansion
speculative parallel execution
advanced scheduling
workflow optimization
complex reconciliation engines
agent optimization
multi-project scheduling
multi-tenant infrastructure
high availability
leader election
distributed locking
```

These may be introduced in a future production implementation.

---

# 37. Performance Principles

Frontier should be efficient without introducing distributed-system complexity.

Use:

```text
in-process orchestration
in-memory active state
simple local persistence
bounded execution
deterministic validation
minimal serialization
adapter-based external calls
```

Avoid unnecessary:

```text
network hops
database round trips
message queues
service boundaries
LLM calls for deterministic decisions
repeated repository scans
```

The orchestration kernel should be cheap relative to Worker/Verifier execution.

---

# 38. Performance-Critical Design Rule

LLMs should only be invoked when reasoning is actually required.

Do not use an LLM for:

```text
DAG validation
state transitions
dependency readiness
scope validation
diff inspection
retry counting
policy checks
completion gating
```

These operations must remain deterministic.

Use LLMs for:

```text
repository interpretation
planning
semantic code changes
semantic verification where required
recovery recommendations
```

This is a core Frontier performance principle.

---

# 39. Recommended Prototype Structure

Use a small modular structure similar to:

```text
frontier/
│
├── workflow/
│   ├── project
│   ├── task
│   ├── state
│   ├── transition
│   ├── dag
│   ├── scope
│   └── completion
│
├── orchestration/
│   ├── task-runner
│   └── recovery
│
├── contracts/
│   ├── planner
│   ├── worker
│   ├── verifier
│   └── evidence
│
├── adapters/
│   ├── discovery
│   ├── planner
│   ├── worker
│   └── verifier
│
├── persistence/
│   └── project-store
│
└── tests/
    ├── workflow
    ├── dag
    ├── scope
    ├── completion
    └── orchestration
```

Do not create packages merely to anticipate future infrastructure.

---

# 40. Testing Strategy

The workflow kernel must be thoroughly tested before integrating LLMs.

### State-machine tests

Test:

```text
valid transitions
invalid transitions
terminal states
blocked transitions
human gates
failure handling
```

### DAG tests

Test:

```text
valid DAG
missing dependency
duplicate Task ID
simple cycle
complex cycle
replanning DAG
```

### Scope tests

Test:

```text
all changes within scope
single out-of-scope file
multiple out-of-scope files
new file outside scope
deleted file outside scope
repair retaining original scope
```

### Completion tests

Test:

```text
Worker success + verification success → COMPLETE

Worker success + scope violation → not COMPLETE

Worker success + verifier failure → not COMPLETE

Verifier success without Worker result → not COMPLETE

deterministic check failure → not COMPLETE
```

### Recovery tests

Test:

```text
retry
repair
replan
blocked
human gate
failure after exhausted attempts
```

### Orchestration tests

Use Mock Workers and Mock Verifiers to test:

```text
READY → EXECUTING → VERIFYING → COMPLETE
```

without invoking external LLMs.

---

# 41. First Implementation Milestone

Before implementing real agents or modernization logic, Claude Code must build the workflow kernel.

Implement:

```text
1. Project model
2. Task model
3. Project state model
4. Task state model
5. State transition rules
6. DAG representation
7. DAG validation
8. Task readiness calculation
9. File-scope model
10. Scope validation
11. Resource conflict validation
12. Worker result contract
13. Verifier result contract
14. Evidence model
15. Completion gate
16. Recovery decision model
17. Basic Task Runner
18. Simple ProjectStore
19. Unit tests
```

Then stop.

Do not implement the real Planner, Worker, or Verifier until the kernel is coherent and tested.

---

# 42. Second Implementation Milestone

After the kernel is tested:

```text
Discovery adapter
Planner adapter
Worker adapter
Verifier adapter
```

Implement one concrete path end-to-end:

```text
Discovery
    ↓
Planner
    ↓
Task
    ↓
Worker
    ↓
Scope validation
    ↓
Verifier
    ↓
Completion gate
```

Use mocks wherever the external capability is not yet ready.

---

# 43. Third Implementation Milestone

Demonstrate a real modernization workflow against a small Java repository.

Example:

```text
Java 8
Spring Boot 1.5.x
        ↓
Discovery
        ↓
Planner
        ↓
Task DAG
        ↓
OpenRewrite / Worker
        ↓
semantic fixes
        ↓
verification
        ↓
completion
```

The demonstration should prove that Frontier can:

```text
plan
execute
validate
verify
recover
persist
resume
```

without Frontier itself performing LLM reasoning.

---

# 44. Claude Code Implementation Rules

Claude Code must follow these rules:

### Rule 1 — Inspect before modifying

First inspect:

```text
repository structure
build system
existing code
tests
configuration
```

Do not assume the repository layout.

### Rule 2 — Minimize architecture

When an implementation choice is unspecified:

> Choose the simplest deterministic design that preserves the Frontier architectural boundaries.

Document the decision.

### Rule 3 — Do not introduce speculative infrastructure

Do not add:

```text
Kafka
Redis
Postgres
Kubernetes
microservices
message buses
distributed locks
event stores
```

unless explicitly required.

### Rule 4 — Preserve boundaries

Never allow:

```text
Worker → state mutation
Planner → state mutation
Verifier → state mutation
Worker → Worker
Planner → Worker
Verifier → Worker
```

### Rule 5 — Prefer interfaces at external boundaries

Use interfaces for:

```text
Discovery
Planner
Worker
Verifier
ProjectStore
```

The workflow kernel itself should remain concrete and deterministic where possible.

### Rule 6 — Test behavior, not implementation details

Tests should primarily validate:

```text
legal behavior
state transitions
invariants
contracts
workflow outcomes
```

---

# 45. Important Invariants

Frontier must maintain these invariants.

### State invariant

Only Frontier can mutate workflow state.

### Dependency invariant

A Task cannot become READY until all dependencies are COMPLETE.

### DAG invariant

The accepted Task graph must never contain a cycle.

### Scope invariant

A Worker cannot modify files outside its authorized write scope.

### Verification invariant

An executable Task cannot become COMPLETE without successful verification.

### Evidence invariant

Agent results are evidence, not authoritative state.

### Completion invariant

Worker success alone never completes a Task.

### Recovery invariant

Agents may recommend recovery, but Frontier decides recovery.

### Communication invariant

Agents cannot directly control other agents.

### History invariant

Completed work is not silently rewritten during replanning.

---

# 46. Definition of Done — Frontier Prototype

Frontier is considered prototype-complete when it can demonstrate:

```text
1. Initialize a project
2. Perform read-only discovery
3. Generate an execution plan
4. Validate the Task DAG
5. Validate file scopes
6. Detect unsafe scope conflicts
7. Select READY Tasks
8. Execute a Worker
9. Inspect actual workspace changes
10. Reject out-of-scope changes
11. Run a Verifier
12. Apply the completion gate
13. Retry a recoverable failure
14. Repair a Task
15. Trigger replanning
16. Pause for human approval
17. Persist workflow state
18. Resume from persisted state
19. Complete the project
20. Fail safely when recovery is exhausted
```

The prototype does **not** need distributed execution or sophisticated scheduling to satisfy this definition.

---

# 47. Final Architectural Principle

Frontier should remain small.

The desired architecture is:

```text
                 ┌───────────────────────┐
                 │       FRONTIER        │
                 │                       │
                 │ deterministic kernel  │
                 │                       │
                 │ state                 │
                 │ DAG                   │
                 │ scope                 │
                 │ validation            │
                 │ verification          │
                 │ recovery              │
                 │ persistence           │
                 └───────────┬───────────┘
                             │
                ┌────────────┼────────────┐
                ↓            ↓            ↓
             Planner       Worker      Verifier
                │            │            │
                └────────────┴────────────┘
                             │
                             ↓
                         Repository
```

The fundamental separation is:

> **Frontier decides what is legal. Agents decide how to perform the work.**

Do not compromise that boundary in the name of prototype simplicity.

At the same time:

> **Do not build production infrastructure before the workflow model has been proven.**

Frontier is successful if the deterministic kernel is small, understandable, well-tested, and capable of orchestrating real modernization work efficiently.