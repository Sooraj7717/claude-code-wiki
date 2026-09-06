# Frontier Documentation — Document Purpose Map

| Document | One-sentence purpose |
|---|---|
| **IMPLEMENTATION-SPEC.md** | Defines the overall Frontier architecture, principles, components, boundaries, and implementation constraints. |
| **AGENT-WORKFLOW-RULES.md** | Defines exactly how Claude Code should construct, invoke, constrain, observe, and terminate agent-based workflow executions. |
| **CLAUDE.md** | Provides Claude Code with the top-level implementation instructions, architectural laws, and rules it must follow while building Frontier. |
| **states/project-states.md** | Defines the legal **project lifecycle states** and the rules governing transitions between them. |
| **states/task-states.md** | Defines the legal **task lifecycle states** and how individual modernization tasks progress through execution. |
| **states/gates.md** | Defines the conditions that must be satisfied before Frontier can advance through critical workflow gates. |
| **workflows/00-lifecycle.md** | Defines the complete end-to-end lifecycle of a Frontier modernization project. |
| **workflows/01-inspect-and-plan.md** | Defines how Frontier inspects a repository and invokes the Planner to produce an executable modernization plan. |
| **workflows/02-execute-task.md** | Defines how Frontier selects, invokes, verifies, and completes an individual Worker task. |
| **workflows/03-recovery.md** | Defines how Frontier handles task failures through retry, repair, replan, blocking, human intervention, or failure. |
| **workflows/04-replan.md** | Defines how Frontier returns to the Planner when the existing plan is no longer sufficient. |
| **workflows/05-human-gate.md** | Defines how Frontier pauses execution for an explicit human decision and subsequently resumes. |
| **workflows/06-completion.md** | Defines how Frontier proves that all required work and project-level acceptance criteria are satisfied before declaring completion. |
| **agents/planner.md** | Defines the Planner agent's responsibilities, inputs, outputs, reasoning boundary, and restrictions. |
| **agents/worker.md** | Defines the Worker agent's responsibilities, execution boundary, write authorization, inputs, outputs, and restrictions. |
| **agents/states.md** | Defines the runtime states and lifecycle semantics applicable to agent invocations. |
| **toolsets/repository-inspector.md** | Defines the deterministic, read-only repository inspection capabilities used to build repository context. |
| **toolsets/git.md** | Defines the Git operations Frontier uses for workspace state, change detection, and diff inspection. |
| **toolsets/java-build.md** | Defines the Java build/test capabilities used for deterministic compilation and validation. |
| **toolsets/openrewrite.md** | Defines how OpenRewrite is exposed as a bounded modernization capability. |
| **toolsets/scope.md** | Defines deterministic enforcement of task read/write scope and detection of unauthorized changes. |
| **toolsets/verification.md** | Defines the deterministic and optional semantic verification capabilities used to validate task results. |
| **orchestrator/ORCHESTRATOR.md** | Defines how the Frontier control plane coordinates states, workflows, agent invocations, validation, and persistence. |
| **orchestrator/recovery-policy.md** | Defines the deterministic rules Frontier uses to select the appropriate recovery operation after failure. |
| **contracts/task.yaml** | Defines the structured schema for a modernization task. |
| **contracts/planner.yaml** | Defines the structured input/output contract for Planner invocations. |
| **contracts/worker.yaml** | Defines the structured input/output contract for Worker invocations. |
| **contracts/verifier.yaml** | Defines the structured contract for verification results. |
| **contracts/evidence.yaml** | Defines the structure used to record observable evidence supporting workflow decisions. |
| **commands/frontier-inspect.md** | Defines the reusable terminal command for repository inspection. |
| **commands/frontier-plan.md** | Defines the reusable terminal command for generating and validating a modernization plan. |
| **commands/frontier-run.md** | Defines the reusable terminal command for executing the Frontier workflow. |
| **commands/frontier-verify.md** | Defines the reusable terminal command for running verification. |
| **commands/frontier-replan.md** | Defines the reusable terminal command for triggering replanning. |
| **commands/frontier-status.md** | Defines the reusable terminal command for viewing current project/task workflow status. |
| **commands/frontier-resume.md** | Defines the reusable terminal command for safely resuming a persisted workflow. |
| **README.md** | Gives developers the concise entry point explaining what Frontier is, how its pieces fit together, and how to use it. |
| **SYSTEM.md** | Describes the complete system model and how Frontier, agents, capabilities, state, workflows, and persistence interact. |
| **Frontier-Agentic-Wording-Map-V1.md** | Standardizes the terminology and phrasing Claude Code should use so that architectural language consistently expresses the intended agentic model. |
| **Frontier-Agent-Workflow-Rules-V1.md** | Converts that agentic model into explicit implementation rules for creating and executing bounded agent invocations inside Frontier. |

## Simplest Documentation Hierarchy

```text
IMPLEMENTATION-SPEC
        ↓
   What Frontier is
        ↓
AGENT-WORKFLOW-RULES
        ↓
How agents actually operate
        ↓
CLAUDE.md
        ↓
What Claude Code must obey
        ↓
States + Workflows + Agents + Toolsets + Contracts
        ↓
Detailed implementation rules
        ↓
Orchestrator + Commands
        ↓
Actual executable system
```

> **Note:** This table reflects the documentation set described in the preceding discussion; it is a purpose map, not a claim that every file was separately uploaded or manually reviewed in the current chat.
