# Instructions for Claude Code — Build Uplift Orchestrator V5

You are implementing the Uplift Orchestrator V5 workflow described in `IMPLEMENTATION-SPEC-V5.md`.

## Before implementation

1. Read `IMPLEMENTATION-SPEC-V5.md`.
2. Read `ARCHITECTURE-DECISIONS.md`.
3. Read `Backlog.md`.
4. Treat the locked architecture as authoritative.
5. Inspect the existing repository if this is an upgrade of an existing Uplift Orchestrator implementation.

## Critical restriction

This workflow is for **Java/Spring uplift**. Do not introduce TypeScript/Node-specific migration concepts, examples, schemas, fixtures, or acceptance rules. Java/Spring target-repository semantics are mandatory.

## Implementation behavior

- Do not ask an agent to manage global workflow state.
- Do not let AgentResult directly mutate state.
- Do not allow Planner or Verifier writes.
- Do not allow agent spawning.
- Do not begin implementation before full Plan Gate acceptance.
- Do not automatically clean or reset a dirty new-run repository.
- Do not attribute pre-existing changes to an Attempt.
- Do not accept out-of-scope changes.
- Do not accept unauthorized contract changes.
- Always create an Attempt for implementation.
- Always invoke an independent Verifier for every implementation Attempt.
- Always persist durable evidence.
- Never blindly rerun an interrupted Attempt during resume.
- Keep recovery bounded.
- Keep history immutable/history-preserving.

## Build strategy

Implement deterministic workflow helpers first, then schemas/contracts, then Claude Code agents/commands/hooks, then integration tests.

Prefer small composable scripts/helpers over giant prompt-only orchestration.

## Definition of done

Run the deterministic test suite and demonstrate the acceptance criteria in Section 30 of the implementation specification.
