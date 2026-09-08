# Frontier — Agent State & Workflow Implementation Specification V1

This document is the executable decomposition of the Frontier Prototype Implementation Specification into isolated agent states, deterministic workflows, a single orchestrator, specialized toolsets, and reusable commands.

## 1. Architecture law

```text
Frontier owns:
  state
  transitions
  readiness
  validation
  scope
  gates
  recovery
  persistence

Agents own:
  reasoning
  execution
  recommendations
  evidence

Workspace/Git owns:
  actual source-change truth
```

## 2. Agent surface

Only two components are reasoning-oriented agents:

```text
Planner Agent
Worker Agent
```

Verifier is a capability boundary; it may be deterministic or semantic. Repository Inspector is deterministic. Recovery is deterministic.

## 3. Isolation

No direct:

```text
Planner → Worker
Worker → Planner
Worker → Verifier
Verifier → Worker
```

Only the Frontier orchestrator coordinates these calls.

## 4. Workflow states

### Project

```text
INITIALIZING
DISCOVERING
PLANNING
EXECUTING
COMPLETING
COMPLETE

BLOCKED
HUMAN_GATE
FAILED
```

### Task

```text
BLOCKED
READY
EXECUTING
VERIFYING
COMPLETE
```

Recovery operations are not persistent states.

## 5. State-machine rules

Only Frontier mutates state. DAG readiness is deterministic. Completed tasks are immutable by default. Revised plans preserve completed history.

## 6. Core workflows

1. Lifecycle
2. Inspect and Plan
3. Execute Task
4. Recover
5. Replan
6. Human Gate
7. Project Completion

See `workflows/` for isolated procedures.

## 7. Toolsets

```text
Repository Inspector
Git / Workspace Truth
Java Build / Test
OpenRewrite
Scope Enforcement
Verification
```

Toolsets are deterministic where possible and are not agents.

## 8. Reusable commands

```text
frontier inspect
frontier plan
frontier run
frontier verify
frontier replan
frontier status
frontier resume
```

Each command has a narrow purpose and should be invokable from Claude Code or a future CLI without embedding workflow logic inside the command itself.

## 9. Verification policy

```text
actual diff
→ scope
→ deterministic checks
→ semantic LLM verification only when necessary
```

LLMs must not be used for DAG validation, readiness, scope, diff inspection, retry counting, policy checks, or completion gating.

## 10. Recovery policy

```text
RETRY
REPAIR
REPLAN
BLOCK
HUMAN_GATE
FAIL
```

Recovery is table-driven/deterministic. Agent classifications are advisory.

## 11. Persistence

```text
.frontier/
├── project.json
├── plan.json
└── attempts/
```

Persist after meaningful workflow boundaries. Resume must reconcile persisted state with actual workspace/Git state.

## 12. Definition of done

The system can:

- initialize
- inspect read-only
- plan
- validate the DAG
- validate scope/conflicts
- select READY tasks
- execute a Worker
- inspect actual changes
- reject out-of-scope changes
- deterministically verify
- optionally semantically verify
- retry
- repair
- replan
- preserve completed history
- pause for human approval
- persist
- resume
- perform project-level acceptance
- complete
- fail safely

## 13. Non-goals

No distributed execution, agent fleet, message bus, worker pool, scheduler framework, capability marketplace, event sourcing, persistent agent sessions, or sophisticated reconciliation engine is required for V1.
