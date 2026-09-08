# V5 Architecture Decisions

## AD-001 — Java/Spring specialization
V5 is specifically a Java/Spring uplift workflow. Application migration semantics must not be expressed as TypeScript/Node/Python or other-language rules.

## AD-002 — Dirty new-run gate
A new run with a dirty Git worktree enters HUMAN_GATE. No automatic stash/reset/clean.

## AD-003 — Single bounded discovery
V5 uses one bounded Planner invocation for Discovery. Split discovery is backlog.

## AD-004 — Whole-plan gate
No implementation begins until the complete Planner-produced plan passes Plan Gate.

## AD-005 — Intentional scope overlap
Overlapping Task scopes are allowed only when explicit and dependency-ordered where necessary.

## AD-006 — Sequential execution
V5 executes one Task at a time in the primary workspace. Worktree parallelism is backlog.

## AD-007 — Attempt as execution identity
Every Implementer invocation is exactly one Attempt with a captured baseline and computed delta.

## AD-008 — Workspace authority
Actual Git/workspace state outranks AgentResult claims.

## AD-009 — Independent verification
Every implementation Attempt receives a fresh Verifier invocation.

## AD-010 — Contract integrity
Protected Java/API/application contracts receive deterministic integrity checking. Unauthorized changes cause HUMAN_GATE.

## AD-011 — Orchestrator recovery authority
Agents never select RETRY/REPAIR/REPLAN/BLOCK/HUMAN_GATE/FAIL.

## AD-012 — Durable workflow state
Orchestrator exclusively owns state.json, events.jsonl, lifecycle statuses, and Human Gate state.

## AD-013 — Resume is reconciliation
Resume is distinct from failure recovery. Interrupted Attempts are reconciled rather than blindly rerun.

## AD-014 — Layered security
Prompt, Claude permissions, hooks, and post-execution inspection are complementary enforcement layers. Prompts are not the security boundary.

## AD-015 — Controlled Bash
Implementer has Bash capability subject to layered controls. No universal command allowlist is required for V5.

## AD-016 — AgentRunner abstraction
Claude Code invocation details live behind AgentRunner/ClaudeCodeAdapter. Agents do not spawn agents.

## AD-017 — No automatic Git commit/push
Workflow completion does not imply a Git commit. The user reviews and commits changes separately.

## AD-018 — History preservation
Plans, Attempts, recovery decisions, and events are append-only/history-preserving. Corrections create new records.
