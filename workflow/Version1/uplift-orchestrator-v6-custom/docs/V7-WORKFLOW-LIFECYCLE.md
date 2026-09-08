# V7 Workflow Lifecycle

## Canonical lifecycle

```text
                         V7 WORKFLOW

┌──────────────────────────────────────────────────────────────┐
│ COMMAND: /uplift                                             │
│                                                              │
│ INITIALIZING                                                 │
│      ↓                                                       │
│ PREPARING                                                    │
│      │ OpenRewrite Preparation Capability                  │
│      │ • ordered approved Apache-2.0 recipe steps          │
│      │ • native RecipeRun.json evidence                    │
│      ↓                                                       │
│ DISCOVERING                                                  │
│      ↓                                                       │
│ PLANNING                                                     │
│      │ consumes sealed PlanningContext                       │
│      │ reasons over preparation + Discovery + constraints   │
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

## Command boundaries

- `/uplift`: starts at initialization and owns preparation, discovery, planning, and Plan Gate. It ends at an authorized Plan. It does not execute implementation Tasks.
- `/execute`: requires an authorized Plan. It owns Task execution, verification, and completion. It does not re-plan.
- Commands are interaction boundaries; the Workflow Engine remains authoritative for lifecycle state transitions.

## OpenRewrite preparation rule

OpenRewrite is a pluggable Migration Preparation Capability. It executes before Planning, produces deterministic Planning Evidence, and has no authority to modify the authoritative project workspace or create/execute Tasks.

If a preparation step fails, the Orchestrator opens a durable Human Gate. Successful prior evidence remains usable if the human explicitly authorizes continuation.


## Discovery persistence

Discovery runs in-memory by default and produces `DiscoveryFacts` for the Planning Context Builder. It does not create Discovery files. If `/uplift --force` is explicitly supplied, Discovery may persist the current facts as diagnostic JSON files under the fixed project-level `discovery/` directory; existing files are overwritten. There is no `.uplift/runs/<run-id>/discovery/` persistence and no Discovery history retention. Planning semantics are identical with or without `--force`.

## Plan boundary

The Planner consumes the sealed PlanningContext and produces a structured `ProposedPlan`. The ProposedPlan remains non-executable until Plan Gate authorization. Once authorized, `/execute` consumes the Authorized Plan and reuses the V6 Task/Attempt/Implementer/Verifier execution core without re-planning.
