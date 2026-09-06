# Uplift Orchestrator — Claude Code Implementation Brief

## Objective

Build the **Uplift Orchestrator** for Java modernization.

Initial modernization scenario:

- Source: Java 8
- Spring Boot: 1.5.x
- Target: Java 21
- Spring Boot: 3.5.x

The Orchestrator is a **deterministic workflow controller**.

> Agents reason and execute work.  
> The Orchestrator owns workflow state, validation, gates, and transitions.

Do not turn the Orchestrator itself into an LLM agent.

---

## 1. Core Model

```text
Project
  └── Tasks
        └── Files
```

- Project = workflow container
- Task = independently executable unit of work
- File = resource touched by Tasks
- Tasks form a strict DAG
- Scheduler operates on Tasks
- Files are NOT the primary workflow unit

---

## 2. Project Workflow

Implement these project states:

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

Recovery/control paths:

```text
EXECUTING → REPLANNING → EXECUTING

EXECUTING → BLOCKED → EXECUTING

any applicable state → HUMAN_GATE

unrecoverable condition → FAILED
```

Meanings:

- `INITIALIZING` — establish project/workspace
- `DISCOVERING` — collect baseline modernization evidence
- `PLANNING` — create execution plan
- `EXECUTING` — execute Tasks
- `REPLANNING` — revise affected remaining work
- `BLOCKED` — cannot currently proceed
- `HUMAN_GATE` — human decision required
- `COMPLETING` — Tasks complete; final project acceptance pending
- `COMPLETE` — modernization accepted
- `FAILED` — terminal workflow failure

---

## 3. Task Workflow

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
                  ├── retry
                  ├── repair
                  ├── replan
                  ├── human gate
                  └── FAILED
```

Repair:

```text
VERIFYING
   ↓
REPAIRING
   ↓
EXECUTING
```

Rules:

- `FAILED` is terminal.
- Completed Tasks are normally immutable.
- A completed Task may be explicitly reopened only by policy.
- Otherwise create a superseding Task.
- `BLOCKED → READY` should happen automatically when deterministic preconditions resolve.
- Worker timeout/crash is treated as execution failure.
- Verification failure follows the same recovery policy.

---

## 4. Discovery

Discovery is a first-class phase.

Discovery is **strictly read-only**.

Use both:

```text
Deterministic tools
    +
LLM exploration/interpretration
```

Examples of deterministic discovery capabilities:

- OpenRewrite
- Maven/Gradle
- Java parsing
- dependency analysis
- static analysis
- Git/repository inspection

Baseline Discovery is complete only when the required artifacts defined by the workflow definition exist.

Do NOT define Discovery completion as merely "all tools finished".

Additional Discovery may happen later if the Planner determines existing evidence is insufficient.

---

## 5. Planner

The Planner is an LLM-based **modernization strategist**.

Planner is:

- read-only
- allowed to inspect the repository
- allowed to request additional context
- allowed to propose/create Tasks
- allowed to define Task dependencies
- allowed to define Task file scopes
- allowed to define verification strategy
- allowed to recommend Worker capability/runtime
- NOT allowed to mutate workflow state directly
- NOT allowed to override Orchestrator policy

Planner output must describe the complete execution plan:

```text
Task
  ├── objective
  ├── dependencies
  ├── required context
  ├── authorized files
  ├── capability requirements
  ├── preferred Worker
  └── verification strategy
```

Planner may propose workflow-definition changes.

Such changes require human approval.

---

## 6. Task Dependencies

Dependencies form a strict DAG.

If:

```text
Task B depends on Task A
```

then:

```text
A must reach COMPLETE
before B becomes READY
```

The Orchestrator must:

1. validate the complete remaining DAG whenever the plan changes
2. reject cycles
3. validate dependencies again before affected execution resumes

Do NOT infer dependencies.

If the Planner creates a new Task, its dependencies must be explicitly defined.

---

## 7. File Scope

A Task has an explicit authorized write scope.

Example:

```text
Task:
  authorized_write_files:
    - pom.xml
    - src/main/java/com/example/Foo.java
```

Worker:

- may READ broadly
- may WRITE only authorized files

If Worker needs to modify another file:

```text
Worker stops
    ↓
reports evidence/request
    ↓
Orchestrator routes to Planner
    ↓
Planner may revise/split/replan
```

Worker must never expand its own scope.

During repair, the same scope remains enforced.

---

## 8. Resource Conflicts

Overlapping modification scopes must serialize.

If two Tasks modify overlapping files:

```text
Task A ──┐
         ├── must not execute concurrently
Task B ──┘
```

The Orchestrator must reject an unsafe plan when overlapping modification scopes have no explicit dependency.

Do NOT invent a dependency automatically.

Planner-declared semantic dependencies are also authoritative.

---

## 9. Workers

Workers perform actual modernization work.

Possible Worker capabilities:

```text
OpenRewrite
Codex
Claude
Other deterministic or LLM capability
```

OpenRewrite should be treated as a **deterministic modernization capability**, not necessarily as a separate agent role.

Typical pattern:

```text
OpenRewrite
     ↓
deterministic migration
     ↓
LLM Worker
     ↓
semantic/application fixes
     ↓
Verifier
```

A single Task may involve multiple Worker executions.

Workers are stateless/isolated per execution.

---

## 10. Worker Contract

Worker receives:

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

Worker returns:

```text
Worker Result
  ├── outcome
  ├── changes
  ├── evidence
  ├── issues
  └── requests
        ├── context_request
        └── capability_request
```

Worker-reported changes are evidence only.

The Orchestrator must inspect the actual workspace diff and enforce scope independently.

Worker cannot declare a Task `COMPLETE`.

---

## 11. Verification

Every executable Task requires verification.

Verifier is:

- read-only
- allowed to build/test/analyze
- allowed to inspect repository state
- never allowed to modify source

Verifier receives:

```text
Task
+
verification_strategy
+
required_context
```

Verifier returns:

```text
Verification Result
  ├── outcome
  ├── checks_performed
  ├── evidence
  ├── failures
  └── advisory_classification
```

Allowed advisory classifications:

```text
IMPLEMENTATION_ISSUE
PLAN_ISSUE
DEPENDENCY_ISSUE
ENVIRONMENT_ISSUE
```

These classifications are advisory.

The Orchestrator determines the actual recovery transition.

---

## 12. Task Completion Gate

A Task may become `COMPLETE` only when all are true:

```text
Worker result exists
        AND
actual diff is within authorized scope
        AND
deterministic checks pass
        AND
Verifier evidence supports success
```

Worker success alone is never sufficient.

Core rule:

> Agents provide evidence.  
> Orchestrator owns state.

---

## 13. Failure / Recovery

Recovery is evidence-driven.

Do not automatically replan every failure.

General policy:

```text
transient/simple problem
        → retry

implementation/code problem
        → repair Worker

planning problem
        → Planner / replan

dependency problem
        → discovery / replan

unsafe or unresolved problem
        → human gate

exhausted/unrecoverable
        → FAILED
```

Workers and Verifiers may recommend recovery.

Only the Orchestrator performs the transition.

---

## 14. Replanning

Replanning is **evidence-driven, not failure-driven**.

Evidence may come from:

- Discovery
- Worker
- Verifier
- deterministic tooling
- dependency analysis
- repository conditions

When replanning begins, Planner receives:

```text
complete current project state
+
complete task state
+
existing evidence
+
triggering evidence
```

Planner may rebuild the remaining execution plan.

However:

```text
completed/history
    → preserved

unaffected Tasks
    → preserved

affected Tasks
    → revised/replaced
```

The Orchestrator determines the affected execution boundary.

After replanning:

```text
Planner creates revised plan
        ↓
Orchestrator validates DAG
        ↓
Orchestrator validates scopes/conflicts
        ↓
Orchestrator validates policy
        ↓
EXECUTING
```

---

## 15. Human Gate

Human intervention is required when:

1. workflow policy explicitly requires it, OR
2. automation cannot safely resolve the situation.

Planner, Worker, Verifier, or tooling may recommend a human gate.

Only the Orchestrator can create:

```text
HUMAN_GATE
```

Human reviews:

```text
evidence
+
proposed action
```

Human then:

```text
APPROVE
    → Orchestrator performs legal transition

REJECT
    → REPLANNING
```

Agents do not directly transition workflow state.

Task-level human intervention may remain a Task-level `BLOCKED` condition.

Project-wide human intervention uses project `HUMAN_GATE`.

---

## 16. Project Completion

When all required executable Tasks are `COMPLETE`:

```text
EXECUTING
    ↓
COMPLETING
```

In `COMPLETING`:

1. perform project-level verification if required by policy
2. Planner assesses modernization objectives
3. Orchestrator validates the assessment against acceptance criteria

Only then:

```text
COMPLETING → COMPLETE
```

---

# 17. Orchestrator Responsibilities

The Orchestrator owns:

```text
Workflow state
Task state
Transition legality
DAG validation
Dependency validation
File-scope enforcement
Resource conflict enforcement
Worker routing
Verification routing
Retry/recovery decisions
Replanning transitions
Human gates
Project completion
Persistent orchestration state
Event/reconciliation handling
Authoritative workflow policy
```

The Orchestrator does NOT:

```text
reason about code like an LLM
modify source code
perform modernization itself
allow agents to mutate state directly
infer unsafe dependencies
allow workers to expand scope
```

---

# 18. Agent Interaction Rule

There must be no direct agent-to-agent control flow.

Use:

```text
              ┌──────────────┐
              │ Orchestrator │
              └──────┬───────┘
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    Planner        Worker       Verifier
       │             │             │
       └─────────────┴─────────────┘
                     │
              Evidence / Result
                     ↓
              Orchestrator
```

Agents communicate through the Orchestrator's contracts/results.

---

# 19. Initial Implementation Scope

Do NOT implement the entire modernization system at once.

Start with the **workflow kernel**.

Implement first:

```text
1. Project state model
2. Task state model
3. Task model
4. Dependency/DAG validation
5. File-scope model
6. Transition rules
7. Worker/Verifier result contracts
8. Evidence model
9. Recovery decision model
10. Basic orchestration loop
```

Then add:

```text
Discovery
Planner
Workers
Verifier
Human gates
Persistence
```

Do not prematurely implement sophisticated scheduling, distributed execution, load balancing, event sourcing, or agent optimization.

---

# 20. Implementation Principle

Prefer:

```text
small deterministic core
+
well-defined contracts
+
replaceable agents/capabilities
+
explicit state transitions
+
auditable evidence
```

Avoid:

```text
implicit state
agent-controlled transitions
hidden dependencies
automatic scope expansion
large monolithic agent
hardcoded modernization phases
```

---

# 21. First Claude Code Task

Before implementing agents or modernization logic:

### Build the workflow kernel.

Claude Code should:

1. inspect the repository
2. identify the existing project structure
3. propose the minimal implementation structure
4. implement Project/Task state models
5. implement legal state transitions
6. implement DAG validation
7. implement Task file-scope/conflict validation
8. implement the basic Task completion gate
9. add unit tests for the state machine and validation rules
10. stop and report what was implemented

Do not proceed into Planner/Worker/Verifier implementation until the workflow kernel is coherent and tested.

When making architectural decisions not explicitly defined above, prefer the **simplest deterministic design** and document the decision rather than silently introducing additional concepts.