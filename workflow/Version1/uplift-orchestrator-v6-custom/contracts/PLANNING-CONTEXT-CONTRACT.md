# Planning Context Contract

## Purpose

Provide the Planner with one bounded, immutable, evidence-driven planning input.

## Structure

```text
PlanningContext
├── contextId
├── schemaVersion
├── runId
├── projectId
├── repositoryBaseline
├── migrationProfile
├── preparationEvidence
├── discoveryEvidence
├── projectConstraints
├── planHistory
└── contextIntegrity
```

## Rules

- Context is sealed before Planner consumption.
- Source artifact IDs/hashes are retained.
- RecipeRun evidence is evidence, not authority.
- OpenRewrite-derived work must retain explicit RecipeRun evidence traceability.
- Preparation evidence may be partial when a human has explicitly authorized continuation after a preparation failure.
- Planner proposes a Plan; Plan Gate authorizes it.
- Context is never mutated in place.


## Discovery input semantics

Discovery produces in-memory `DiscoveryFacts`. The Planning Context Builder incorporates those facts into `discoveryEvidence` before sealing the context. The Planner consumes the sealed context rather than reading persisted Discovery JSON.

When `/uplift --force` is supplied, the same current DiscoveryFacts may be persisted as diagnostic files under the fixed project-level `discovery/` directory, overwriting existing files. Those files are not a second Planning input path.

## Planner reasoning

The Planner reasons over the combined context: preparation evidence, Discovery facts, migration objective, constraints, plan history, dependencies, and planning rules. It determines outstanding work and produces a structured `ProposedPlan`; it does not blindly convert findings into Tasks.
