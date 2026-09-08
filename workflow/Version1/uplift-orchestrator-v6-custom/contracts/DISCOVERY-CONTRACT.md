# Discovery Contract

## Purpose

Define how repository Discovery supplies facts to Planning without making Discovery a second planning authority or requiring persisted files on every run.

## Output

Discovery produces an in-memory `DiscoveryFacts` structure containing bounded repository facts such as:

```text
DiscoveryFacts
├── repository
├── build
├── dependencies
├── sourceInventory
├── frameworks
├── constraints
└── contracts
```

These facts are passed to the Planning Context Builder and incorporated into the sealed `PlanningContext.discoveryEvidence`.

## Default persistence rule

Discovery does **not** create persisted files by default. There is no run-based Discovery persistence under `.uplift/runs/<run-id>/discovery/`.

## `--force` diagnostic persistence

When `/uplift --force` is explicitly supplied, the current DiscoveryFacts may additionally be serialized as diagnostic JSON files in the fixed project-level directory:

```text
discovery/
├── repository.json
├── build.json
├── dependencies.json
├── source-inventory.json
├── frameworks.json
├── constraints.json
└── contracts.json
```

Existing files are overwritten. No historical Discovery snapshots are retained.

## Planning authority

Persisted Discovery JSON is diagnostic output only. The Planner never reads these files as a separate input path; it consumes the sealed PlanningContext. `--force` does not alter Planning semantics.
