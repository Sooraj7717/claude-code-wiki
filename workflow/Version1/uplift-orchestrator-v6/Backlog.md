# Uplift Orchestrator V5 Backlog

These items are intentionally excluded from the V5 implementation unless required to preserve a locked invariant.

- Split Discovery into multiple bounded Planner invocations (repository/tooling, implementation, tests/verification).
- Parallel Task execution using Git worktrees.
- Worktree lifecycle, merge/integration policy, conflict detection, and post-integration re-verification.
- Clean-room verification from a reconstructed base plus patch.
- Containerized verification and undeclared-environment dependency detection.
- Automatic commit/branch/PR workflow.
- More advanced Java AST/bytecode/API compatibility analysis.
- Automated Spring Boot migration recipes/catalogues beyond repository-driven discovery.
- Persistent metrics/telemetry dashboards.
- Full event-sourcing implementation.
- Distributed/remote execution.
- Agent capability registry.
- Generic multi-language uplift framework.

## V6+ / UI and Engine Future Enhancements

- Persistent database implementation behind repository interfaces.
- Authentication, authorization, audit identity, and multi-user RBAC.
- Richer WebSocket/event delivery if SSE becomes insufficient.
- Parallel execution using Git worktrees, including integration/merge lifecycle and re-verification.
- Clean-room verification in isolated environments.
- Advanced multi-invocation discovery.
- Cross-run analytics and uplift history.
