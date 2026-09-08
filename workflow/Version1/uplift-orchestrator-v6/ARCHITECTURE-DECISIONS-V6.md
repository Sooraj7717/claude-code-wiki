# Architecture Decisions — V6

## Milestone boundary

V5 remains the completed workflow-definition milestone for Java/Spring uplift. V6 extends that milestone with three coordinated capabilities:

1. Workflow engine implementation boundary
2. Orchestrator API contract
3. UI architecture contract

The UI is a control plane over the Orchestrator API. It is not an orchestration engine and never invokes Claude agents directly.

## Authority model

```text
UI -> Orchestrator API -> Workflow Engine -> AgentRunner/Claude Code -> Workspace
```

The Orchestrator owns Run, Plan, Task, Attempt, Human Gate, Recovery, and Completion state. Agents return evidence only.

## Backend technology

The workflow engine and API are Java/Spring Boot. Maven or Gradle is supported according to the repository under uplift. Do not introduce TypeScript, Node.js, Python, Go, Rust, or other implementation languages into the workflow engine specification.

The UI is a separate browser application. Its frontend language/framework is intentionally an implementation concern of the UI layer and must not be confused with the Java/Spring uplift target domain.

## API-first boundary

All UI operations go through versioned Orchestrator APIs. The UI must not read or mutate `.uplift/runs/**` directly and must not invoke Claude Code directly.

## Event delivery

V6 should support an event/status stream, preferably Server-Sent Events (SSE) initially, backed by the append-only event log. Polling remains a fallback.

## Persistence

V6 may retain file-backed persistence for the first implementation milestone, but the workflow engine must expose repository interfaces for state, events, artifacts, plans, and gates so durable database persistence can be introduced later without changing the API contract.

## API semantics

GET operations are read-only. Mutating operations are explicit commands and must pass Orchestrator policy and state-transition validation. The API must return durable resource identifiers and current state rather than agent conversation transcripts as authority.

## UI responsibilities

The UI may:
- inspect runs, plans, tasks, attempts, events, artifacts, diffs, verification, and gates;
- request allowed lifecycle commands such as start, pause, resume, replan, or a human-gate decision;
- subscribe to run events;
- inspect evidence and diffs.

The UI may not:
- choose recovery paths autonomously;
- mark tasks complete directly;
- mutate workflow state files;
- invoke Planner/Implementer/Verifier directly;
- bypass Human Gates, Plan Gates, scope checks, contract checks, or completion gates.

## Java/Spring uplift domain

The workflow contracts and examples must remain specific to Java/Spring modernization, including Java toolchains, Maven/Gradle, Spring Boot, Spring Framework, Jakarta migration, Spring Security, JPA/Hibernate, REST contracts, configuration properties, application startup, and Java public APIs where relevant.
