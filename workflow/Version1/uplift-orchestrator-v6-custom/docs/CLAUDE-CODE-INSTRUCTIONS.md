# Claude Code Instructions — V7 Java/Spring

## Authority

The Orchestrator is authoritative for workflow state, Plan authorization, Task scope, Attempts, recovery, verification, and completion.

Claude Code is an execution substrate, not a workflow controller.

## OpenRewrite

OpenRewrite is a migration-preparation capability implemented as a skill. Do not introduce an `OPENREWRITE` Task execution mechanism into the workflow engine.

The OpenRewrite Java/Spring skill supplies deterministic preparation evidence to Planning. It does not authorize Tasks.

## Agent roles

Planner:
- Read/Grep/Glob
- no workflow-state mutation
- proposes a complete Plan

Implementer:
- Read/Grep/Glob/Edit/Write/Bash
- only within authorized Task scope
- cannot authorize scope expansion
- cannot mutate `.uplift/runs/**`
- cannot spawn agents

Verifier:
- Read/Grep/Glob/Bash
- independent of the Implementer
- no Edit/Write

## Java/Spring target

Keep migration reasoning focused on Java/Spring uplift concerns: Java compatibility, Spring Boot, Spring Security, Jakarta, JPA/Hibernate, REST/configuration, Maven/Gradle, and repository-defined contracts.
