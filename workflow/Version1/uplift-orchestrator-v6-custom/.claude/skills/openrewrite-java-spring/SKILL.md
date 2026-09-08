# OpenRewrite Java/Spring Migration Preparation Skill

## Purpose

Provide deterministic pre-planning migration evidence for Java/Spring uplift workflows.

## Contract

Input: a bounded repository baseline, migration profile, and preparation configuration.

Output: immutable native OpenRewrite `RecipeRun.json` evidence for each configured preparation step plus provenance metadata.

## Licensing policy

The V7 prototype permits **only OpenRewrite engine and recipe artifacts verified as Apache License 2.0**. License verification is mandatory before a recipe artifact is executed.

- Reject any non-Apache-2.0 recipe artifact before OpenRewrite starts.
- Do not create a `RecipeRun` for a rejected artifact.
- Do not modify the authoritative workspace.
- Open the normal Orchestrator Human Gate.
- If the human continues, proceed through the normal V6 discovery/planning path without the rejected evidence.
- Do not use `org.openrewrite.recipe:rewrite-spring` or its Spring recipes.

## Migration objectives

The target objectives remain:

1. Java 8 → Java 21
2. Spring Boot 1.4 → 2.7
3. Spring Boot 2.7 → 3.5

These objectives are not a license exception. Spring-specific work not covered by an approved Apache-2.0 recipe becomes residual Planner work.

## Ordered preparation

Preparation steps are ordered by migration intent. Recipe modules such as `rewrite-core`, `rewrite-java`, and Maven integration are supporting dependencies, not workflow steps. Each logical step runs against the logical staging state produced by the previous step, while the authoritative workspace remains untouched.

## Boundaries

- Do not modify the real workflow workspace.
- Do not modify `.uplift/runs/**` workflow state.
- Do not authorize Tasks or Plans.
- Do not run unit tests or main compilation during preparation.
- Preserve native RecipeRun output unchanged.
- Report failures to the Orchestrator; do not select workflow recovery.
