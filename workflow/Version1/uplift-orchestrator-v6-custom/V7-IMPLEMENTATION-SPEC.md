# Uplift Orchestrator V7 — Java/Spring Implementation Specification

## 1. Purpose

V7 is a fast-track evolution of V6 for Java/Spring application uplift. It adds a pluggable migration-preparation layer and evidence-driven Planning while retaining the V6 workflow core.

## 2. Target envelope

Primary uplift scenarios:
- Java 8 → Java 21
- Spring Boot 1.4 → 2.7
- Spring Boot 2.7 → 3.5
- Maven and Gradle projects where supported by the existing V6 workflow
- Spring Security
- Jakarta migration
- JPA/Hibernate
- REST/configuration and repository-defined public contracts

The uplift specification is Java/Spring-specific. TypeScript, Node.js, Python, Go, and Rust are outside this target envelope.

## 3. End-to-end lifecycle

```text
INITIALIZING
    ↓
PREPARING
    ↓
DISCOVERING
    ↓
PLANNING
    ↓
PLAN GATE
    ↓
EXECUTING
    ↓
COMPLETING
    ↓
COMPLETE
```

Existing V6 control states remain available: `BLOCKED`, `HUMAN_GATE`, `FAILED`.

`PREPARING` is the V7 addition at the Run/control level. Preparation produces deterministic evidence when successful. If any preparation step fails, the Orchestrator opens a durable Human Gate; the human may stop or explicitly continue into the existing V6 discovery/planning flow without the missing evidence.

## 4. Generic Migration Preparation Contract

A preparation capability is invoked through a generic contract so the Workflow Engine is not coupled to OpenRewrite.

### Request

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

### Result

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

The capability must not mutate Orchestrator state. It may use an isolated staging area for analysis/preparation.

## 5. OpenRewrite Java/Spring preparation capability

The first capability is `OPENREWRITE_JAVA_SPRING`.

### Ordered preparation steps

The preparation capability is sequence-driven, but the exact recipe artifacts are configuration-driven. The V7 prototype is **Apache-2.0-only for OpenRewrite engine and recipe artifacts**. No non-Apache recipe artifact may be executed.

A configured recipe artifact must pass license verification **before** the OpenRewrite process starts. If the artifact is not verified as Apache License 2.0, the step is rejected, no `RecipeRun` is created, the authoritative workspace remains untouched, and the Orchestrator opens the normal Human Gate. No special rejection artifact is required.

The migration objectives remain: 

1. Java 8 → 21
2. Spring Boot 1.4 → 2.7
3. Spring Boot 2.7 → 3.5

These objectives do **not** imply use of `rewrite-spring`. In particular, `org.openrewrite.recipe:rewrite-spring` and its Spring recipes are excluded from the V7 prototype. Spring-specific migration work not covered by an approved Apache-2.0 recipe remains residual Planner-created work and is executed through the normal V6 Task path.

Each approved preparation step uses OpenRewrite dry-run semantics with tests and main compilation skipped as configured by the preparation contract. Recipe coordinates and versions must remain configuration-driven; pinning approved versions is preferred for reproducibility.

## 6. Preparation workspace rule

The real workflow workspace remains untouched before Plan authorization and Task execution.

Preparation uses an isolated/staging representation sufficient to execute the ordered dry-run analysis and capture evidence.

The sequence is logically:

```text
Original baseline
    ↓
Preparation staging state 0
    ↓ Step 1 analysis
RecipeRun #1
    ↓ logical Step 1 staging
Preparation staging state 1
    ↓ Step 2 analysis
RecipeRun #2
    ↓ logical Step 2 staging
Preparation staging state 2
    ↓ Step 3 analysis
RecipeRun #3
```

If the implementation cannot safely establish the required sequential staging semantics, preparation must fail or enter the configured Human Gate rather than silently treating all three steps as independent analyses of the original baseline.

## 7. RecipeRun Artifact Contract

Native OpenRewrite `RecipeRun.json` is preserved unchanged.

The Orchestrator envelope records:

```text
RecipeRunArtifact
├── artifactId
├── artifactType = OPENREWRITE_RECIPE_RUN
├── schemaVersion
├── runId
├── projectId
├── preparationId
├── stepId
├── sequence
├── repositoryBaselineId
├── repositoryRevision
├── openRewriteVersion
├── recipeArtifactCoordinates
├── activeRecipe
├── recipeConfigurationHash
├── executionId
├── startedAt
├── completedAt
├── nativeArtifactHash
└── nativeArtifactReference
```

Use SHA-256 for integrity hashes. `artifactId` and content hash are distinct concepts.

Artifacts are immutable. Re-execution creates new artifacts.

## 8. Preparation Manifest

One manifest ties the ordered artifacts together:

```text
OpenRewritePreparationManifest
├── preparationId
├── runId
├── capabilityId
├── status
├── repositoryBaselineId
├── sequence
│   ├── Step 1 → RecipeRun artifact
│   ├── Step 2 → RecipeRun artifact
│   └── Step 3 → RecipeRun artifact
└── provenance
```

## 9. Planning Context Contract

Planning receives one sealed, immutable context:

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

`preparationEvidence` references RecipeRun artifacts and a normalized representation.

The Planner should not need to parse raw OpenRewrite JSON to understand common evidence.

Discovery is also represented as in-memory `DiscoveryFacts` and incorporated into the sealed `PlanningContext`. Persisted Discovery JSON is diagnostic only and is never a second Planning input path.

## 10. Normalized preparation evidence

```text
PreparationEvidence
├── preparationId
├── capabilityId
├── stepId
├── recipe
├── affectedFiles
├── affectedResources
├── findingCount
├── transformationCount
├── sourceLocations
├── categories
└── rawArtifactReference
```

Exact normalized fields may evolve according to the observed OpenRewrite output, but the native artifact remains unchanged.

## 11. Candidate versus authorized work

Preparation evidence may be converted into deterministic candidate migration work, but candidate work is not authoritative.

```text
RecipeRun
  ↓
Normalized Evidence
  ↓
Candidate Work
  ↓
Planner
  ↓
Proposed Plan
  ↓
Plan Gate
  ↓
Authorized Tasks
```

The candidate extractor must not become a second planning authority.

For OpenRewrite-derived work, the normal file-scoped invariant is **one Task per affected file**. Multiple findings or RecipeRun references affecting the same file are grouped into that single Task. RecipeRun count and finding count do not determine Task count. If a change inherently spans multiple files and cannot be safely represented as file-scoped work, the Planner may create a cross-file/residual Task instead of falsely forcing file scope.

The final ProposedPlan must expose affected-file → Task grouping and the OpenRewrite-derived Task count.

## 12. Outstanding Work semantics

The Planning Core answers:

> What work remains necessary to satisfy the migration objective, given preparation evidence, discovery evidence, project constraints, and history?

Planning must account for:
- work evidenced by preparation
- work not covered by preparation
- application-specific code changes
- configuration changes
- protected contract impacts
- dependency and sequencing requirements
- verification requirements
- completed historical work

OpenRewrite findings are never assumed to equal the complete migration scope.

## 13. Task priority and deterministic readiness

OpenRewrite-derived Tasks receive higher scheduling priority only among otherwise READY Tasks. V6 dependencies, scope/conflict rules, gates, and Plan ordering always take precedence. No second scheduler is introduced.

Initial semantic priority levels:
- `P0` — blocking / prerequisite
- `P1` — OpenRewrite-derived deterministic work
- `P2` — required residual migration work
- `P3` — optional / cleanup

The selection sequence is:

```text
Dependencies / DAG
    ↓
Scope / conflicts / gates
    ↓
READY Tasks
    ↓
Semantic priority
    ↓
Deterministic selection
```

## 14. Planner contract

Planner input:

```text
runId
projectId
contextId
planVersion
PlanningContext
planningRules
```

The Planner is a reasoning component, not a JSON-to-Task converter. It determines outstanding work from preparation evidence, Discovery facts, migration objectives, constraints, history, dependencies, and planning rules.

Planner output is a structured `ProposedPlan` (JSON-compatible domain representation) with at least:

```text
ProposedPlan
├── planId
├── runId
├── projectId
├── schemaVersion
├── planningContextId
├── status = PROPOSED
├── summary
│   ├── totalTasks
│   ├── openRewriteTasks
│   └── residualTasks
├── tasks[]
│   ├── taskId
│   ├── type
│   ├── title
│   ├── scope
│   ├── priority
│   ├── dependencies[]
│   ├── evidence[]
│   └── acceptanceCriteria[]
├── planningRationale
└── integrity
```

For OpenRewrite-derived tasks, `evidence[]` must retain explicit RecipeRun/artifact references. The ProposedPlan is not executable until Plan Gate authorization.
```

Planner has no authority to mutate Orchestrator state, authorize Tasks, execute migration work, or bypass Plan Gate.

## 14. V6 workflow core retained

After Plan Gate, V7 follows the V6 model:

```text
Authorized Plan
   ↓
Task DAG
   ↓
READY selection
   ↓
Attempt
   ↓
Implementer / Claude Code
   ↓
Workspace delta
   ↓
Scope check
   ↓
Protected contract check
   ↓
Independent Verifier
   ↓
Task acceptance
   ↓
Project verification
   ↓
Complete
```

There is no OpenRewrite Task execution mechanism in V7.

## 15. Task and Attempt

Task lifecycle remains:

```text
BLOCKED → READY → EXECUTING → VERIFYING → COMPLETE
```

Attempt remains the concrete execution/audit unit with the V6 lifecycle:

```text
CREATED → BASELINED → HANDOFF_READY → EXECUTING →
EXECUTION_RETURNED → DELTA_CAPTURED → SCOPE_CHECKED →
VERIFYING → VERIFIED / RECOVERY / FAILED / HUMAN_GATE
```

Actual workspace delta, including untracked files, is authoritative.

## 16. Implementer

The Implementer is retained for residual/custom migration work.

It receives bounded handoffs containing:
- task objective
- authorized scope
- acceptance criteria
- protected contract constraints
- relevant Planning Context evidence
- attempt identity

It cannot authorize scope expansion or workflow transitions.

Claude Code remains the execution substrate. The AgentRunner/ClaudeCodeAdapter owns invocation lifecycle details.

## 17. Verification

Every implementation Attempt requires:

1. actual delta capture
2. scope validation
3. protected-contract integrity check
4. deterministic checks
5. independent Verifier
6. Task acceptance criteria

Project Completion requires all required Tasks complete plus final independent project verification.

## 18. Recovery and fallback

Recovery authority remains with the Orchestrator.

Preparation failures use the V6 classification model:

```text
transient tool failure → RETRY
missing bounded fact → CONTEXT_REQUEST
inadequate preparation/planning input → REPLAN where applicable
ambiguous/provenance/safety/workspace issue → HUMAN_GATE
unrecoverable/repeated equivalent failure → FAIL
```

Recommended default: OpenRewrite preparation is an accelerator, but failure is never silently bypassed. Any failed preparation step opens a Human Gate. A human may explicitly continue without the failed evidence, preserving the V6 workflow as the safety net; safety, baseline, provenance, or workspace integrity failures should require an explicit human decision.

## 19. Persistence and resume

Retain V6 state model:

```text
.uplift/runs/<run-id>/
    state.json
    events.jsonl
    artifacts/
    preparation/
    planning/
```

Discovery does **not** use run-based persistence. By default Discovery produces in-memory `DiscoveryFacts` only. When `/uplift --force` is explicitly supplied, the current Discovery facts may additionally be written as diagnostic JSON files to the fixed project-level `discovery/` directory; existing files are overwritten. There is no `.uplift/runs/<run-id>/discovery/` directory and no Discovery history/snapshot retention. Planning semantics are identical with or without `--force`.

The Orchestrator owns state and events.

Preparation artifacts are immutable. Planning Contexts are immutable after sealing.

On resume:
1. load state
2. validate event/state consistency
3. reconcile workspace
4. reconcile active preparation/Attempt/Gate
5. detect baseline mismatch or unexpected mutation
6. continue only from a safe durable state

Never blindly rerun an interrupted Attempt.

## 20. Security

Prompt text is not the security boundary.

Use:
- Claude Code permissions
- runtime hooks
- controlled Bash
- Orchestrator policy
- post-execution inspection

Preparation capabilities receive bounded permissions and cannot mutate `.uplift/runs/**` workflow state.

Security events retain the V6 model, including:
`TOOL_BLOCKED`, `UNSAFE_COMMAND_BLOCKED`, `PERMISSION_DENIED`, `SCOPE_VIOLATION`, `CONTRACT_VIOLATION`, `WORKFLOW_STATE_TAMPERING`, `HUMAN_GATE_OPENED`.

## 21. API changes from V6

Retain all V6 Run/Plan/Task/Attempt/Verification/Diff/Gate/Event/Artifact endpoints.

Add preparation/evidence read APIs:

```text
GET /api/v1/runs/{runId}/preparation
GET /api/v1/runs/{runId}/preparation/artifacts
GET /api/v1/runs/{runId}/preparation/artifacts/{artifactId}
GET /api/v1/runs/{runId}/planning-context
```

Exact command APIs remain V6 command-oriented and workflow-state validated.

## 22. UI changes from V6

Retain the V6 control plane and add:
- preparation status
- migration capability
- ordered preparation steps
- RecipeRun evidence summary
- preparation artifacts
- Planning Context summary
- outstanding-work view
- evidence-to-plan traceability

The UI never reads `.uplift/runs` directly and never invokes a preparation capability or Claude Code directly.

## 23. SSE/events

Retain V6 SSE. Add preparation lifecycle events such as:

```text
PREPARATION_CREATED
PREPARATION_STARTED
PREPARATION_STEP_STARTED
PREPARATION_STEP_COMPLETED
PREPARATION_ARTIFACT_CAPTURED
PREPARATION_COMPLETED
PREPARATION_FAILED
PLANNING_CONTEXT_CREATED
PLANNING_CONTEXT_SEALED
```

Stable identifiers should include `run_id`, `project_id`, `preparation_id`, and `artifact_id` where applicable.

## 24. Genuine remaining gaps to resolve before implementation freeze

### Gap A — Generic preparation contract details
Finalize capability registration/discovery and exact request/result schema.

### Gap B — Outstanding-work semantics
Finalize the deterministic boundaries between preparation evidence, candidate work, Planner reasoning, and authorized Tasks.

### Gap C — Preparation staging/baseline semantics
Finalize how the sequential dry-run stages establish their logical input state while keeping the real workspace untouched.

### Gap D — Preparation failure/fallback policy
Finalize the generic failure classification and recovery integration. The non-Apache recipe-license policy is already locked: reject before execution, create no RecipeRun, open Human Gate, and allow explicit human continuation through the normal V6 flow without the rejected evidence.

These are the remaining implementation-contract details. Locked architectural decisions are not reopened during implementation.

## 25. Non-goals

- parallel Task execution
- Git worktrees
- Agent Teams
- distributed workers
- multi-repository orchestration
- automatic commit/push/PR
- autonomous semantic conflict resolution
- portfolio orchestration
- full event sourcing
- universal AST migration engine
- arbitrary workflow topology
