# Uplift Orchestrator V6 — Java/Spring

V6 is the next milestone after V5.

## Scope

V6 adds:

1. Workflow engine implementation boundary
2. Spring Boot Orchestrator API
3. UI architecture contract
4. API-first UI integration
5. SSE event/status delivery

V5 remains an immutable milestone and is the baseline for workflow semantics.

## Domain

The system orchestrates Java/Spring uplift workflows. Maven and Gradle are supported according to the target repository.

The UI is a separate frontend concern; it does not change the Java/Spring uplift domain.

## Read first

- `IMPLEMENTATION-SPEC-V6.md`
- `ARCHITECTURE-DECISIONS-V6.md`
- `API-CONTRACT-V6.md`
- `UI-ARCHITECTURE-CONTRACT-V6.md`
- `CLAUDE-CODE-V6.md`
- `Backlog.md`

## Core boundary

```text
UI
 ↓
Spring Boot Orchestrator API
 ↓
Workflow Engine
 ↓
AgentRunner / Claude Code
 ↓
Java/Spring target workspace
```
