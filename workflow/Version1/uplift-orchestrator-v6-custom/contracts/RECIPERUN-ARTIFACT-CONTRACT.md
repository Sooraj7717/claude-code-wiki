# RecipeRun Artifact Contract

Native OpenRewrite `RecipeRun.json` is preserved unchanged.

## Envelope

```text
RecipeRunArtifact
├── artifactId
├── artifactType
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

## Rules

- SHA-256 integrity hashes.
- Immutable after capture/validation.
- Re-execution creates a new artifact.
- `artifactId` is distinct from content hash.
- All successful ordered preparation-step artifacts are linked by a preparation manifest; the manifest is not limited to a fixed number of steps.
- Successful artifacts remain valid if a later preparation step fails and a human authorizes continuation.
- Missing/failed steps must remain explicitly represented as unavailable; they must never be implied to have succeeded.
