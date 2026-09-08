# Uplift Orchestrator V6 — Stage 3

## M3: Production Control Plane & Full UI

This package defines the final implementation milestone of V6 for the Java/Spring Uplift Orchestrator.

### Objective

Turn the M2 workflow engine into a secure, observable, auditable operator control plane.

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

### Prerequisites

- V6 Stage 1 / M1 complete
- V6 Stage 2 / M2 complete
- Existing workflow, recovery, resume, API, and SSE contracts remain authoritative

### M3 focus

1. Workflow-engine hardening
2. Security and enforcement
3. Complete API
4. Full operator UI
5. Observability and audit
6. End-to-end hardening and Java/Spring acceptance

### Important boundaries

The UI never reads `.uplift/runs` directly and never invokes Claude Code directly.

Agents remain workers/evidence producers. They cannot own workflow state.

The Orchestrator remains the authority for:

- Run state
- Plan state
- Task state
- Attempt state
- Human Gates
- recovery
- verification
- completion

### Still out of scope

V6 M3 does not introduce:

- parallel Task execution
- Git worktrees
- Agent Teams
- distributed execution
- multi-repository orchestration
- automatic commits/pushes/PRs
- autonomous workflow topology
- full event sourcing

Those belong to V7+.

### Deliverables

The detailed milestone contract is in:

`V6-STAGE-3-IMPLEMENTATION-SPEC.md`

### V6 end state

```text
M1 — First Vertical Slice
        ↓
M2 — Multi-Task + Recovery + Resume
        ↓
M3 — Production Control Plane + Full UI
        ↓
V6 COMPLETE
```
