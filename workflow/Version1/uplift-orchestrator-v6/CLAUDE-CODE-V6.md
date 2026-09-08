# Claude Code Implementation Instructions — V6

Build the V6 milestone from this specification and the V5 baseline.

## Mandatory domain

This is a Java/Spring uplift orchestration system. Keep the workflow engine and its domain examples Java/Spring-specific. Support Maven and Gradle repositories as appropriate.

Do not replace the Java/Spring workflow engine with TypeScript, Node.js, Python, Go, Rust, or another backend language.

## Architecture

Implement:

```text
UI -> Spring Boot Orchestrator API -> Workflow Engine -> AgentRunner -> Claude Code agents
```

The UI must not call agents directly.

## Preserve V5 invariants

- Orchestrator owns workflow state.
- Agents produce evidence only.
- Fresh agent context per invocation.
- Every implementation invocation belongs to one Attempt.
- Workspace/Git state is authoritative for actual changes.
- Every implementation Attempt gets independent verification.
- Deterministic contract integrity checks are mandatory.
- Recovery is selected by Orchestrator, not agents or UI.
- Human Gates are durable.
- State snapshot plus append-only event history.
- No blind rerun after interruption.
- No automatic commit/push.
- Implementer uses controlled Bash with permissions/hooks/post-checks.

## Implementation order

1. Establish Java/Spring Boot project and package boundaries.
2. Implement domain models and explicit state transitions.
3. Implement persistence repositories and append-only events.
4. Implement AgentRunner/ClaudeCodeAdapter boundary.
5. Implement deterministic workspace/scope/contract checks.
6. Implement workflow engine orchestration.
7. Implement REST API and OpenAPI contract.
8. Implement SSE event stream.
9. Implement UI against the API contract.
10. Add integration/smoke tests for API, state transitions, gates, attempts, recovery, resume, and UI/API boundaries.

Do not collapse workflow policy into controllers.
