# Uplift Orchestrator V6 — Stage 1 Implementation Specification
## Milestone M1: First Runnable Java/Spring Vertical Slice

**Status:** Implementation-ready milestone specification  
**Parent milestone:** V6 — Workflow Engine + Orchestrator API + UI Architecture  
**Target domain:** Java/Spring uplift only  
**Implementation target:** Java + Spring Boot backend; web UI as a separate frontend layer  
**Primary objective:** Build the smallest real, runnable end-to-end Uplift Orchestrator without prematurely implementing the full V6 platform.

---

## 1. M1 Goal

M1 must prove one complete, controlled uplift lifecycle against a real Java/Spring repository:

```text
Create Run
  -> initialize
  -> discover/plan
  -> Plan Gate
  -> authorize one Task
  -> create Attempt
  -> capture workspace baseline
  -> invoke Implementer
  -> capture actual workspace delta
  -> scope check
  -> deterministic Contract Integrity Check
  -> invoke independent Verifier
  -> Task Completion Gate
  -> Project Completion Gate
  -> visible result in UI
```

M1 is successful only if this is a genuine execution path using Claude Code agents and a real Java/Spring target repository. Mocks/fakes may be used for unit and integration tests, but not as a substitute for the real happy-path acceptance test.

---

## 2. Scope of M1

### 2.1 Workflow Engine

Implement:

- Run aggregate and lifecycle
- initialization
- new-run dirty-worktree detection
- durable HUMAN_GATE for a dirty new run
- one accepted Plan version
- exactly one required Task for the M1 happy path
- Task lifecycle
- Attempt lifecycle
- baseline capture
- workspace delta capture
- deterministic scope checking
- deterministic protected-contract integrity checking
- Implementer invocation
- independent Verifier invocation
- Task Completion Gate
- Project Completion Gate
- `state.json` snapshot
- append-only `events.jsonl`
- durable agent Invocation identity
- durable artifacts
- deterministic READY-task selection, even though M1 contains one task
- safe terminal states

### 2.2 Claude Code Integration

Implement:

- `AgentRunner` abstraction
- `ClaudeCodeAdapter` implementation
- custom Planner, Implementer and Verifier subagents
- fresh context for each invocation
- structured handoff/result contract
- invocation IDs
- role-specific tool policy
- no recursive agent spawning
- Implementer controlled Bash
- destructive-operation PreToolUse protection
- no agent authority over workflow state

M1 does not need the complete recovery matrix. A failure must be recorded durably and terminate safely or open a Human Gate according to the limited M1 policy.

### 2.3 Spring Boot API

Implement minimum API needed by the UI and acceptance tests:

```text
POST /api/v1/runs
GET  /api/v1/runs
GET  /api/v1/runs/{runId}
POST /api/v1/runs/{runId}/start

GET  /api/v1/runs/{runId}/tasks
GET  /api/v1/runs/{runId}/attempts
GET  /api/v1/runs/{runId}/events
GET  /api/v1/runs/{runId}/gates
POST /api/v1/runs/{runId}/gates/{gateId}/decision

GET  /api/v1/runs/{runId}/diff
GET  /api/v1/runs/{runId}/verification
```

Do not expose internal mutable state objects directly as an accidental API. Use explicit DTOs.

API responsibilities:

- validate requests
- call application/workflow services
- return current workflow state
- never independently advance workflow state
- never invoke Claude directly from controllers

Controllers -> Application Service -> Workflow Engine -> AgentRunner.

### 2.4 UI

Build a minimal functional web UI, not the complete platform.

Required views:

1. Runs list
2. Run overview
3. Task/Attempt status
4. Human Gate panel
5. Event timeline
6. Workspace diff
7. Verification result

The UI must consume the API. It must not read `.uplift/runs` directly and must not invoke Claude.

A simple polling implementation is acceptable for M1. Do not require SSE yet.

---

## 3. Java/Spring Uplift Domain

The workflow is specifically for Java/Spring uplift.

M1 must use Java/Spring terminology and validation.

Examples of relevant protected contracts:

- public Java methods
- constructors
- service interfaces
- DTOs
- REST endpoints
- request/response schemas
- event/message contracts
- configuration properties
- persistence-facing contracts where explicitly protected

Typical migration concerns include:

- Java 8 -> Java 21
- Spring Boot 2.x -> 3.x
- Spring Framework 6
- `javax.*` -> `jakarta.*`
- Spring Security
- Spring MVC/WebFlux
- JPA/Hibernate
- Maven or Gradle

Do not introduce TypeScript, Node.js, Python, Go, Rust, or other language migration specifications into the uplift domain.

The UI may use whatever web technology is selected for the frontend implementation, but that technology is not part of the Java/Spring uplift rules.

---

## 4. Locked Architectural Rules

These rules are non-negotiable.

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

Agents may return evidence/results but cannot mutate these states.

### 4.2 Workspace authority

The workspace/Git state is authoritative for actual repository changes.

Never trust an agent statement such as:

> "I only changed these files."

Compute the actual delta.

### 4.3 Fresh context

Every Planner, Implementer and Verifier invocation gets a fresh context.

### 4.4 Verifier independence

Verifier:

- receives fresh context
- reads the resulting workspace
- may execute deterministic checks
- cannot edit/write repository files
- cannot repair its own findings

### 4.5 Implementer Bash

Implementer may use Bash subject to:

- Claude Code permissions
- runtime safety hooks
- task policy
- mandatory post-execution inspection

Bash does not grant workflow authority.

### 4.6 Dirty new run

For a NEW run:

```text
clean tree -> continue
dirty tree -> HUMAN_GATE
```

Do not automatically stash, reset, clean, or discard changes.

Important: this rule does not imply that a future resume of an active Attempt must have a clean tree.

### 4.7 Scope

Unauthorized actual workspace changes outside Task scope result in `HUMAN_GATE` in M1.

### 4.8 Contract integrity

Protected contracts are identified by the Plan.

Unexpected protected-contract changes result in `CONTRACT_VIOLATION` and `HUMAN_GATE`.

A contract may change only when the accepted Plan explicitly authorizes the change.

### 4.9 Git

M1 does not automatically commit, push, reset, clean, rebase, or discard user changes.

Block dangerous commands through hooks.

### 4.10 Agent spawning

Agents cannot spawn other agents.

---

## 5. M1 State Model

Minimum Run states:

```text
INITIALIZING
DISCOVERING
PLANNING
EXECUTING
COMPLETING
COMPLETE

HUMAN_GATE
BLOCKED
FAILED
```

Minimum Task states:

```text
BLOCKED
READY
EXECUTING
VERIFYING
COMPLETE
```

Minimum Attempt states:

```text
CREATED
BASELINED
HANDOFF_READY
EXECUTING
EXECUTION_RETURNED
DELTA_CAPTURED
SCOPE_CHECKED
VERIFYING
VERIFIED
FAILED
HUMAN_GATE
```

Do not implement the full V6 recovery state machine in M1.

---

## 6. Attempt Model

Every Implementer invocation belongs to exactly one Attempt.

An Attempt must record at minimum:

- `attempt_id`
- `run_id`
- `plan_version`
- `task_id`
- `invocation_id`
- role
- status
- created timestamp
- baseline
- resulting delta
- scope result
- contract integrity result
- deterministic check results
- verifier result
- final disposition

Baseline should capture enough information to identify the starting workspace, including:

- Git HEAD
- branch
- tracked status
- relevant working-tree state
- untracked files
- timestamp

Delta must account for:

- added
- modified
- deleted
- renamed
- untracked

Do not assume `git diff` alone captures everything.

---

## 7. Plan and Task Contract

M1 uses one immutable accepted plan, for example:

```text
PLAN-001
```

The Plan must contain:

- plan ID/version
- objective
- one Task
- task ID
- objective
- bounded scope
- dependencies
- protected contracts
- required deterministic checks
- acceptance criteria
- permitted contract changes
- verification requirements

The Orchestrator validates the Plan before execution.

Plan Gate must at minimum check:

1. unique task IDs
2. dependency references
3. no self-dependencies
4. DAG validity
5. bounded scope
6. verification defined
7. acceptance criteria defined
8. protected contracts explicitly represented
9. permitted contract changes explicitly represented

No implementation starts before Plan Gate passes.

---

## 8. Discovery

M1 uses one bounded Planner invocation for discovery/planning.

Planner is evidence-producing, not workflow-authoritative.

Planner tools:

- Read
- Grep
- Glob

Planner must not modify repository files.

Planner should identify enough Java/Spring repository information to construct the single M1 Task, including:

- build system: Maven or Gradle
- wrapper availability
- Java version
- Spring Boot/Spring Framework version where detectable
- relevant source structure
- relevant tests
- likely uplift constraints
- relevant protected contracts
- required verification commands

---

## 9. Handoff Contract

Implementer receives only a bounded handoff containing:

- run ID
- plan version
- task ID
- attempt ID
- objective
- allowed scope
- excluded scope
- dependencies
- relevant discovery artifacts
- protected contracts
- permitted contract changes
- required checks
- constraints

Do not inject the entire run state or the entire repository into the prompt.

Verifier receives:

- task objective
- acceptance criteria
- protected contracts
- permitted contract changes
- expected scope
- required deterministic checks
- relevant artifacts
- resulting workspace directly

Verifier should not rely on the Implementer's narrative as truth.

---

## 10. Agent Results

Define structured result schemas for:

- Plan Result
- Agent Result
- Verification Result
- Attempt
- Run

Agent result must be treated as evidence.

At minimum capture:

```text
invocation_id
role
status
summary
claims/evidence
requested checks
reported failures
artifact references
```

Do not allow agent output to directly set workflow status.

---

## 11. Contract Integrity Check

M1 requires a deterministic check in addition to the Verifier.

At planning time, identify protected contracts.

At post-execution time:

1. capture actual workspace delta
2. compare protected contract representation against baseline
3. compare against explicitly authorized contract changes
4. produce PASS or `CONTRACT_VIOLATION`

For M1, support at least practical checks for Java source/API signatures and repository-declared REST contract files where discoverable.

The exact parser/AST sophistication should be appropriate to M1; do not build a universal Java compiler analysis platform.

---

## 12. Deterministic Verification

Where applicable, run repository-defined deterministic checks such as:

- Maven compile/test
- Maven wrapper
- Gradle compile/test
- Gradle wrapper
- project-defined lint/static checks

Do not hard-code a single build tool.

The Plan identifies the commands.

The Orchestrator records:

- command
- exit code
- duration
- stdout/stderr artifact references
- pass/fail

The Verifier independently evaluates semantic correctness.

---

## 13. Task Completion Gate

A Task may become COMPLETE only when all applicable conditions pass:

- Task is authorized by accepted Plan
- dependencies are complete
- successful Attempt exists
- workspace delta captured
- scope PASS
- contract integrity PASS
- required deterministic checks PASS
- independent Verifier PASS
- acceptance criteria PASS

Agent claims alone are insufficient.

---

## 14. Project Completion Gate

For M1, Project Completion requires:

- all required Tasks complete
- final project verification passes
- project acceptance criteria pass

Because M1 has one Task, this still must be implemented as a distinct Project Completion Gate rather than simply equating Task COMPLETE with Run COMPLETE.

---

## 15. Persistence

Use:

```text
.uplift/
  runs/
    <run-id>/
      state.json
      events.jsonl
      plans/
      tasks/
      attempts/
      invocations/
      artifacts/
      gates/
      verification/
```

The exact directory structure may be refined during implementation, but the ownership boundary must remain.

### state.json

Current snapshot only.

### events.jsonl

Append-only history.

Never rewrite historical events to correct them. Add a new event.

Every meaningful transition/action should produce an event.

Examples:

```text
RUN_CREATED
WORKSPACE_INSPECTED
HUMAN_GATE_OPENED
PLANNER_STARTED
PLANNER_RETURNED
PLAN_CREATED
PLAN_GATE_PASSED
TASK_AUTHORIZED
ATTEMPT_CREATED
BASELINE_CAPTURED
IMPLEMENTER_STARTED
IMPLEMENTER_RETURNED
DELTA_CAPTURED
SCOPE_CHECK_PASSED
CONTRACT_CHECK_PASSED
VERIFIER_STARTED
VERIFIER_RETURNED
TASK_COMPLETED
PROJECT_VERIFICATION_STARTED
PROJECT_COMPLETED
```

---

## 16. Human Gate

M1 must support a durable Human Gate.

At minimum:

```text
gate_id
run_id
reason
type
status
opened_at
context/artifact references
decision
decided_at
```

Required M1 gate scenarios:

- dirty new workspace
- unauthorized scope change
- unauthorized contract change

The UI must allow a human to inspect and make a bounded decision.

Do not let the UI directly mutate `state.json`; it calls the API.

---

## 17. Security / Enforcement

Use layered enforcement:

```text
Prompt
  +
Claude Code permissions
  +
PreToolUse hooks
  +
post-execution deterministic inspection
  +
Orchestrator decisions
```

Implement role restrictions:

| Role | Read | Grep | Glob | Edit | Write | Bash |
|---|---:|---:|---:|---:|---:|---:|
| Planner | yes | yes | yes | no | no | no |
| Implementer | yes | yes | yes | yes | yes | yes |
| Verifier | yes | yes | yes | no | no | yes |

No role may spawn agents.

Block at least:

- `git reset --hard`
- `git clean -f`
- `git checkout --`
- `git restore --source`
- `git push --force`
- `git push -f`
- `git rebase -i`
- `git filter-repo`
- destructive branch deletion

Also protect `.uplift/runs/**` from agent workflow-state mutation as far as Claude Code permissions/hooks allow.

Actual post-execution inspection remains authoritative.

---

## 18. API Error Semantics

Use stable error responses.

Minimum categories:

```text
VALIDATION_ERROR
RUN_NOT_FOUND
INVALID_STATE_TRANSITION
HUMAN_GATE_REQUIRED
PLAN_GATE_FAILED
SCOPE_VIOLATION
CONTRACT_VIOLATION
AGENT_INVOCATION_FAILED
VERIFICATION_FAILED
WORKSPACE_CONFLICT
INTERNAL_ERROR
```

Do not expose stack traces as the normal API error body.

---

## 19. UI M1 Design

Keep the UI deliberately small.

### Runs

List:

- run ID
- repository
- objective
- status
- plan version
- progress
- active gate

### Run Overview

Show:

- lifecycle status
- current task
- current attempt
- plan
- progress
- latest events
- verification
- workspace summary

### Human Gate

Show:

- why gate opened
- affected task/attempt
- evidence
- relevant diff
- available decisions

### Diff

Show:

- added
- modified
- deleted
- renamed
- untracked
- protected-contract changes

### Verification

Show:

- deterministic checks
- verifier result
- acceptance criteria
- final disposition

Do not make the UI a chat interface. Agent conversation is secondary evidence.

---

## 20. Testing Strategy

M1 must have tests at several levels.

### Unit

Test:

- state transitions
- Plan Gate
- scope calculation
- contract integrity
- completion gates
- event creation
- invalid transitions

### Integration

Test:

- API -> workflow engine
- persistence
- fake AgentRunner
- Human Gate decisions
- workspace baseline/delta

### Claude adapter tests

Use a fake Claude executable/runner where possible to test:

- invocation construction
- handoff generation
- result parsing
- non-zero exit handling

### Real acceptance test

Against a small real Java/Spring repository:

1. start from clean workspace
2. create run
3. Planner discovers repository
4. Plan Gate accepts plan
5. Implementer modifies only authorized files
6. actual delta is captured
7. scope passes
8. contract check passes
9. Verifier independently verifies
10. Task Completion Gate passes
11. Project Completion Gate passes
12. UI displays COMPLETE

Also test dirty workspace:

```text
dirty repository
  -> create run
  -> HUMAN_GATE
  -> no implementation occurs
```

And at least one negative test:

```text
Implementer changes file outside scope
  -> SCOPE_VIOLATION
  -> HUMAN_GATE
  -> Task not COMPLETE
```

---

## 21. M1 Non-Goals

Do NOT implement in M1:

- full recovery matrix
- automatic RETRY/REPAIR/REPLAN orchestration
- multiple Plan versions
- sophisticated resume/reconciliation
- parallel task execution
- Git worktrees
- Agent Teams
- distributed execution
- multi-repository orchestration
- automatic commit/push/PR creation
- cloud worker infrastructure
- full enterprise authentication/authorization
- complete event-sourcing architecture
- universal Java AST/API compatibility engine
- full production dashboard
- advanced SSE/event streaming
- autonomous agent-generated workflow topology

These belong to later milestones/backlog.

---

## 22. M1 Definition of Done

M1 is complete only when:

- [ ] Spring Boot backend starts successfully
- [ ] UI starts successfully
- [ ] a Run can be created through the API
- [ ] a Run can be viewed through the UI
- [ ] dirty new worktree opens a durable Human Gate
- [ ] Planner runs through the AgentRunner
- [ ] accepted Plan is persisted
- [ ] one Task is selected deterministically
- [ ] Attempt baseline is persisted
- [ ] Implementer runs with controlled Bash
- [ ] actual workspace delta is captured
- [ ] scope is checked independently
- [ ] protected contract integrity is checked independently
- [ ] Verifier runs with fresh context and no write access
- [ ] deterministic checks are recorded
- [ ] Task Completion Gate is enforced
- [ ] Project Completion Gate is enforced
- [ ] state.json reflects current state
- [ ] events.jsonl preserves history
- [ ] Human Gate decisions are durable
- [ ] UI displays task/attempt/verification/diff status
- [ ] agents cannot mutate workflow state
- [ ] dangerous Git commands are blocked
- [ ] real Java/Spring acceptance test passes
- [ ] negative scope-violation test passes

---

## 23. Implementation Order

Claude Code should implement in this order:

### Phase A — Skeleton

1. Spring Boot application
2. domain models
3. workflow state model
4. persistence abstractions
5. event model
6. API skeleton
7. minimal UI shell

### Phase B — Core vertical slice

8. workspace inspector
9. baseline/delta capture
10. Plan Gate
11. Attempt lifecycle
12. scope checker
13. contract checker
14. completion gates

### Phase C — Claude integration

15. AgentRunner
16. ClaudeCodeAdapter
17. Planner subagent
18. Implementer subagent
19. Verifier subagent
20. structured result parsing
21. permissions/hooks

### Phase D — UI integration

22. Run view
23. Task/Attempt view
24. Gate view
25. Diff view
26. Verification view
27. API integration

### Phase E — Hardening

28. unit tests
29. integration tests
30. security tests
31. real Java/Spring acceptance test
32. negative tests
33. documentation
34. final M1 smoke test

Do not move to M2 functionality until M1 Definition of Done passes.

---

## 24. Architectural Quality Bar

Do not optimize M1 for feature count.

Optimize for:

- deterministic state transitions
- explicit ownership
- durable evidence
- safe failure
- independent verification
- small interfaces
- testability
- clear Java/Spring domain boundaries

Prefer simple explicit implementations over premature frameworks.

The most important M1 question is:

> Can a human observe and trust one complete Java/Spring uplift Task from authorization through independently verified completion?

If not, M1 is not complete.
