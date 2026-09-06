# Frontier — Claude Code Implementation Brief V1

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

The goal of Frontier V1 is to prove the orchestration model on a real repository while keeping the implementation small, fast, deterministic, and easy to evolve into a production implementation later.

V1 deliberately reduces agent and orchestration complexity without removing the workflow guarantees that make Frontier valuable.

---

# 1. Prototype Philosophy

Frontier V1 deliberately implements the **control model**, not the complete production orchestration platform.

The prototype should favor:

```text
small deterministic core
+
explicit contracts
+
real repository execution
+
strong validation
+
limited LLM usage
+
simple persistence
+
replaceable adapters
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
capability registries
iterative context orchestration
workflow optimization
```

The most important architectural boundaries must remain intact because they are difficult to retrofit later.

The V1 principle is:

> **Reduce abstractions, not guarantees.**

---

# 2. Frontier Architecture

```text
                           FRONTIER
                Deterministic Workflow Controller
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  Project State + Task Graph + Deterministic Kernel                │
│                                                                    │
│   ┌───────────────────┐                                            │
│   │ Repository         │                                            │
│   │ Inspector          │                                            │
│   │ deterministic      │                                            │
│   └─────────┬─────────┘                                            │
│             │ RepositoryContext                                    │
│             ▼                                                      │
│   ┌───────────────────┐                                            │
│   │ Planner            │                                            │
│   │ LLM reasoning      │                                            │
│   └─────────┬─────────┘                                            │
│             │ ExecutionPlan                                       │
│             ▼                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ Plan / State / DAG / Scope / Conflict Validation            │   │
│   └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│                       Simple Task Runner                            │
│                              │                                      │
│                              ▼                                      │
│                         ┌──────────┐                                │
│                         │  Worker  │                                │
│                         │ LLM/tool │                                │
│                         └────┬─────┘                                │
│                              │                                      │
│                              ▼                                      │
│                    Actual Workspace Diff                            │
│                              │                                      │
│                              ▼                                      │
│                   Scope Validation + Verifier                       │
│                              │                                      │
│                 ┌────────────┴────────────┐                         │
│                 ▼                         ▼                         │
│          Deterministic checks      Semantic verification            │
│                                      only when needed                │
│                                                                    │
│   Frontier decides completion, recovery, persistence, and gates.   │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
                         Repository Workspace
```

V1 uses two reasoning-oriented capabilities:

```text
Planner
Worker
```

and lightweight deterministic/capability boundaries:

```text
RepositoryInspector
Verifier
RecoveryPolicy
ProjectStore
```

These are capabilities, not independent communicating agents.

There must be no direct Planner → Worker, Worker → Planner, or Worker → Verifier control flow. All interactions are mediated by Frontier.

---

# 3. Core Domain Model

Frontier uses:

```text
Project
  └── Tasks
```

Files remain resources represented by paths/scopes rather than first-class workflow entities.

### Project

The Project is the workflow container.

It owns:

- project state
- modernization objective
- repository/workspace information
- task collection
- current plan
- plan history
- project evidence/artifacts
- acceptance criteria
- workflow metadata

### Task

A Task is the primary executable unit.

A Task owns:

- task ID
- objective
- dependencies
- authorized write scope
- verification strategy
- optional constraints/context requirements
- execution attempts
- evidence/artifacts
- current state

V1 should avoid speculative task metadata such as worker selection or capability negotiation unless a concrete implementation requires it.

### Files

Files are resources touched by Tasks.

Files are **not** primary workflow entities.

```text
authorized_write_files: list[path]
```

is sufficient for V1.

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

Frontier does not require a persistent `REPLANNING` project state.

Replanning is an orchestration operation:

```text
EXECUTING
    ↓
Planner
    ↓
validate revised plan
    ↓
EXECUTING
```

The V1 implementation may record plan versions without introducing an additional project state.

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

Collect baseline modernization context.

Discovery is strictly read-only.

V1 Discovery is implemented primarily by the deterministic `RepositoryInspector`. Optional LLM repository exploration may be used only when semantic interpretation is actually required.

### PLANNING

Planner generates or revises the execution plan.

### EXECUTING

Tasks are selected, executed, scope-checked, verified, and completed or recovered.

### BLOCKED

Execution cannot safely continue until a blocking condition is resolved.

### HUMAN_GATE

Human decision is required.

### COMPLETING

All required executable Tasks are complete and project-level acceptance is being performed.

### COMPLETE

Modernization objectives and acceptance criteria have been accepted.

### FAILED

The workflow cannot safely continue.

`FAILED` is terminal.

---

# 6. Task State Model

Frontier uses:

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

Explicit reopening may be supported later but is not required for V1.

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

The V1 runner executes sequentially by default, even if the domain model leaves room for future parallelism.

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

DAG validation is mandatory before execution begins and after replanning.

No LLM participates in DAG legality checks.

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

Frontier reconciles readiness deterministically.

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

V1 should use the simplest reliable local mechanism available, preferably Git diff/status for repository-backed work.

---

# 13. Resource Conflicts

Frontier executes tasks sequentially by default.

Therefore runtime locking is intentionally simple.

However, the plan validator must still detect unsafe overlapping write scopes.

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

Directory/path overlap must also be detected when the V1 scope model supports it.

---

# 14. Prototype Execution Model

Frontier uses a simple task runner:

```text
find READY task
      ↓
execute Worker
      ↓
inspect actual diff
      ↓
validate scope
      ↓
run Verifier
      ↓
completion gate
      ↓
update state
      ↓
persist
      ↓
repeat
```

Single-task execution is the default V1 behavior.

Do not implement a sophisticated scheduler, worker pool, distributed locking, speculative parallel execution, or load-balancing system.

---

# 15. Task Runner

The Task Runner is deterministic.

Conceptually:

```text
while project is executable:

    reconcile task readiness

    select a READY task

    execute Worker

    inspect actual changes

    validate scope

    execute Verifier

    evaluate completion gate

    apply recovery policy if necessary

    persist state
```

The Task Runner must never ask an LLM to determine basic workflow legality.

The runner may stop for `BLOCKED`, `HUMAN_GATE`, or terminal `FAILED` states.

---

# 16. Discovery / Repository Inspection

Discovery remains a first-class workflow phase but is implemented as a lightweight capability, not a dedicated agent.

Discovery is:

```text
READ-ONLY
```

V1 `RepositoryInspector` should gather useful deterministic context such as:

```text
repository structure
build system
Java version
Spring Boot version
dependencies
modules
Git status/diff
relevant source/configuration inventory
```

It may invoke:

```text
Maven / Gradle
Java parsing
Git inspection
OpenRewrite analysis
static analysis
other local deterministic tools
```

LLM repository exploration is optional and should only be introduced where deterministic inspection cannot provide the required semantic information.

Repository inspection should normally be performed as a batched read-only operation rather than multiple specialized discovery agents.

Example:

```text
RepositoryInspector
    inspect(Project)
        ↓
RepositoryContext
```

`RepositoryContext` should contain structured facts and references to useful artifacts/logs.

Baseline Discovery completion is determined by the workflow definition, not merely by whether every tool ran.

---

# 17. Planner

The Planner is an LLM-based modernization strategist.

The Planner is:

```text
READ-ONLY with respect to the repository
```

The Planner may:

- interpret RepositoryContext
- interpret Discovery evidence
- inspect relevant repository context
- propose Tasks
- define dependencies
- define file scopes
- define verification strategy
- provide constraints
- propose plan changes
- recommend recovery/replanning when requested by Frontier

The Planner may not:

- mutate Project state
- directly execute Workers
- directly execute Verifiers
- bypass scope validation
- bypass DAG validation
- bypass policy
- mark Tasks complete
- modify repository source

V1 should not require an interactive Planner context-request loop during normal operation. Frontier should provide a sufficiently rich initial RepositoryContext.

A bounded optional additional-context mechanism may be supported when genuinely necessary.

---

# 18. Planner Contract

Planner input:

```text
Project objective
+
RepositoryContext
+
Current Project state
+
Current Task/plan state
+
Relevant evidence
```

Planner output:

```text
ExecutionPlan
    └── tasks[]
```

Each Task should contain at minimum:

```text
task_id
objective
dependencies
authorized_write_files
verification_strategy
```

Optional fields may include:

```text
constraints
required_context
```

V1 should avoid requiring `preferred_worker` or `capability_requirements` unless multiple concrete implementations actually exist.

Frontier validates every returned plan before accepting it.

---

# 19. Replanning

Replanning is evidence-driven.

It may be triggered by:

```text
new discovery evidence
Worker evidence
Verifier evidence
dependency analysis
repository conditions
repeated task failure
```

A failure does not automatically imply replanning.

Use the default recovery progression:

```text
attempt
   ↓
retry / repair where appropriate
   ↓
replan only when required
```

When replanning is required, Planner receives:

```text
current project state
+
current task state
+
existing evidence/artifacts
+
triggering evidence
```

The Planner may propose a revised plan.

Completed work/history must be preserved.

Unaffected Tasks should be preserved where practical.

V1 may implement this using simple plan versioning:

```text
Plan v1
   ↓
replan
   ↓
Plan v2
```

The implementation does not need a sophisticated graph-diff or affected-boundary engine.

Minimum replanning rule:

```text
completed tasks remain immutable
+
new plan must preserve completed history
+
new plan must pass DAG/scope/conflict/policy validation
```

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

A Worker is an execution capability.

Potential implementations include:

```text
Claude
Codex
OpenRewrite
other deterministic capability
```

OpenRewrite should be treated as a deterministic modernization capability rather than forcing it into an agent abstraction.

For Frontier V1, implement:

```text
one real Worker
+
one Mock Worker
```

The Mock Worker is important for testing the orchestration kernel without invoking an LLM.

If multiple Workers are introduced later, Frontier may add routing. V1 should not build a worker-selection framework merely in anticipation of that need.

---

# 21. Worker Contract

Worker input should be intentionally small:

```text
ExecutionContext
  ├── task
  ├── objective
  ├── authorized_write_files
  ├── verification_strategy
  ├── relevant_context
  └── repository/workspace
```

Worker output:

```text
WorkerResult
  ├── outcome
  ├── summary
  ├── evidence/artifacts
  └── requests
        ├── context_request (optional)
        └── capability_request (optional)
```

Worker results are evidence.

The Worker cannot declare the Task complete.

Worker-reported changed files are informational; Frontier derives the authoritative changed-file set from the workspace.

A Worker may request additional context or capability, but V1 should implement only simple bounded handling:

```text
supported request
    → satisfy deterministically

unsupported request
    → BLOCK / REPLAN / HUMAN_GATE according to policy
```

Do not build a dynamic capability marketplace or agent negotiation protocol.

---

# 22. Verifier

Every executable Task requires verification.

The Verifier is a **capability boundary**, not necessarily a separate LLM agent.

V1 should prefer deterministic verification.

Verifier may:

- build
- test
- analyze
- inspect repository state
- inspect generated changes
- perform semantic verification when deterministic checks are insufficient

The default verification sequence should be:

```text
actual diff
   ↓
scope validation
   ↓
deterministic checks
   ↓
semantic LLM verification only if required
```

Do not invoke an LLM merely to confirm a result that deterministic checks already establish.

Verifier must never modify source code.

---

# 23. Verifier Contract

Verifier input:

```text
Task
+
verification_strategy
+
relevant context
+
workspace state
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

Classification may be:

```text
IMPLEMENTATION_ISSUE
PLAN_ISSUE
DEPENDENCY_ISSUE
ENVIRONMENT_ISSUE
```

These classifications are advisory.

Frontier owns the actual recovery decision.

A deterministic verifier implementation should be sufficient for most V1 tasks.

An optional semantic verifier may be used for tasks whose acceptance criteria cannot be established reliably by deterministic checks alone.

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

Frontier implements a small deterministic recovery policy.

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

Agents may recommend a recovery action, but Frontier decides.

Failure classification from the Verifier is input to policy, not policy itself.

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

Do not implement sophisticated exponential backoff, distributed retry queues, retry schedulers, or retry workers in Frontier V1.

---

# 27. Repair

Repair means another Worker execution against the same Task using the same authoritative write scope.

```text
VERIFYING
    ↓
repair decision
    ↓
EXECUTING
```

A Worker cannot use repair as a mechanism to expand its write scope.

If additional files are required:

```text
request
   ↓
Planner / revised plan
   ↓
validated task scope
```

Repair does not modify completed history.

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

V1 human-gate persistence may simply be represented in project state:

```text
HUMAN_GATE
  reason
  requested_at
  decision
```

Human decision:

```text
APPROVE
    ↓
legal Frontier transition

REJECT
    ↓
replan / fail according to policy
```

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

```text
1. run required project-level verification
2. assess modernization objectives
3. validate acceptance criteria
```

Then:

```text
COMPLETING → COMPLETE
```

The Planner may provide an assessment, but Frontier validates completion against explicit acceptance criteria.

Project completion must not be inferred merely from the last Task succeeding.

---

# 30. Persistence

Frontier uses simple local persistence.

Do not implement:

```text
event sourcing
distributed database
message broker
workflow database
```

Recommended V1 structure:

```text
.frontier/
├── project.json
├── plan.json
└── attempts/
    ├── task-001-1.json
    ├── task-001-2.json
    └── ...
```

`project.json` should contain workflow state and essential project metadata.

`plan.json` should represent the current accepted plan.

Attempts should preserve execution/verification evidence and artifacts needed for diagnosis and resume.

Meaningful persistence boundaries include:

```text
state transition
Worker execution
verification
recovery decision
plan update
human decision
```

The persistence implementation must be behind a simple interface:

```text
ProjectStore
    load(projectId)
    save(project)
```

V1 may keep active state in memory and persist at workflow boundaries.

---

# 31. Evidence and Artifacts Model

Evidence remains lightweight.

V1 should prefer evidence attached to project/task attempts rather than implementing a generalized evidence subsystem.

Suggested model:

```text
Evidence
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

Artifacts may include:

```text
logs
build/test output
diffs
analysis reports
model summaries
```

The workspace remains authoritative for actual source changes.

---

# 32. Workspace Model

Frontier operates against a repository workspace.

The prototype assumes:

```text
one project
one workspace
one active execution context
```

Do not build workspace clusters, distributed locks, remote execution pools, or sandbox orchestration.

Workers execute within the workspace abstraction exposed by Frontier.

The workspace/code state is authoritative for actual file modifications.

---

# 33. Agent Interaction Rule

There must be no direct agent-to-agent control flow.

Correct:

```text
                  ┌──────────────┐
                  │   Frontier   │
                  └──────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
       Planner         Worker        Verifier
          │              │              │
          └──────────────┴──────────────┘
                         │
                         ▼
                  Result / Evidence
                         │
                         ▼
                      Frontier
```

Incorrect:

```text
Planner → Worker
Worker → Planner
Worker → Verifier
Verifier → Worker
```

RepositoryInspector is also invoked by Frontier, not directly by agents.

All control interactions go through Frontier.

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
Worker invocation
Verifier invocation
Completion gates
Retry decisions
Recovery decisions
Replanning orchestration
Plan history
Human gates
Project completion
Persistence
Evidence/artifact recording
```

Frontier is deliberately deterministic.

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
implement distributed scheduling
```

---

# 36. Prototype Non-Goals

The following are explicitly out of scope for Frontier V1:

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
capability marketplaces
specialized discovery-agent fleets
LLM verification for every task
iterative planner-context loops as a normal workflow
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
batched repository inspection
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
LLM verification when deterministic evidence is sufficient
sequential agent chains that add no reasoning value
```

The orchestration kernel should be cheap relative to Worker and any necessary LLM verification.

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
basic build/test result interpretation
```

These operations must remain deterministic.

Use LLMs for:

```text
repository interpretation when required
planning
semantic code changes
semantic verification where required
recovery recommendations when useful
```

Default V1 verification should be deterministic.

Semantic verification is an explicit exception, not the default.

---

# 39. Recommended Prototype Structure

Use a small modular structure similar to:

```text
frontier/
│
├── domain/
│   ├── project
│   ├── task
│   └── state
│
├── kernel/
│   ├── transition
│   ├── dag
│   ├── scope
│   └── completion
│
├── orchestration/
│   ├── task-runner
│   └── recovery
│
├── capabilities/
│   ├── repository
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
    ├── recovery
    └── orchestration
```

Do not create packages merely to anticipate future infrastructure.

The kernel should remain concrete and deterministic where possible.

The capability interfaces define only real external boundaries.

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
replanned DAG
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
directory/path overlap
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

### Replanning/history tests

Test:

```text
completed Tasks remain immutable
completed history survives plan replacement
unaffected Tasks can be preserved
new plan passes DAG validation
invalid revised plan is rejected
```

### Orchestration tests

Use Mock Worker and Mock Verifier to test:

```text
READY → EXECUTING → VERIFYING → COMPLETE
```

without invoking external LLMs.

### Project completion tests

Test:

```text
all required Tasks complete → COMPLETING
project verification failure → not COMPLETE
acceptance criteria failure → not COMPLETE
acceptance success → COMPLETE
```

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
14. Lightweight evidence/artifact model
15. Completion gate
16. Recovery decision model
17. Basic Task Runner
18. Simple ProjectStore
19. Project acceptance model
20. Unit tests
```

Then stop.

Do not implement the real Planner or Worker until the kernel is coherent and tested.

---

# 42. Second Implementation Milestone

After the kernel is tested:

```text
RepositoryInspector
Planner capability
Worker adapter
Verifier capability
```

Implement one concrete path end-to-end:

```text
Repository inspection
    ↓
Planner
    ↓
Task plan
    ↓
Worker
    ↓
actual diff / scope validation
    ↓
Verifier
    ↓
Completion gate
```

Use mocks wherever the external capability is not yet ready.

Start with deterministic verification commands before adding semantic verification.

---

# 43. Third Implementation Milestone

Demonstrate a real modernization workflow against a small Java repository.

Example:

```text
Java 8
Spring Boot 1.5.x
        ↓
Repository inspection
        ↓
Planner
        ↓
Task DAG
        ↓
Worker / OpenRewrite
        ↓
semantic fixes where required
        ↓
deterministic verification
        ↓
optional semantic verification
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
replan when required
complete
fail safely
```

without Frontier itself performing LLM reasoning.

---

# 44. Claude Code Implementation Rules

Claude Code must follow these rules.

### Rule 1 — Inspect before modifying

First inspect:

```text
repository structure
build system
existing code
tests
configuration
Git state
```

Do not assume repository layout.

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
worker pools
scheduler frameworks
capability registries
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
RepositoryInspector
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

### Rule 7 — Do not pay an LLM for deterministic work

Before introducing an LLM call, ask:

```text
Can this be established reliably with code, a repository tool,
a build command, Git, parsing, or another deterministic check?
```

If yes, use the deterministic mechanism.

### Rule 8 — Prefer one rich context over repeated context requests

Provide sufficient RepositoryContext up front.

Additional context requests must be bounded and exceptional.

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

### Workspace truth invariant

The actual workspace/Git diff is authoritative for source modifications; Worker-reported changes are evidence only.

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

### Plan validation invariant

No revised plan may execute until DAG, scope/conflict, and policy validation succeeds.

### Read-only verification invariant

Verifier and RepositoryInspector must not modify source code.

---

# 46. Definition of Done — Frontier V1 Prototype

Frontier V1 is considered prototype-complete when it can demonstrate:

```text
1. Initialize a project
2. Perform read-only repository inspection
3. Generate an execution plan
4. Validate the Task DAG
5. Validate file scopes
6. Detect unsafe scope conflicts
7. Select READY Tasks
8. Execute a Worker
9. Inspect actual workspace changes
10. Reject out-of-scope changes
11. Run deterministic verification
12. Invoke semantic verification only when required
13. Apply the completion gate
14. Retry a recoverable failure
15. Repair a Task
16. Trigger replanning
17. Preserve completed history during replanning
18. Pause for human approval
19. Persist workflow state
20. Resume from persisted state
21. Perform project-level acceptance
22. Complete the project
23. Fail safely when recovery is exhausted
```

The prototype does not need distributed execution or sophisticated scheduling to satisfy this definition.

---

# 47. Final Architectural Principle

Frontier should remain small.

The desired V1 architecture is:

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
                     │ acceptance            │
                     └───────────┬───────────┘
                                 │
                   ┌─────────────┼─────────────┐
                   ↓             ↓             ↓
              Inspector       Planner       Worker
                   │             │             │
                   │             │             │
                   └─────────────┼─────────────┘
                                 ↓
                              Verifier
                                 │
                                 ↓
                            Repository
```

The fundamental separation is:

> **Frontier decides what is legal. Agents decide how to perform the work.**

Do not compromise that boundary in the name of prototype simplicity.

At the same time:

> **Do not build production infrastructure—or multiply agent abstractions—before the workflow model has been proven.**

Frontier V1 is successful if the deterministic kernel is small, understandable, well-tested, capable of orchestrating real modernization work, and frugal with LLM calls.
