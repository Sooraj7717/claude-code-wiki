# Uplift Orchestrator V6 — Stage 3 Implementation Specification

## Milestone

**M3 — Production Control Plane & Full UI**

Stage 3 is the final V6 implementation milestone. It builds on M1 and M2 and turns the workflow engine into a secure, observable, auditable operator control plane for Java/Spring uplift workflows.

## Goal

A durable Java/Spring uplift orchestration platform can be operated through a complete UI/API control plane with strong security boundaries, auditability, reconciliation, verification, and human oversight.

The target architecture remains:

```text
UI
 ↓
Spring Boot Orchestrator API
 ↓
Workflow Engine
 ↓
AgentRunner / Claude Code
 ↓
Java/Spring target workspace
```

The UI and API are control surfaces over the Orchestrator. They are not alternative workflow engines.

---

# 1. Prerequisites

M3 assumes M1 and M2 are complete and passing.

M2 must already provide:

- multi-task DAG orchestration
- deterministic READY-task selection
- Attempts
- recovery classification and bounded budgets
- failure signatures
- Plan versioning
- Human Gates
- resume/reconciliation
- project verification
- REST API
- SSE event stream
- functional workflow UI

M3 must harden and expose those capabilities rather than redesign them.

---

# 2. Scope

M3 consists of six implementation areas:

1. Workflow-engine hardening
2. Security and enforcement hardening
3. Complete Orchestrator API
4. Full operator UI
5. Observability and audit
6. End-to-end hardening and acceptance

---

# 3. Workflow Engine Hardening

## 3.1 State persistence

The Orchestrator remains the sole owner of workflow state.

Use:

```text
.uplift/runs/<run-id>/
    state.json
    events.jsonl
    artifacts/
```

`state.json` is the current snapshot.

`events.jsonl` is append-only history.

Agents must not mutate either.

Persistence must provide:

- atomic state writes
- append-only event writes
- state versioning
- corruption detection
- deterministic serialization where practical
- safe startup recovery

Full event sourcing is not required for V6.

## 3.2 State/event consistency

Every state transition must have a durable event.

A transition must not become visible as successful state without the corresponding event being persisted.

If persistence fails, the transition is not accepted.

Corrections are represented as new events; history is never rewritten.

## 3.3 Concurrency

V6 remains sequential for Task execution, but API clients can race.

For a given Run, workflow commands must be serialized or protected by optimistic concurrency.

Examples:

```text
POST /pause
POST /resume
POST /gates/{id}/decision
POST /replan
```

must not produce invalid state transitions through races.

The workflow engine, not the client, decides whether a command is valid in the current state.

## 3.4 Resume/reconciliation

On restart:

1. Load state snapshot.
2. Read event history.
3. Inspect workspace/Git state.
4. Identify active Attempt and Human Gates.
5. Reconcile persisted state against observable workspace state.
6. Continue only from a safe state.
7. Never blindly rerun an interrupted Attempt.

Unexpected workspace mutation or baseline mismatch must result in a durable Human Gate or equivalent safe stop.

---

# 4. Security and Enforcement

Prompt instructions are guidance, not a security boundary.

Enforcement layers remain:

```text
Platform/security sandbox
    ↓
Claude Code permissions
    ↓
PreToolUse/runtime hooks
    ↓
Orchestrator policy
    ↓
Task scope and protected contracts
    ↓
Agent prompt
```

## 4.1 Agent capabilities

### Planner

```text
Read
Grep
Glob
```

No write access.

### Implementer

```text
Read
Grep
Glob
Edit
Write
Bash
```

Bash is controlled through Claude Code permissions/sandboxing, destructive-command hooks, task-scoped policy, and mandatory post-execution inspection.

### Verifier

```text
Read
Grep
Glob
Bash
```

No Edit or Write.

No agent may spawn another agent.

## 4.2 Destructive command enforcement

Continue blocking dangerous Git operations, including:

- `git reset --hard`
- `git clean -f`
- `git checkout --`
- `git restore --source`
- force push
- interactive rebase
- `git filter-repo`
- branch deletion

V6 does not enable automatic commits, pushes, or PR creation.

## 4.3 Workflow-state protection

Agents must not modify:

```text
.uplift/runs/**
```

workflow state.

The system must detect attempted state tampering.

## 4.4 Security events

First-class audit events include:

```text
TOOL_BLOCKED
UNSAFE_COMMAND_BLOCKED
PERMISSION_DENIED
SCOPE_VIOLATION
CONTRACT_VIOLATION
WORKFLOW_STATE_TAMPERING
AGENT_SPAWN_BLOCKED
HUMAN_GATE_OPENED
```

Security failures must not be silently converted into ordinary implementation failures.

---

# 5. API Contract

Base path:

```text
/api/v1
```

The API is command-oriented. Do not expose generic state mutation endpoints such as arbitrary `PUT /tasks/{id}`.

## 5.1 Runs

```text
GET  /runs
POST /runs
GET  /runs/{runId}

POST /runs/{runId}/start
POST /runs/{runId}/pause
POST /runs/{runId}/resume
```

## 5.2 Plans

```text
GET /runs/{runId}/plans
GET /runs/{runId}/plans/{planVersion}
```

## 5.3 Tasks

```text
GET /runs/{runId}/tasks
GET /runs/{runId}/tasks/{taskId}
```

## 5.4 Attempts

```text
GET /runs/{runId}/attempts
GET /runs/{runId}/attempts/{attemptId}
GET /runs/{runId}/attempts/{attemptId}/diff
```

## 5.5 Recovery

```text
GET /runs/{runId}/recovery
GET /runs/{runId}/tasks/{taskId}/recovery
```

## 5.6 Human Gates

```text
GET  /runs/{runId}/gates
GET  /runs/{runId}/gates/{gateId}

POST /runs/{runId}/gates/{gateId}/decision
```

The API must validate authorization and workflow-state validity before applying a decision.

## 5.7 Verification

```text
GET /runs/{runId}/verification
```

## 5.8 Diff

```text
GET /runs/{runId}/diff
GET /runs/{runId}/attempts/{attemptId}/diff
```

## 5.9 Artifacts

```text
GET /runs/{runId}/artifacts
GET /runs/{runId}/artifacts/{artifactId}
```

## 5.10 Events

```text
GET /runs/{runId}/events
GET /runs/{runId}/events/stream
```

SSE remains the preferred live event mechanism.

## 5.11 API authorization

Where authentication is enabled, permissions should distinguish at least:

```text
VIEW_RUN
START_RUN
PAUSE_RUN
RESUME_RUN
DECIDE_GATE
REQUEST_REPLAN
VIEW_ARTIFACT
VIEW_DIFF
```

API authorization answers:

> Who may request this operation?

Workflow validation answers:

> Is this operation legal in the current Run state?

Both checks are required.

## 5.12 Error semantics

API errors must be structured and stable.

At minimum distinguish:

```text
VALIDATION_ERROR
NOT_FOUND
UNAUTHORIZED
FORBIDDEN
INVALID_STATE_TRANSITION
CONFLICT
HUMAN_GATE_REQUIRED
WORKFLOW_FAILURE
INTERNAL_ERROR
```

Do not expose raw stack traces or agent internals as the API contract.

---

# 6. Full UI Architecture

The UI is an operator/control plane.

It must never:

- read `.uplift/runs` directly
- invoke Claude Code directly
- mutate workflow state directly
- infer workflow authority from agent output

All data and commands go through the Orchestrator API.

## 6.1 Information architecture

```text
Dashboard
Runs
Run Workspace
 ├── Overview
 ├── Plan / DAG
 ├── Tasks
 ├── Attempts
 ├── Verification
 ├── Diff
 ├── Contracts
 ├── Human Gates
 ├── Events / Audit
 └── Artifacts
```

## 6.2 Dashboard

Show:

- active Runs
- executing Runs
- Human Gates
- blocked Runs
- failed Runs
- completed Runs
- recent security/recovery events

The primary question is:

> What needs operator attention?

## 6.3 Run Workspace

The Run Workspace is the central operator view.

Display:

- Java/Spring uplift objective
- source and target versions
- current Plan version
- Run state
- progress
- current Task
- active Attempt
- recovery state
- Human Gates
- verification summary

## 6.4 Plan/DAG

Display:

- Tasks
- dependencies
- status
- Attempt count
- recovery count
- verification status

Task nodes must be navigable to Task detail.

## 6.5 Task and Attempt views

Task detail should show:

- objective
- scope
- dependencies
- acceptance criteria
- attempts
- current state
- recovery history

Attempt detail should show:

- baseline
- workspace delta
- scope result
- protected contract result
- deterministic checks
- Verifier result
- failure signature
- recovery classification
- artifacts

## 6.6 Contract viewer

For Java/Spring uplifts, show protected contracts such as:

- public Java methods
- interfaces/types
- REST endpoints
- request/response schemas
- events/messages
- repository-specific contracts

Display status:

```text
UNCHANGED
AUTHORIZED CHANGE
UNAUTHORIZED CHANGE
```

with evidence.

## 6.7 Verification center

Separate:

```text
Deterministic checks
Semantic Verifier
Task acceptance
Project acceptance
```

The UI must not equate agent claims with verification evidence.

## 6.8 Human Gate center

Provide a queue of unresolved gates with:

- severity
- reason
- Run/Task/Attempt
- required decision
- supporting evidence
- available decisions

Human decisions are API commands and become durable events.

## 6.9 Event/audit explorer

Provide:

- chronological event stream
- filtering
- security events
- recovery events
- verification events
- Human Gate events
- Agent lifecycle events

Every event should retain stable identifiers where applicable:

```text
run_id
plan_version
task_id
attempt_id
invocation_id
gate_id
```

## 6.10 Artifact browser

Allow operators to inspect durable artifacts without directly browsing the `.uplift` filesystem.

---

# 7. Observability

M3 introduces operational telemetry without changing workflow semantics.

Track:

- Run duration
- Task duration
- Attempt duration
- Agent invocation duration
- Verification duration
- recovery counts
- Human Gate wait time
- failure categories
- success/failure rates

Useful metrics include:

```text
average_task_duration
average_attempts_per_task
repair_rate
replan_rate
human_gate_rate
verification_failure_rate
```

Structured logs should include stable workflow identifiers.

Do not log credentials, secrets, or unnecessary sensitive tool output.

---

# 8. Java/Spring Uplift Quality

The implementation framework must remain Java/Spring-specific.

The system should support repository-defined checks around:

- Java compatibility
- Spring Boot compatibility
- javax → jakarta migration
- Maven/Gradle builds
- unit tests
- integration tests
- REST contracts
- configuration
- persistence/JPA/Hibernate
- Spring Security
- project acceptance criteria

The Orchestrator provides enforcement and evidence collection; it does not hard-code every possible migration rule.

TypeScript, Node.js, Python, Go, and Rust are not uplift-specification technologies.

---

# 9. Testing

## Workflow tests

- valid transitions
- invalid transitions
- persistence failures
- concurrent commands
- state/event consistency
- resume/reconciliation

## Security tests

- blocked dangerous commands
- scope violations
- contract violations
- workflow-state tampering
- unauthorized API operations
- unauthorized Human Gate decisions
- agent-spawn attempts

## Recovery tests

- retry budgets
- repair budgets
- replan budgets
- context-request budgets
- repeated failure signatures
- Human Gate escalation

## API tests

- authentication
- authorization
- validation
- invalid state commands
- concurrency/conflict behavior
- stable error semantics
- SSE

## UI tests

- Dashboard
- Run Workspace
- DAG
- Task/Attempt explorer
- Recovery
- Verification
- Diff
- Contracts
- Human Gates
- Events
- Artifacts
- SSE reconnect/error behavior

---

# 10. Real Java/Spring Acceptance Test

Use a realistic Java/Spring service rather than only a toy fixture.

Exercise representative migration concerns:

```text
Java 8 → Java 21
Spring Boot 2.x → Spring Boot 3.x
javax → jakarta
Spring Security
JPA/Hibernate
REST APIs
configuration
tests
```

Exercise both successful and adverse paths:

```text
successful Task
repairable failure
repeated equivalent failure
scope violation
contract violation
Human Gate
replan
process interruption
resume
project verification
```

The complete lifecycle must be understandable from the UI.

---

# 11. Non-Goals

M3 does not implement:

- parallel Task execution
- Git worktree orchestration
- Agent Teams
- distributed workers
- cloud execution
- Kubernetes
- multi-repository orchestration
- automatic Git commits
- automatic pushes
- automatic PR creation
- autonomous workflow topology
- agent-to-agent communication
- full event sourcing

These remain V7+ candidates.

---

# 12. Implementation Order

### Phase A — Workflow hardening

- persistence
- state/event consistency
- concurrency
- reconciliation

### Phase B — Security

- role/tool permissions
- state protection
- security events
- API authorization

### Phase C — API completion

- versioning
- command model
- artifacts
- diff
- verification
- operational endpoints

### Phase D — UI control plane

- dashboard
- Run Workspace
- DAG
- Tasks/Attempts
- Verification
- Diff/Contracts
- Human Gates
- Artifacts/Events

### Phase E — Observability

- structured logs
- metrics
- audit views

### Phase F — Hardening and acceptance

- workflow
- security
- recovery/resume
- API
- UI
- realistic Java/Spring acceptance

---

# 13. Definition of Done

M3 is complete when:

- workflow persistence is robust
- state/event consistency is protected
- concurrent API commands cannot corrupt Run state
- resume/reconciliation is hardened
- agent permissions are enforced
- dangerous operations are blocked
- workflow-state tampering is detected
- security events are auditable
- API authorization is implemented where applicable
- API cannot bypass workflow transitions
- API error semantics are stable
- complete resource APIs work
- SSE works reliably
- Dashboard works
- Run Workspace works
- DAG visualization works
- Task/Attempt history works
- Contract viewer works
- Verification center works
- Human Gate center works
- Artifact browser works
- Event/audit explorer works
- structured logging works
- operational metrics work
- Java/Spring acceptance workflow works
- security tests pass
- recovery/resume tests pass
- API/UI tests pass
- realistic Java/Spring acceptance passes
- no V7 functionality has leaked into M3

---

# 14. V6 Completion Boundary

After M3:

```text
V5
Frozen workflow architecture
        ↓
V6 M1
First runnable vertical slice
        ↓
V6 M2
Multi-task orchestration + recovery + resume
        ↓
V6 M3
Production control plane + full UI
        ↓
V6 COMPLETE
        ↓
V7+
Parallelism / worktrees / distributed execution /
multi-repository / Git automation / Agent Teams
```

V6 is complete when the Orchestrator is safe and understandable to operate for a real Java/Spring uplift. New execution topology or autonomous integration capabilities belong to later milestones.
