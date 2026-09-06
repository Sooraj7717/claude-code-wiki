# Frontier — Agentic Wording & Terminology Mapping V1

## Purpose

This document defines the canonical language for Frontier Markdown files,
Claude Code instructions, agent definitions, workflows, contracts, commands,
and implementation notes.

Its purpose is to remove ambiguity between:

- Frontier as the deterministic orchestrator
- reasoning agents such as Planner and Worker
- deterministic capabilities/toolsets
- workflow state
- agent actions
- agent recommendations
- authoritative state and evidence

The terminology and sentence patterns in this document are normative.

---

# 1. Core Language Rule

Use this mental model:

```text
FRONTIER
decides what is allowed, what happens next, and whether work is accepted.

AGENTS
reason about the work and perform assigned work.

CAPABILITIES / TOOLS
provide deterministic operations.

WORKSPACE / GIT
is authoritative for actual source changes.

EVIDENCE
reports observations/results. It does not change workflow state.
```

The fundamental wording is:

> **Frontier decides what is legal. Agents decide how to perform the work.**

Never describe Frontier itself as an LLM agent.

---

# 2. Actor Vocabulary

| Term | Canonical meaning | Use | Avoid |
|---|---|---|---|
| Frontier | Deterministic workflow controller/orchestrator | state, transitions, validation, gates, recovery | AI agent, reasoning agent, autonomous agent |
| Planner Agent | Reasoning agent that proposes/revises a Task Plan | planning | controller, scheduler |
| Worker Agent | Reasoning agent that executes an assigned Task | implementation | autonomous worker pool |
| Verifier | Verification capability boundary | checks and evidence | always call it an agent |
| Repository Inspector | Deterministic read-only capability | repository inspection | Discovery Agent |
| RecoveryPolicy | Deterministic recovery decision policy | failure handling | Recovery Agent |
| Toolset | Collection of executable capabilities | Git, build, OpenRewrite, verification | agent |
| Workspace | Actual repository being modified | source of truth for changes | agent state |
| Evidence | Result/observation supporting a decision | facts, logs, diffs, checks | authoritative state |

---

# 3. Agentic vs Non-Agentic Wording

When describing a reasoning agent, use **action-oriented language**.

### Preferred

```text
The Planner Agent analyzes RepositoryContext and produces a Task Plan.

The Worker Agent receives one authorized Task and performs the required changes.

The Worker Agent may read outside its write scope but must not modify outside it.

The Worker Agent returns evidence describing the work performed.

The Planner Agent may recommend a revised plan when the current plan is invalid.
```

### Avoid

```text
The Planner is responsible for planning.
The Worker is used for implementation.
The Worker handles code changes.
The agent interacts with the repository.
The agents collaborate.
```

The avoided wording is too vague for an executable agent specification.

---

# 4. Required Agent Sentence Pattern

For every reasoning agent, describe behavior using:

```text
ROLE
→ INPUT
→ ACTION
→ CONSTRAINT
→ OUTPUT
```

Example:

```text
ROLE:
You are the Frontier Worker Agent.

INPUT:
You receive one authorized Task, its execution context,
and its explicit write scope.

ACTION:
Inspect the relevant code, perform the required modernization work,
run appropriate tools, and validate the result where possible.

CONSTRAINT:
Do not modify files outside the authorized write scope.
Do not mutate Frontier workflow state.
Do not invoke another Frontier agent directly.

OUTPUT:
Return a WorkerResult containing status, observations, errors,
reported changes, and evidence.
```

---

# 5. Planner Language

Use:

> **Planner proposes. Frontier validates and accepts.**

Preferred:

```text
The Planner Agent converts RepositoryContext and the modernization objective
into an explicit executable Task Plan.
```

Agentic form:

```text
You are the Planner Agent.

Analyze the supplied RepositoryContext and modernization objective.

Produce an explicit Task Plan containing:
- Tasks
- dependencies
- authorized write scopes
- verification requirements
- assumptions
- expected outcomes

Do not modify the repository.
Do not mutate Frontier state.
Do not execute Tasks.
```

Planner verbs:

```text
analyze
infer
decompose
propose
prioritize
identify
recommend
revise
explain
```

Planner must not:

```text
execute
modify
commit
approve completion
change task state
expand worker scope
override Frontier policy
```

---

# 6. Worker Language

Use:

> **Worker performs the work. Frontier decides whether the work is accepted.**

Preferred:

```text
You are the Frontier Worker Agent.

Execute the assigned Task.

First inspect the relevant repository context.
Then perform the required changes.
Use authorized toolsets where appropriate.
Keep all modifications within the assigned write scope.
Run the required checks.
Return the observed result and supporting evidence.
```

Worker verbs:

```text
inspect
read
analyze
modify
create
delete
run
test
build
refactor
transform
validate
report
recommend
```

Worker must not:

```text
change Frontier state
change Task state
expand its own write scope
assign another Worker
invoke the Planner directly
invoke the Verifier as a controller
declare a Task COMPLETE
declare the project COMPLETE
override a gate
rewrite completed Tasks
```

A Worker can report success. It cannot make the Task COMPLETE.

---

# 7. Verifier Language

Use:

> **Verifier reports. Frontier decides.**

Preferred:

```text
The Verifier evaluates the supplied workspace state and returns verification evidence.

The Verifier reports whether the required checks passed.

The Verifier may classify failures.

Frontier applies the completion gate using the verification result.
```

Avoid:

```text
The Verifier approves the Task.
The Verifier completes the Task.
The Verifier decides whether the workflow proceeds.
The Verifier controls the Worker.
```

---

# 8. Deterministic Capability Language

Do not describe deterministic capabilities as agents.

## Repository Inspector

Preferred:

```text
Repository Inspector reads the repository and produces RepositoryContext.
```

It may:

```text
read
scan
extract
summarize
detect
report
```

It does not:

```text
create Tasks
modify source code
change workflow state
decide the modernization strategy
```

Use **Repository Inspector**, not **Discovery Agent**.

## RecoveryPolicy

Preferred:

```text
RecoveryPolicy evaluates failure evidence and maps it to a permitted
recovery operation.
```

It does not independently control workflow state.

---

# 9. Frontier Language

Frontier should use **control-plane verbs**, not reasoning verbs.

Frontier may:

```text
initialize
load
persist
validate
check
calculate
select
transition
gate
authorize
reject
accept
record
recover
pause
resume
reconcile
```

Preferred:

```text
Frontier validates the plan.
Frontier calculates Task readiness.
Frontier selects the next READY Task.
Frontier invokes the Worker.
Frontier inspects the actual diff.
Frontier applies the completion gate.
Frontier selects the recovery action.
Frontier persists the resulting state.
```

Avoid:

```text
Frontier reasons about the repository.
Frontier understands the code.
Frontier decides how to modernize the code.
Frontier writes the code.
Frontier collaborates with the agents.
```

---

# 10. State Language

Distinguish **state** from **action**.

## Persistent states

```text
INITIALIZING
DISCOVERING
PLANNING
EXECUTING
COMPLETING
COMPLETE

BLOCKED
HUMAN_GATE
FAILED
```

Task states:

```text
BLOCKED
READY
EXECUTING
VERIFYING
COMPLETE
```

## Actions

```text
select
start
execute
verify
accept
retry
repair
replan
block
pause
resume
fail
```

Do not describe RETRY as a persistent state when it is a recovery operation.

Use:

```text
Frontier applies the RETRY recovery operation and starts a new attempt.
```

Canonical rule:

> **States describe durable workflow status. Recovery operations describe what Frontier does in response to failure.**

---

# 11. State Transition Wording

Always use:

```text
ACTOR + CONDITION + ACTION + RESULT
```

Preferred:

```text
When all Task dependencies are COMPLETE, Frontier may transition the Task
from BLOCKED to READY.

When Frontier starts a Task attempt, it transitions the Task from READY
to EXECUTING.

After Worker execution returns, Frontier transitions the Task to VERIFYING.

The Task becomes COMPLETE only when the completion gate succeeds.
```

Avoid:

```text
The Task becomes ready when dependencies are done.
The Worker completes the Task.
Verification moves the Task to complete.
The agent decides the next state.
```

---

# 12. Workflow Language

Every workflow should explicitly state:

```text
WHO acts?
WHAT input is used?
WHAT action occurs?
WHAT constraints apply?
WHAT result is produced?
WHO controls the next transition?
```

Recommended structure:

```text
## Step N — <Action>

Actor:
Frontier / Planner / Worker / Verifier / Capability

Input:
<explicit input>

Action:
<imperative action>

Constraints:
<what must not happen>

Result:
<returned result/evidence>

Next:
<Frontier-controlled transition>
```

Example:

```text
## Step 3 — Execute Task

Actor:
Worker Agent

Input:
One READY Task and its authorized execution context.

Action:
Execute the Task within the assigned write scope.

Constraints:
Do not modify files outside the write scope.
Do not mutate Frontier state.
Do not invoke another agent directly.

Result:
WorkerResult plus workspace changes.

Next:
Frontier inspects the actual diff and performs scope validation.
```

---

# 13. Receives vs Reads vs Uses

Use these terms precisely.

| Word | Meaning | Example |
|---|---|---|
| receives | data explicitly supplied to the component | Worker receives TaskContext |
| reads | component actively inspects/retrieves information | Worker reads source files |
| uses | component consumes a capability/value | Worker uses OpenRewrite |
| produces | explicit output is generated | Planner produces PlanResult |
| returns | output crosses a call boundary | Worker returns WorkerResult |

Avoid using generic "gets" when one of these precise verbs applies.

---

# 14. Request vs Command

## Request

An agent asks Frontier for something it cannot directly perform.

```text
Worker returns a capability_request when required information is unavailable.
```

A request is not automatically authorized.

## Command

A deterministic instruction issued by Frontier or a reusable CLI operation.

```text
frontier run <task-id>
```

Do not describe arbitrary agent output as a command.

---

# 15. Recommendation vs Decision

This distinction is mandatory.

### Agent

```text
recommends
proposes
classifies
reports
```

### Frontier

```text
decides
accepts
rejects
transitions
authorizes
gates
```

Example:

```text
The Worker recommends REPAIR because the build failed after a localized change.

Frontier evaluates RecoveryPolicy and selects REPAIR.
```

Never write:

```text
The Worker decides to repair the Task.
```

---

# 16. Success vs Completion

These are different concepts.

## Worker success

Means:

```text
The Worker completed its execution attempt without reporting an execution failure.
```

It does not mean:

```text
Task COMPLETE
```

## Verification success

Means:

```text
The required verification checks passed.
```

It does not independently mean:

```text
Task COMPLETE
```

## Task completion

Means:

```text
Frontier's completion gate accepted the Worker result,
actual workspace changes, scope validation, and required verification.
```

Canonical sentence:

> **Worker success is evidence. Task completion is a Frontier decision.**

---

# 17. Changed-Files Language

Never treat Worker-reported changed files as authoritative.

Preferred:

```text
The Worker reports changed files as evidence.

Frontier obtains the authoritative change set from the actual workspace/Git diff.

Frontier validates the actual change set against the authorized write scope.
```

Canonical hierarchy:

```text
Workspace/Git diff
        ↓
authoritative actual changes

WorkerResult
        ↓
reported evidence
```

---

# 18. Scope Language

Use:

```text
authorized write scope
```

for what a Worker may modify.

Use:

```text
read access
```

for what it may inspect.

Preferred:

```text
The Worker may read broadly enough to understand the Task,
but may modify only files within the authorized write scope.
```

Avoid:

```text
The Worker should mostly stay within scope.
```

Scope is a hard invariant.

Use:

```text
Frontier rejects the attempt when actual changes fall outside the authorized scope.
```

---

# 19. Agent Communication Language

Frontier uses **shared-state mediation**, not peer-to-peer collaboration.

Preferred:

```text
Agent → Frontier → State → Agent
```

or:

```text
Agent → Result/Evidence → Frontier → Next Agent
```

Avoid:

```text
Planner collaborates with Worker.
Worker delegates to Verifier.
Verifier asks Worker to fix the code.
Planner hands work directly to Worker.
```

Canonical statement:

> **Agents cannot directly control other agents.**

Information moving between agents must pass through Frontier-controlled context/state.

---

# 20. Context Language

Prefer explicit context names:

```text
RepositoryContext
TaskContext
ExecutionContext
VerificationContext
RecoveryContext
ProjectState
TaskState
Plan
Evidence
WorkerResult
VerifierResult
```

Avoid vague terms such as:

```text
context
agent memory
shared information
system knowledge
workflow data
```

when a precise object can be named.

---

# 21. Toolset Language

Toolsets are capabilities, not agents.

Preferred:

```text
The Worker uses the Git toolset to inspect the workspace.

The Worker uses the Java Build toolset to run tests.

Frontier uses Scope Enforcement to validate actual changes.
```

Avoid:

```text
Git Agent
Build Agent
Scope Agent
OpenRewrite Agent
```

unless a real reasoning agent has intentionally been introduced.

---

# 22. Command Language

Reusable commands should express operator intent:

```text
frontier inspect
frontier plan
frontier run
frontier verify
frontier replan
frontier status
frontier resume
```

Each command description should contain:

```text
Purpose
Inputs
Preconditions
Action
Output
Failure behavior
```

Commands invoke Frontier. They should not contain hidden workflow policy or agent reasoning.

---

# 23. Recovery Language

Recovery is Frontier-controlled policy.

Canonical operations:

```text
RETRY
REPAIR
REPLAN
BLOCK
HUMAN_GATE
FAIL
```

Preferred:

```text
The Worker reports a recoverable failure.

Frontier records the failure evidence.

RecoveryPolicy evaluates the failure classification and attempt history.

Frontier selects the permitted recovery operation.

Frontier executes the selected operation through the normal workflow boundary.
```

Avoid:

```text
The Worker decides whether to retry.
The agent enters repair mode.
The Verifier tells the Worker what to do next.
```

---

# 24. Replanning Language

Replanning is a controlled revision of future work.

Preferred:

```text
The Planner proposes a revised plan.

Frontier validates the revised DAG and scopes.

Completed Tasks remain preserved.

Frontier accepts the revised plan only when it satisfies the plan invariants.
```

Avoid:

```text
The Planner rewrites the workflow.
The Planner resets the project.
The Planner starts over.
```

unless an explicit reset operation exists.

---

# 25. Human Gate Language

Preferred:

```text
Frontier pauses the workflow at HUMAN_GATE.

Frontier persists the gate reason and requested decision.

A human provides the decision.

Frontier validates the decision and resumes or terminates the workflow.
```

Avoid:

```text
The agent asks the user for permission.
The Worker waits for approval.
```

The human gate belongs to the workflow controller.

---

# 26. Persistence Language

Persistence describes Frontier state, not agent memory.

Preferred:

```text
Frontier persists ProjectState, the accepted Plan, and attempt evidence.

On resume, Frontier loads persisted state and reconciles it with the actual workspace.
```

Avoid:

```text
The agent remembers its previous work.
The agent session is persisted.
Agents maintain long-term memory.
```

V1 does not require persistent agent sessions.

---

# 27. Verification Language

Use the layered model:

```text
actual diff
    ↓
scope validation
    ↓
deterministic checks
    ↓
semantic verification when necessary
    ↓
completion gate
```

Preferred:

```text
Frontier first validates the actual diff against the authorized scope.

Frontier runs deterministic checks.

If deterministic checks are insufficient, Frontier may invoke semantic verification.

Frontier then applies the completion gate.
```

Avoid:

```text
The Verifier decides whether the code is good.
Every Task is checked by an LLM.
The Worker validates its own completion.
```

---

# 28. Contract Language

Every agent contract should use:

```text
INPUT
ACTION
CONSTRAINTS
OUTPUT
FAILURE
```

Example:

```text
INPUT
- Task
- TaskContext
- authorized write scope

ACTION
- inspect
- execute
- validate where possible
- report

CONSTRAINTS
- no state mutation
- no scope expansion
- no direct agent-to-agent control

OUTPUT
- WorkerResult
- evidence
- reported changes

FAILURE
- execution failure
- blocked execution
- capability request
```

---

# 29. Forbidden Ambiguity Patterns

Treat these phrases as review triggers:

```text
"the agent handles..."
"the agent manages..."
"the agent decides..."
"the agent completes..."
"the system figures out..."
"the system understands..."
"the agents collaborate..."
"the Worker controls..."
"the Planner assigns..."
"the Verifier approves..."
"Frontier reasons..."
"Frontier understands..."
"Frontier decides how..."
"the workflow automatically knows..."
"the agent can do anything required..."
"the agent has full access..."
"the agent may modify whatever is necessary..."
```

Replace them with explicit actor/action/authority wording.

---

# 30. Recommended Replacements

| Ambiguous | Canonical |
|---|---|
| Agent handles task | Worker executes the assigned Task |
| Agent completes task | Worker returns a result; Frontier applies the completion gate |
| Agent decides next step | Frontier selects the next workflow transition |
| Planner creates workflow | Planner proposes a Task Plan; Frontier validates and accepts it |
| Worker decides to retry | Worker reports failure; Frontier applies RecoveryPolicy |
| Verifier approves task | Verifier returns verification evidence; Frontier applies the completion gate |
| Agents collaborate | Agents exchange information through Frontier-controlled state/context |
| Discovery Agent | Repository Inspector |
| Recovery Agent | RecoveryPolicy |
| Agent memory | persisted workflow state / attempt evidence |
| Shared agent state | Frontier-controlled shared workflow state |
| Agent scope | authorized write scope |
| Agent changed files | Worker-reported changed files |
| Actual changed files | workspace/Git authoritative change set |
| Agent can modify | Worker is authorized to modify |
| Agent should avoid | Frontier rejects / policy forbids |
| Retry state | RETRY recovery operation |
| Agent asks for approval | Frontier enters HUMAN_GATE |
| Agent plans implementation | Planner proposes Tasks |
| System decides code is correct | Verification passes and Frontier accepts the completion gate |
| Agent-to-agent handoff | Frontier-mediated context handoff |
| Agent invokes another agent | Frontier invokes the next capability/agent |

---

# 31. Canonical End-to-End Narrative

Use this sequence when describing the Frontier lifecycle:

```text
1. Frontier initializes the Project.

2. Repository Inspector reads the repository and produces RepositoryContext.

3. Frontier provides RepositoryContext and the modernization objective to the Planner.

4. Planner analyzes the context and proposes a Task Plan.

5. Frontier validates the Task Plan, including the DAG, dependencies,
   write scopes, and conflicts.

6. Frontier selects a READY Task.

7. Frontier provides the Task and authorized execution context to the Worker.

8. Worker inspects the relevant code and performs the Task within its
   authorized write scope.

9. Worker returns a WorkerResult and evidence.

10. Frontier inspects the actual workspace/Git diff.

11. Frontier validates the actual changes against the authorized scope.

12. Frontier runs deterministic verification.

13. Frontier invokes semantic verification only when deterministic checks
    are insufficient.

14. Frontier applies the completion gate.

15. If the gate fails, Frontier applies RecoveryPolicy.

16. Recovery may result in RETRY, REPAIR, REPLAN, BLOCK, HUMAN_GATE, or FAIL.

17. Completed Tasks remain preserved during replanning.

18. Frontier persists workflow state at meaningful boundaries.

19. After all required Tasks are complete, Frontier performs project-level
    verification and acceptance.

20. Frontier marks the Project COMPLETE only when project completion criteria
    are satisfied.
```

---

# 32. Canonical One-Line Definitions

```text
Frontier:
Deterministic workflow controller for agent-mediated repository modernization.

Planner:
Reasoning agent that proposes executable Task Plans.

Worker:
Reasoning agent that executes one authorized Task.

Verifier:
Capability boundary that produces verification evidence.

Repository Inspector:
Deterministic read-only capability that produces RepositoryContext.

RecoveryPolicy:
Deterministic policy that maps failure evidence to permitted recovery operations.

Task:
Explicit unit of executable modernization work with dependencies,
write scope, and verification requirements.

Task Plan:
Explicit DAG of executable Tasks accepted by Frontier.

Evidence:
Observed information produced by agents or capabilities; not authoritative workflow state.

Completion Gate:
Deterministic Frontier rule that decides whether a Task may become COMPLETE.

Authorized Write Scope:
Set of files/resources a Worker is permitted to modify for a Task.

Workspace/Git:
Authoritative source of actual repository changes.
```

---

# 33. Markdown Rule for Claude Code

When writing or modifying Frontier Markdown files:

```text
1. Name the actor.
2. Use an explicit action verb.
3. Identify the input.
4. State the authority/constraint.
5. Identify the output.
6. State who controls the next transition.
```

Good:

```text
Frontier provides the Worker with one READY Task and its authorized write scope.
The Worker executes the Task and returns a WorkerResult.
Frontier validates the actual workspace diff and decides whether the Task
passes the completion gate.
```

Weak:

```text
The agent works on the task and then the system verifies it.
```

---

# 34. Final Language Principle

Frontier documentation must make these questions impossible to misunderstand:

```text
WHO ACTS?
    → Frontier / Planner / Worker / Verifier / Capability

WHO DECIDES?
    → Frontier

WHAT IS AUTHORITATIVE?
    → Frontier state for workflow
    → accepted Plan for intended work
    → Workspace/Git diff for actual changes

WHAT DO AGENTS PROVIDE?
    → reasoning
    → execution
    → recommendations
    → evidence
```

If a sentence makes these boundaries unclear, rewrite it.

> **Make agents agentic in their instructions, but never make Frontier agentic in its control model.**
