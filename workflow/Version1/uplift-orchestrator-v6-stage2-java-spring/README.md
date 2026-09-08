# Uplift Orchestrator V6 — Stage 2

## M2: Multi-Task Orchestration, Recovery & Resume

This package contains the implementation milestone specification for **V6 Stage 2 / M2**.

### Prerequisite

V6 Stage 1 / M1 must be complete and pass its Definition of Done before M2 implementation begins.

### Milestone objective

M2 turns the M1 single-task vertical slice into a real Java/Spring uplift orchestrator supporting:

- multi-task dependency DAGs
- deterministic task selection
- multiple Attempts
- RETRY / REPAIR / REPLAN
- bounded Context Requests
- BLOCK / HUMAN_GATE / FAIL
- recovery budgets
- failure signatures
- immutable Plan versions
- project verification
- resume/reconciliation
- expanded Spring Boot API
- SSE event streaming
- workflow-oriented UI

### Implementation rule

Build M2 incrementally on top of M1. Do not rewrite the architecture merely to add features.

The Orchestrator remains the workflow authority. Claude Code agents remain bounded workers/evidence producers.

### Domain constraint

The uplift workflow is specifically for Java/Spring applications.

Do not add TypeScript, Node.js, Python, Go, Rust, or other-language migration rules to the uplift engine.

The frontend is a separate application layer. Its implementation technology does not change the Java/Spring uplift domain.

### Stop condition

Claude Code must stop at M2 when the M2 Definition of Done passes. Do not pull M3 functionality into this milestone.
