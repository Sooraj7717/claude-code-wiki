# Uplift Orchestrator V6 — Stage 2 Implementation Specification
## Milestone M2: Multi-Task Orchestration, Recovery & Resume

**Status:** Implementation-ready milestone specification  
**Parent milestone:** V6 — Workflow Engine + Orchestrator API + UI Architecture  
**Prerequisite:** V6 Stage 1 / M1 complete and passing its Definition of Done  
**Target domain:** Java/Spring uplift only  
**Implementation target:** Java + Spring Boot workflow backend; web UI as a separate frontend layer  
**Primary objective:** Extend the proven M1 vertical slice into a real multi-task Java/Spring uplift orchestrator with dependency management, bounded recovery, durable Human Gates, and safe resume/reconciliation.

---

## 1. M2 Goal

M2 must prove that one complete Java/Spring uplift can be represented as a dependency graph and executed safely through multiple Claude Code Attempts, while handling failure and interruption without losing workflow history.

The target lifecycle is:

```text
Create Run
  -> Discover / Plan
  -> Plan Gate
  -> multiple Tasks / DAG
  -> deterministic READY selection
  -> Attempt
  -> Implement
  -> actual workspace delta
  -> scope + contract checks
  -> independent verification
  -> Task Completion
  -> next READY Task
  -> project verification
  -> project completion
```

Failure/recovery must support:

```text
failure
  -> deterministic classification
  -> bounded RETRY / REPAIR / REPLAN / CONTEXT_REQUEST
  -> HUMAN_GATE / BLOCK / FAIL where required
  -> new Attempt or new Plan
  -> continue safely
```

Process interruption must support:

```text
restart process
  -> load state
  -> read event history
  -> inspect workspace
  -> reconcile active Attempt/Gate
  -> continue only from a safe state
```

M2 is successful only if this behavior is demonstrated against a realistic Java/Spring uplift repository.

---

## 2. Scope of M2

### 2.1 Workflow Engine

Add:

- multiple Tasks per Plan
- dependency DAG
- deterministic READY-task selection
- full Task lifecycle
- multiple Attempts per Task
- recovery classification
- bounded recovery budgets
- normalized failure signatures
- RETRY
- REPAIR
- REPLAN
- CONTEXT_REQUEST
- BLOCK
- HUMAN_GATE
- FAIL
- immutable Plan versions
- task/attempt/recovery history
- project-level verification
- project acceptance
- safe resume/reconciliation
- interrupted Attempt handling
- expanded event history

### 2.2 Claude Code Integration

Extend M1 to support:

- repeated Implementer invocations
- repeated Verifier invocations
- Planner re-invocation for REPLAN
- bounded Context Request handoffs
- recovery-specific handoffs
- invocation lineage
- previous Attempt evidence references

Agents remain workers/evidence producers.

Agents do not:

- choose recovery
- advance workflow state
- mutate Task/Attempt/Plan/Run state
- spawn other agents

### 2.3 Spring Boot API

Expand the M1 API to expose:

```text
GET  /api/v1/runs/{runId}/tasks
GET  /api/v1/runs/{runId}/tasks/{taskId}

GET  /api/v1/runs/{runId}/attempts
GET  /api/v1/runs/{runId}/attempts/{attemptId}

GET  /api/v1/runs/{runId}/plans
GET  /api/v1/runs/{runId}/plans/{planVersion}

GET  /api/v1/runs/{runId}/recovery
GET  /api/v1/runs/{runId}/tasks/{taskId}/recovery

POST /api/v1/runs/{runId}/pause
POST /api/v1/runs/{runId}/resume

GET  /api/v1/runs/{runId}/events
GET  /api/v1/runs/{runId}/events/stream
```

Existing M1 endpoints remain valid unless an explicit backward-compatible evolution is required.

API controllers must remain thin:

```text
Controller
  -> Application Service
  -> Workflow Engine
  -> AgentRunner / Persistence / Workspace services
```

Controllers must never independently decide or mutate workflow state.

---

## 3. Java/Spring Uplift Domain

The workflow is specifically for Java/Spring applications.

Typical M2 uplift task decomposition may include:

```text
T001 Java toolchain
T002 Jakarta migration
T003 Spring Security
T004 JPA/Hibernate
T005 Integration tests
T006 Final acceptance
```

Possible concerns include:

- Java 8 -> Java 21
- Spring Boot 2.x -> 3.x
- Spring Framework 6
- `javax.*` -> `jakarta.*`
- Spring Security
- Spring MVC/WebFlux
- JPA/Hibernate
- Maven or Gradle
- wrapper configuration
- configuration properties
- REST APIs
- Java public APIs
- DTOs
- persistence contracts

Do not introduce TypeScript, Node.js, Python, Go, Rust, or other-language migration specifications into the uplift engine.

The frontend is a separate application layer and does not redefine the Java/Spring uplift domain.

---

## 4. Locked Architectural Rules

### 4.1 Orchestrator authority

The Orchestrator owns:

- Run status
- Plan status
- Task status
- Attempt status
- Human Gate status
- workflow transitions
- recovery decisions
- completion decisions
- persistence

Agents return evidence/results only.

### 4.2 Workspace authority

Actual repository state is authoritative.

AgentResult claims must never replace workspace inspection.

### 4.3 Fresh context

Every meaningful Planner, Implementer and Verifier invocation receives a fresh context.

### 4.4 Verifier independence

Verifier:

- gets fresh context
- reads resulting workspace
- may run deterministic checks
- cannot edit/write repository files
- cannot repair its own findings

### 4.5 Controlled Bash

Implementer may use Bash subject to:

- Claude Code permissions
- safety hooks
- task policy
- post-execution inspection

### 4.6 New-run dirty workspace

For a NEW run:

```text
clean -> continue
dirty -> HUMAN_GATE
```

Do not automatically stash/reset/clean/discard.

Resume of an active run is different: reconcile against the Attempt baseline.

### 4.7 Scope

Unexpected actual changes outside authorized Task scope cause `SCOPE_VIOLATION` and normally `HUMAN_GATE`.

### 4.8 Contract integrity

Protected contracts are defined by the accepted Plan.

Unexpected changes cause `CONTRACT_VIOLATION` and normally `HUMAN_GATE`.

### 4.9 Git

Do not automatically commit, push, reset, clean, rebase, or discard changes.

### 4.10 No recursive orchestration

Agents cannot spawn agents.

---

## 5. Multi-Task Plan Model

A Plan contains a directed acyclic graph.

Example:

```text
             ┌── T002 ──┐
T001 ────────┤           ├── T005 ──► T006
             └── T003 ──┘
                    │
                    ▼
                  T004
```

The Plan Gate must validate:

1. unique Task IDs
2. valid dependency references
3. no self-dependencies
4. DAG acyclicity
5. bounded scopes
6. intentional overlap declarations
7. dependency ordering for overlap where required
8. verification requirements
9. recovery budgets
10. acceptance criteria
11. protected contracts
12. permitted contract changes

Plans are immutable.

Example:

```text
PLAN-001  ACCEPTED
PLAN-002  ACCEPTED
```

When a new plan supersedes an old one:

```text
PLAN-001  SUPERSEDED
PLAN-002  ACCEPTED
```

Never mutate historical Plan content.

---

## 6. Task Readiness

A Task is READY only when:

- it is authorized by the accepted Plan
- all required dependencies are COMPLETE
- it is not already COMPLETE
- it is not blocked by an active Human Gate
- no incompatible active Attempt exists

READY selection must be deterministic.

Recommended rule:

1. dependency readiness
2. explicit priority descending, if supported
3. stable Task ID ascending as tie-breaker

The same state must produce the same selected Task.

Agents never select the next Task.

---

## 7. Attempt Model

Every Implementer invocation belongs to exactly one Attempt.

Attempt lifecycle:

```text
CREATED
  -> BASELINED
  -> HANDOFF_READY
  -> EXECUTING
  -> EXECUTION_RETURNED
  -> DELTA_CAPTURED
  -> SCOPE_CHECKED
  -> VERIFYING
  -> VERIFIED
  -> COMPLETED
```

Failure/recovery branches may result in:

```text
FAILED
HUMAN_GATE
BLOCKED
```

Each Attempt records at minimum:

- attempt ID
- run ID
- plan version
- task ID
- invocation ID
- role
- status
- timestamps
- baseline
- workspace delta
- scope result
- contract result
- deterministic checks
- verifier result
- recovery disposition
- failure signature, if applicable

Failed Attempts remain immutable history.

---

## 8. Recovery Engine

Recovery is Orchestrator-controlled.

The agent may report evidence. It cannot choose the recovery path.

Minimum classification table:

| Evidence / Failure | Default Classification |
|---|---|
| transient tool failure | RETRY |
| invocation timeout | RETRY |
| compilation failure | REPAIR |
| test failure | REPAIR |
| implementation defect | REPAIR |
| missing bounded repository fact | CONTEXT_REQUEST |
| inadequate task scope | REPLAN |
| inadequate overall plan | REPLAN |
| ambiguous requirement | HUMAN_GATE |
| unauthorized scope change | HUMAN_GATE |
| unauthorized contract change | HUMAN_GATE |
| dangerous operation | HUMAN_GATE |
| repeated equivalent failure | FAIL or HUMAN_GATE |
| verifier disagreement | HUMAN_GATE |
| unrecoverable failure | FAIL |

The classifier must be deterministic and evidence-based.

---

## 9. Recovery Budgets

Recovery is bounded.

Example defaults:

```yaml
recovery:
  retry: 1
  repair: 2
  replan: 1
  context_request: 1
```

Budgets are per Run/Task according to the Plan model.

When a budget is exhausted, automatic recovery must stop.

Do not allow unbounded loops.

Example:

```text
REPAIR #1
  -> REPAIR #2
  -> budget exhausted
  -> HUMAN_GATE or FAIL
```

The exact default threshold may be configurable, but the invariant is bounded automatic recovery.

---

## 10. Failure Signatures

Equivalent failures must be normalized into comparable signatures.

Example:

```text
Attempt 1:
Cannot resolve symbol CustomerRepository

Attempt 2:
error: cannot resolve symbol CustomerRepository

Attempt 3:
CustomerRepository symbol cannot be resolved
```

These should be recognized as the same or equivalent failure when normalization supports it.

A failure signature should capture enough normalized information to distinguish materially different failures while grouping superficial variations.

At minimum consider:

- failure category
- tool/check
- normalized message
- relevant file/path
- relevant symbol/error code where available

Do not rely solely on raw full stdout.

When equivalent failure count reaches the configured threshold, automatic recovery stops.

---

## 11. RETRY

Use RETRY for transient execution failures.

A RETRY creates a new Attempt.

The Orchestrator must preserve:

```text
Attempt-001 FAILED
Attempt-002 RETRY
```

Retry must not rewrite Attempt-001.

If retry budget is exhausted, stop automatic retry.

---

## 12. REPAIR

Use REPAIR when the Plan remains valid but implementation is defective.

Recommended M2 behavior:

```text
failed Attempt
   -> preserve resulting workspace
   -> create new Attempt
   -> bounded repair handoff
   -> Implementer
```

The repair handoff should include:

- original task objective
- previous Attempt evidence
- failure evidence
- relevant verification output
- current workspace expectations
- allowed scope
- required checks

Do not silently discard previous changes.

If workspace state cannot be reconciled safely, use a Human Gate rather than guessing.

---

## 13. REPLAN

Use REPLAN when the accepted Plan is inadequate.

Flow:

```text
failure / insufficiency
   -> REPLAN decision
   -> Planner
   -> PLAN-002
   -> Plan Gate
   -> new accepted plan
   -> continue
```

New Plan must pass Plan Gate before new work executes.

Old Plan remains immutable.

The Orchestrator determines which existing Tasks remain valid, are superseded, or require new Attempts under the new Plan.

Do not silently rewrite completed historical Tasks.

---

## 14. CONTEXT_REQUEST

Context Requests must be bounded.

Good:

```text
Need definition of CustomerRepository
and the datasource configuration property used by it.
```

Bad:

```text
Need more context.
```

The Orchestrator should provide only the requested bounded information/artifact slice.

A Context Request results in a new bounded invocation.

Do not hydrate entire historical conversations or entire artifacts unnecessarily.

---

## 15. BLOCK

BLOCK is appropriate when execution cannot proceed now but does not necessarily require a human policy decision.

Examples:

- external prerequisite unavailable
- required repository artifact temporarily unavailable
- dependent Task not ready
- environment prerequisite not satisfied

BLOCK must be durable and visible.

The Run must not silently continue past a blocked Task.

---

## 16. HUMAN_GATE

Human Gates are durable workflow objects.

M2 must support at least:

- dirty new workspace
- unauthorized scope
- unauthorized contract change
- ambiguous requirement
- verifier disagreement
- unsafe operation
- unreconcilable interrupted Attempt

Gate fields:

```text
gate_id
run_id
task_id, if applicable
attempt_id, if applicable
type
reason
status
opened_at
evidence/artifact references
available decisions
decision
decided_at
```

A gate decision is an immutable event.

Do not directly edit state files from the UI.

---

## 17. Resume / Reconciliation

M2 must implement actual resume behavior.

On process startup or explicit resume:

```text
LOAD state.json
  -> READ events.jsonl
  -> INSPECT Git/workspace
  -> IDENTIFY active Attempt/Gate
  -> RECONCILE
  -> persist reconciliation event
  -> continue only from safe state
```

The system must not blindly rerun an interrupted Attempt.

Examples:

### Crash before execution

Safe to create/continue an Attempt according to persisted invocation state.

### Crash after workspace changes

Inspect actual workspace and compare against baseline.

### Crash during verification

Do not assume verification passed.

### Crash while Human Gate is open

Restore the same durable gate.

### State snapshot disagreement with event history

Use event history to reconstruct where possible. Ambiguity requires HUMAN_GATE.

### Unexpected workspace mutation

Require reconciliation/HUMAN_GATE rather than guessing.

---

## 18. Resume vs Restart

Explicitly distinguish:

### Resume

Continue an existing Run after process interruption.

### Restart Attempt

Create a new Attempt for the same Task.

### Restart Run

Create a new Run identity.

These must be different API/application operations and different audit events.

---

## 19. Project Verification

After all required Tasks are COMPLETE:

```text
PROJECT VERIFICATION
  -> full build
  -> full tests
  -> protected contract integrity
  -> project acceptance criteria
  -> independent final Verifier
  -> PROJECT ACCEPTANCE
```

For Java/Spring repositories, use the project's Maven or Gradle build system.

Examples:

```text
./mvnw test
./mvnw verify

./gradlew test
./gradlew check
```

Do not hard-code both systems; discover and use the repository's configured build tool.

Project verification failure is classified through the recovery system.

---

## 20. Claude Code Recovery Handoffs

Recovery handoffs must be explicit.

### Repair handoff

Contains:

- Task
- Attempt
- failure evidence
- previous result
- workspace delta
- allowed scope
- required checks

### Replan handoff

Contains:

- current Plan
- completed Task history
- failed Task evidence
- relevant discovery artifacts
- reason Plan is inadequate
- bounded repository evidence

### Context handoff

Contains only the requested context slice.

Agents are never told to choose the recovery strategy.

---

## 21. API Contract

M2 API additions:

```text
GET  /api/v1/runs/{runId}/plans
GET  /api/v1/runs/{runId}/plans/{planVersion}

GET  /api/v1/runs/{runId}/tasks
GET  /api/v1/runs/{runId}/tasks/{taskId}

GET  /api/v1/runs/{runId}/attempts
GET  /api/v1/runs/{runId}/attempts/{attemptId}

GET  /api/v1/runs/{runId}/recovery
GET  /api/v1/runs/{runId}/tasks/{taskId}/recovery

POST /api/v1/runs/{runId}/pause
POST /api/v1/runs/{runId}/resume

GET  /api/v1/runs/{runId}/events
GET  /api/v1/runs/{runId}/events/stream
```

The API must not expose arbitrary mutation endpoints such as:

```text
POST /tasks/{id}/complete
POST /attempts/{id}/success
POST /runs/{id}/setStatus
```

Workflow transitions remain controlled by the engine.

---

## 22. SSE Event Stream

M2 introduces Server-Sent Events.

Example:

```text
GET /api/v1/runs/{runId}/events/stream
```

Events should correspond to durable Orchestrator events.

Examples:

```text
TASK_READY
ATTEMPT_CREATED
BASELINE_CAPTURED
IMPLEMENTER_STARTED
IMPLEMENTER_RETURNED
DELTA_CAPTURED
VERIFICATION_STARTED
VERIFICATION_FAILED
RECOVERY_CLASSIFIED
REPAIR_STARTED
REPLAN_STARTED
PLAN_SUPERSEDED
PLAN_ACCEPTED
HUMAN_GATE_OPENED
HUMAN_GATE_DECIDED
TASK_COMPLETED
PROJECT_VERIFICATION_STARTED
PROJECT_COMPLETED
```

The UI consumes the stream but does not become its source of truth.

---

## 23. UI M2

Extend M1 UI into a real workflow console.

### Run Overview

Show:

- objective
- Java/Spring target versions
- current Plan
- overall progress
- current Task
- current Attempt
- Human Gates
- recent events

### Plan/DAG

Interactive graph showing:

- Task
- status
- dependencies
- priority
- attempts
- scope indicator

### Task View

Show:

- objective
- dependencies
- scope
- protected contracts
- attempts
- recovery history
- verification

### Attempt View

Show:

- baseline
- workspace delta
- scope
- contract result
- deterministic checks
- Verifier result
- recovery classification
- failure signature

### Recovery View

Show the complete Task history:

```text
Attempt #1 -> FAILED -> REPAIR
Attempt #2 -> FAILED -> REPLAN
PLAN-002
Attempt #3 -> VERIFYING
```

### Human Gate View

Show:

- reason
- evidence
- affected Task/Attempt
- diff/artifacts
- available decisions
- decision history

### Event Timeline

Render the durable event stream.

### Live Updates

Use SSE to update active Run views without requiring full-page refresh.

---

## 24. M2 Testing Strategy

### DAG tests

Test:

- valid graph
- cycles
- self-dependencies
- missing dependencies
- deterministic selection
- intentional overlap
- invalid overlap
- dependency ordering

### Recovery tests

Test every supported recovery category.

### Budget tests

Verify recovery stops after configured limits.

### Failure signature tests

Verify equivalent failures group correctly and distinct failures do not.

### Attempt tests

Verify:

- immutable history
- new Attempt identity
- baseline capture
- delta capture
- recovery lineage

### Replan tests

Verify:

- old Plan remains immutable
- new Plan receives new version
- Plan Gate runs again
- execution cannot continue before new Plan acceptance

### Resume tests

Simulate interruption:

- before Implementer
- during Implementer
- after Implementer
- before Verifier
- during Verifier
- after Verifier
- while Human Gate is open
- during project verification

Verify safe reconciliation.

### API tests

Verify:

- invalid transitions are rejected
- workflow authority remains in engine
- pause/resume work correctly
- SSE reflects durable events
- no arbitrary status mutation endpoint exists

### UI tests

Verify:

- DAG rendering
- Attempt history
- recovery history
- Human Gate actions
- event updates
- API error states

---

## 25. M2 Real Acceptance Test

Use a realistic Java/Spring uplift with approximately 5–8 Tasks.

Example:

```text
T001 Java toolchain
     |
     +--> T002 Jakarta migration
     |        |
     |        +--> T004 JPA/Hibernate
     |
     +--> T003 Spring Security
              |
              +--> T005 integration tests
                         |
                         v
                    T006 final acceptance
```

The acceptance test must deliberately exercise:

1. successful Task execution
2. dependency ordering
3. a repairable compilation/test failure
4. a repeated equivalent failure
5. a Human Gate
6. successful recovery
7. Plan reversion/replanning through a new Plan version
8. process interruption
9. safe resume
10. final project verification

The final successful path must preserve all historical Attempts, Plans, Events and Gates.

---

## 26. M2 Non-Goals

Do NOT implement:

- parallel Task execution
- Git worktrees
- Agent Teams
- distributed workers
- multi-repository execution
- automatic commits
- automatic pushes
- automatic PR creation
- cloud worker infrastructure
- Kubernetes
- enterprise identity/SSO
- full production UI polish
- complete event-sourcing architecture
- universal Java AST compatibility engine
- arbitrary user-defined workflow graphs beyond the V6 Plan model

These remain future work/backlog.

---

## 27. Implementation Order

Claude Code should implement M2 in this order.

### Phase A — Multi-task domain

1. Task collection
2. dependency graph
3. DAG validation
4. deterministic READY selection
5. Plan version support

### Phase B — Attempt history

6. multiple Attempts
7. Attempt lineage
8. immutable Attempt history
9. recovery disposition

### Phase C — Recovery engine

10. failure classification
11. failure signatures
12. budgets
13. RETRY
14. REPAIR
15. CONTEXT_REQUEST
16. REPLAN
17. BLOCK
18. HUMAN_GATE
19. FAIL

### Phase D — Resume

20. startup reconciliation
21. active Attempt reconciliation
22. Human Gate restoration
23. interrupted execution handling
24. safe continuation

### Phase E — Project completion

25. project verification
26. final independent Verifier
27. project acceptance

### Phase F — API

28. plan/task/attempt APIs
29. recovery APIs
30. pause/resume
31. event APIs
32. SSE

### Phase G — UI

33. DAG view
34. Task view
35. Attempt view
36. Recovery view
37. Human Gate view
38. event timeline
39. SSE integration

### Phase H — Hardening

40. unit tests
41. integration tests
42. recovery tests
43. resume tests
44. API tests
45. UI tests
46. real Java/Spring acceptance test

Do not begin M3 functionality until all M2 acceptance criteria pass.

---

## 28. M2 Definition of Done

M2 is complete only when:

- [ ] Multiple Tasks can exist in one Plan
- [ ] DAG dependencies are validated
- [ ] READY selection is deterministic
- [ ] Intentional scope overlap is represented explicitly
- [ ] Multiple Attempts per Task work
- [ ] Attempt history is immutable
- [ ] RETRY works
- [ ] REPAIR works
- [ ] REPLAN works
- [ ] CONTEXT_REQUEST works
- [ ] BLOCK works
- [ ] HUMAN_GATE works
- [ ] FAIL works
- [ ] recovery budgets are enforced
- [ ] equivalent failure signatures are detected
- [ ] Plan versions are immutable
- [ ] REPLAN creates a new Plan version
- [ ] old Plan history is preserved
- [ ] resume performs workspace reconciliation
- [ ] interrupted Attempts are not blindly rerun
- [ ] Human Gates survive process restart
- [ ] project-level verification is independent
- [ ] project completion is separately gated
- [ ] API exposes the multi-task lifecycle
- [ ] SSE event stream works
- [ ] UI displays the Task DAG
- [ ] UI displays Attempts and recovery history
- [ ] UI supports Human Gate decisions
- [ ] UI displays live workflow events
- [ ] real Java/Spring multi-task uplift passes
- [ ] failure/recovery acceptance tests pass
- [ ] resume acceptance tests pass
- [ ] no M3 functionality has been pulled into M2

---

## 29. M2 Quality Bar

Do not optimize M2 for feature count.

Optimize for:

- deterministic orchestration
- bounded recovery
- immutable history
- safe reconciliation
- explicit authority
- independent verification
- explainable failures
- testability
- Java/Spring domain correctness

The key M2 question is:

> **Can the Orchestrator safely manage a real Java/Spring uplift when Tasks succeed, fail, require repair, require replanning, encounter human decisions, and survive process interruption?**

If yes, M2 is complete.

