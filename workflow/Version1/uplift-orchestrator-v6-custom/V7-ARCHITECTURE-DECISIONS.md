# Uplift Orchestrator V7 — Architecture Decisions

## AD-001 — V7 evolution

**Decision:** V7 = V6 + pluggable migration preparation + evidence-driven planning.

V7 changes the input to Planning, not the V6 workflow execution core.

## AD-002 — OpenRewrite boundary

**Decision:** OpenRewrite is a pluggable Migration Preparation Capability implemented as a skill. It executes before Planning, produces deterministic Planning Evidence, and has no authority to modify the authoritative project workspace or create/execute Tasks.

The skill owns:
- recipes
- recipe sequence
- OpenRewrite/Maven invocation
- OpenRewrite-specific configuration
- native `RecipeRun.json` generation
- OpenRewrite-specific evidence

The Workflow Engine does not own these concerns.

## AD-003 — Preparation evidence is not authority

OpenRewrite output is evidence. It cannot authorize work, create an authoritative Plan, or bypass Plan Gate.

## AD-004 — Planning authority

The Planner consumes a sealed Planning Context and proposes a complete Plan. The Orchestrator validates and authorizes the Plan through Plan Gate.

## AD-005 — Outstanding work is the Planning objective

The Planning Core determines what remains to be done to satisfy the migration objective. OpenRewrite findings are inputs, not a one-to-one Task generator.

## AD-006 — RecipeRun preservation

Native `RecipeRun.json` is preserved unchanged as an immutable artifact. The Orchestrator stores provenance and integrity metadata around it and may derive normalized evidence for Planning.

## AD-007 — Ordered preparation

The Java/Spring preparation capability executes ordered preparation steps by migration intent. The migration objectives remain Java 8 → 21, Spring Boot 1.4 → 2.7, and Spring Boot 2.7 → 3.5, but the recipe artifacts are configuration-driven and must pass the Apache-2.0-only policy. `rewrite-spring` is excluded. Preparation staging must not mutate the actual workflow workspace before an authorized Task executes.

## AD-008 — Fast preparation

Preparation skips unit tests and main compilation. Compilation/tests remain execution/verification concerns.

## AD-009 — V6 Task model retained

V7 Tasks do not have an `OPENREWRITE` execution mechanism. Authorized Tasks represent outstanding work and are executed through the existing V6 execution path.

## AD-010 — Residual implementation

The Implementer remains responsible for custom/residual migration work that cannot be safely completed by deterministic preparation.

## AD-011 — Verification retained

All authorized implementation Attempts still require actual workspace delta capture, scope checking, protected-contract checking, deterministic checks, independent Verifier review, and acceptance criteria evaluation.

## AD-012 — Recovery retained

Preparation failures use the V6 recovery authority and classification model. The skill does not choose workflow recovery.

## AD-013 — Preparation failure is Human-Gated

If any ordered preparation step fails, the Orchestrator opens a durable Human Gate. Successful preparation artifacts remain valid. A human may explicitly choose to continue into the existing V6 discovery/planning flow using only the available evidence, or stop. The failed step is never silently ignored.

## AD-014 — OpenRewrite-derived Task traceability

A Task is OpenRewrite-derived only when it has explicit traceability to a specific RecipeRun artifact/evidence item. Provenance is never inferred from similarity. Planner-created residual/custom work has distinct Planner provenance.

## AD-015 — Priority without scheduler override

OpenRewrite-derived Tasks receive higher scheduling priority only among otherwise READY Tasks. V6 dependencies, scope/conflict rules, gates, and Plan ordering always take precedence. Initial semantic priorities are P0 blocking/prerequisite, P1 OpenRewrite-derived deterministic work, P2 required residual migration work, and P3 optional/cleanup work.

## AD-016 — Discovery persistence

Discovery runs in-memory by default and does not create persisted Discovery files. DiscoveryFacts are incorporated into the sealed PlanningContext. Only when `/uplift --force` is explicitly supplied may Discovery persist diagnostic artifacts to the fixed project-level `discovery/` directory; existing files are overwritten. There is no run-based Discovery persistence and no `.uplift/runs/<run-id>/discovery/` directory. Persistence does not change Planning semantics.

## AD-017 — OpenRewrite license policy

The V7 prototype permits only OpenRewrite engine and recipe artifacts verified as Apache License 2.0. Non-Apache recipe artifacts are rejected before execution, create no RecipeRun, do not modify the authoritative workspace, and open the normal Human Gate. Explicit human continuation uses the normal V6 discovery/planning flow without the rejected evidence. No extra rejection persistence is required.

## AD-018 — OpenRewrite Task grouping

In the normal file-scoped case, the Planner creates exactly one OpenRewrite-derived Task per affected file. Multiple findings or RecipeRun references for the same file are grouped into that Task. Cross-file changes that inherently require cross-file scope may be represented as residual/cross-file Tasks rather than being forced into file-scoped Tasks.

## AD-019 — Planner reasoning and ProposedPlan

The Planner is a reasoning component that consumes the sealed PlanningContext and planning rules. It is not a JSON-to-Task converter. It produces a structured ProposedPlan containing Tasks, dependencies, priorities, evidence/provenance, acceptance criteria, summary counts, planning rationale, and integrity information. ProposedPlan remains non-executable until Plan Gate authorization.

## AD-020 — Portfolio

Portfolio remains reporting/aggregation/navigation only. It does not execute workflow Tasks, Attempts, recovery, or verification.
