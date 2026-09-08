# Generic Migration Preparation Contract

## Purpose

Provide a stable abstraction between the V6/V7 Orchestrator and pluggable migration-preparation capabilities. The capability executes before Planning and produces evidence only; it is not a workflow Task executor.

## Request

```text
MigrationPreparationRequest
├── preparationId
├── runId
├── projectId
├── repositoryBaselineId
├── migrationProfileId
├── capabilityId
├── capabilityConfiguration
└── executionPolicy
```

## Result

```text
MigrationPreparationResult
├── preparationId
├── capabilityId
├── status
├── evidenceArtifactIds[]
├── provenance
├── findingsSummary
├── warnings[]
└── failure
```

## Authority

A preparation capability produces evidence only. It cannot mutate workflow state, authorize a Plan, authorize Tasks, or choose recovery.

## License policy

The V7 prototype permits only OpenRewrite engine and recipe artifacts verified as Apache License 2.0. License verification occurs before recipe execution. A non-Apache recipe artifact is rejected before execution, creates no RecipeRun, and opens the normal Human Gate. If the human continues, the normal V6 discovery/planning flow proceeds without the rejected evidence. No extra license-rejection persistence is required.

## V7 first implementation

`OPENREWRITE_JAVA_SPRING`.

## Failure and partial-success rule

If any ordered preparation step fails, the Orchestrator opens a durable Human Gate. Successful evidence artifacts remain valid. The human may explicitly stop or continue into the existing V6 discovery/planning flow without the failed evidence. The capability never silently bypasses a failed step and never chooses the recovery action itself.

## Freeze note

Capability registration/discovery and exact result schema remain an implementation-contract detail to finalize before implementation freeze; the architectural boundary is locked.
