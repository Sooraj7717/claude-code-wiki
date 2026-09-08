# Outstanding Work Contract

## Principle

The Planning Core determines and authorizes the work still required to satisfy the migration objective.

## Boundary

```text
Preparation Evidence + Discovery + Constraints + History
                         ↓
                      Planner
                         ↓
               Proposed complete Plan
                         ↓
                     Plan Gate
                         ↓
                  Authorized Tasks
```

Preparation findings are not automatically Tasks. The Planner may accept, combine, split, reject, or supplement preparation findings and may create residual/custom work.

A Task is OpenRewrite-derived only when it explicitly traces to a specific RecipeRun artifact/evidence item. Planner-created residual/custom work has distinct provenance.

For normal file-scoped OpenRewrite work, the Planner creates exactly one OpenRewrite-derived Task per affected file. Multiple findings/RecipeRun references affecting the same file are grouped into that Task. The ProposedPlan exposes affected-file → Task grouping and OpenRewrite Task counts.

## Priority

OpenRewrite-derived Tasks are `P1` and receive higher priority only when competing with other otherwise READY Tasks. V6 dependency, scope/conflict, gate, and Plan-order rules always take precedence. Suggested semantic levels: `P0` blocking/prerequisite, `P1` OpenRewrite-derived deterministic work, `P2` required residual migration work, `P3` optional/cleanup.

## Freeze note

The exact deterministic semantics for identifying and representing outstanding work remain a pre-implementation contract detail; the authority and provenance boundaries are locked.
