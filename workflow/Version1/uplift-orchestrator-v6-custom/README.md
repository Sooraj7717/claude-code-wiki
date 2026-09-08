# Uplift Orchestrator V7 — Java/Spring

## Version principle

> **V7 = V6 + pluggable migration preparation + evidence-driven planning.**

V7 preserves the V6 workflow engine, execution model, recovery, verification, persistence, API, UI, and human-control boundaries. V7 adds a preparation layer before Planning and makes Planning evidence-driven.

## OpenRewrite boundary

> **OpenRewrite is a pluggable Migration Preparation Capability. It executes before Planning, produces deterministic Planning Evidence, and has no authority to modify the authoritative project workspace or create/execute Tasks.**

### Licensing policy

The V7 prototype permits only OpenRewrite engine and recipe artifacts verified as **Apache License 2.0**. Non-Apache recipe artifacts are rejected before execution; no `RecipeRun` is created and no workspace change is permitted. The rejection opens the normal Human Gate. `org.openrewrite.recipe:rewrite-spring` and its Spring recipes are excluded. Spring migration objectives remain in scope and uncovered Spring-specific work is Planner-created residual work.

OpenRewrite is **not** a V7 workflow Task execution mechanism. The Workflow Engine does not own recipes, OpenRewrite commands, or OpenRewrite transformation semantics.

If preparation fails at any step, a durable Human Gate is opened. The human may stop or explicitly continue into the normal V6 discovery/planning flow without the missing RecipeRun evidence. Successful earlier RecipeRun artifacts remain valid.

## Fast-track preparation

The first preparation capability is the Java/Spring OpenRewrite skill. Its migration objectives remain:

1. Java 8 → Java 21
2. Spring Boot 1.4 → 2.7
3. Spring Boot 2.7 → 3.5

Only Apache-2.0-verified recipe artifacts may be configured for preparation. The capability must not use `rewrite-spring`. Approved recipe steps are configuration-driven and run as ordered dry-run analyses with tests and main compilation skipped. Native `RecipeRun.json` output is preserved as immutable evidence.

## Canonical workflow lifecycle

```text
                         V7 WORKFLOW

┌──────────────────────────────────────────────────────────────┐
│ COMMAND: /uplift                                             │
│                                                              │
│ INITIALIZING                                                 │
│      ↓                                                       │
│ PREPARING                                                    │
│      │ OpenRewrite Skill                                    │
│      │ • ordered approved Apache-2.0 recipe steps             │
│      │ • migration objectives remain Java/Spring uplift     │
│      │ • RecipeRun.json                                     │
│      ↓                                                       │
│ DISCOVERING                                                  │
│      ↓                                                       │
│ PLANNING                                                     │
│      │ consumes preparation evidence                        │
│      │ determines outstanding work                          │
│      ↓                                                       │
│ PLAN GATE                                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ COMMAND ENDS
                       ▼
                 AUTHORIZED PLAN
                       │
┌──────────────────────▼───────────────────────────────────────┐
│ COMMAND: /execute                                            │
│                                                              │
│ EXECUTING                                                    │
│      │ Implementer makes code changes                        │
│      ↓                                                       │
│ VERIFYING                                                    │
│      ↓                                                       │
│ COMPLETING                                                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ COMMAND ENDS
                       ▼
                    COMPLETE
```

`/uplift` prepares and plans; it does not execute implementation code. `/execute` requires an authorized Plan and does not re-plan. Commands are interaction boundaries; the Workflow Engine owns state transitions.

## Architecture

```text
Project Run
    │
    ▼
Migration Preparation
    │
    └── OpenRewrite Java/Spring Skill
              │
              ▼
      Preparation Evidence
              │
      ┌───────┴────────┐
      ▼                ▼
RecipeRun artifacts  Discovery
      │                │
      └───────┬────────┘
              ▼
       Planning Context
              │
              ▼
           Planner
              │
              ▼
        Proposed Plan
              │
              ▼
          Plan Gate
              │
              ▼
       Authorized Plan
              │
              ▼
        V6 Workflow Core
              │
              ▼
 Tasks → Attempts → Implementer
              │
              ▼
 Scope → Contract → Verification
              │
              ▼
          Completion
```

## What remains V6

- Project/Run lifecycle
- Plan and Plan Gate
- Task DAG and deterministic readiness
- Attempts and workspace baseline/delta
- Implementer / Claude Code adapter
- independent Verifier
- scope enforcement and contract integrity
- recovery, replanning, context requests, Human Gates
- persistence and resume/reconciliation
- Spring Boot Orchestrator API
- operator UI and SSE
- security and audit
- Project Acceptance

## Deliberately excluded from V7

- OpenRewrite workflow execution mechanism
- OpenRewrite-specific Task type
- parallel execution
- Git worktrees
- Agent Teams
- distributed execution
- multi-repository orchestration
- automatic commits/pushes/PRs
- autonomous workflow topology
- portfolio orchestration

Portfolio remains reporting/aggregation only.

## Discovery persistence

Discovery runs in memory and feeds `DiscoveryFacts` to the Planning Context Builder. It creates no files by default. With `/uplift --force`, the current facts may be persisted as diagnostic JSON under the fixed project-level `discovery/` directory, overwriting existing files. There is no `.uplift/runs/<run-id>/discovery/` directory.
