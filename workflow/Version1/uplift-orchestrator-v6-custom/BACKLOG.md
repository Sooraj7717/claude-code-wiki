# V7 Backlog

## Architecture decisions locked

The following architecture decisions are locked and should not be reopened:

1. OpenRewrite is pre-Planning Migration Preparation only; it does not create/execute Tasks or modify the authoritative workspace.
2. Any failed preparation step opens a Human Gate; successful evidence is retained and human-approved continuation may use the existing V6 flow without failed evidence.
3. OpenRewrite-derived Tasks require explicit RecipeRun evidence traceability.
4. OpenRewrite-derived Tasks are P1/high priority only among otherwise READY Tasks; V6 dependencies, scope/conflicts, gates, and Plan ordering remain authoritative.
5. The V7 prototype permits only Apache-2.0-verified OpenRewrite engine/recipe artifacts; non-Apache recipes are rejected before execution and Human-Gated.
6. Normal file-scoped OpenRewrite work produces one Task per affected file; multiple findings for the same file are grouped.
7. Discovery is in-memory by default. `/uplift --force` may overwrite diagnostic JSON files in the fixed project-level `discovery/` directory; no run-based Discovery persistence exists.
8. Planner consumes sealed PlanningContext and produces a structured ProposedPlan; persisted Discovery JSON is never a separate Planner input.

## Remaining implementation-contract details

1. Generic Migration Preparation capability registration/request/result schema.
2. Exact deterministic outstanding-work representation.
3. Preparation staging and baseline mechanics for the ordered dry-run sequence.
4. Exact command/API integration and operator UX for the Human Gate.

## V7 implementation

1. Preparation capability adapter and OpenRewrite Java/Spring skill integration.
2. Immutable RecipeRun artifact storage and provenance.
3. Planning Context builder/sealing/integrity.
4. Evidence-driven Planner handoff.
5. V6 workflow reuse with residual Implementer execution.
6. API/UI preparation evidence and traceability.
7. Preparation events/SSE.
8. End-to-end Java/Spring acceptance.

## Deferred

- parallel execution
- worktrees
- Agent Teams
- distributed execution
- multi-repository workflows
- automatic Git automation
- portfolio orchestration
