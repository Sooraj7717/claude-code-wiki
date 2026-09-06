# Prompt Template — Convert an Implementation Specification & Architecture Brief into Detailed Markdown Documentation

You are an expert software architect and technical documentation engineer.

I will provide an **Implementation Specification & Architecture Brief** for a software system.

Your task is to transform it into a **coherent, implementation-ready Markdown documentation set** that Claude Code can use to build the system.

The goal is **not** to rewrite the specification into many arbitrary files.

The goal is to convert the specification into a **small, logically separated documentation system**, where each Markdown file has one clear responsibility and the documents collectively remove implementation ambiguity.

---

# 1. Source of Truth

Treat the supplied **Implementation Specification & Architecture Brief** as the primary source of truth.

You must:

- preserve its architecture and terminology;
- preserve its design intent;
- preserve its constraints and non-goals;
- preserve important implementation decisions;
- preserve stated state machines, workflows, contracts, and boundaries;
- avoid silently changing architectural decisions;
- avoid introducing technologies or abstractions that are not justified by the source.

If something is not defined by the specification:

- do not invent it silently;
- mark it as **TBD**, **implementation choice**, or **requires clarification**, as appropriate;
- only make an inference when it is necessary to make the documentation executable;
- clearly label inferred material.

---

# 2. Documentation Objective

Create documentation that allows Claude Code to answer, without ambiguity:

1. What is the system?
2. What are its architectural boundaries?
3. What components exist?
4. What responsibilities belong to each component?
5. Which components are deterministic?
6. Which components are agentic/reasoning-oriented?
7. How do components interact?
8. What states exist?
9. What transitions are legal?
10. What workflows exist?
11. When are agents invoked?
12. What context does each agent receive?
13. What capabilities/tools can each agent use?
14. What is each agent authorized to read/write?
15. What does each agent return?
16. Who owns workflow decisions?
17. How are failures handled?
18. How is verification performed?
19. What is persisted?
20. What commands/actions are exposed to developers?
21. What must Claude Code NOT implement?
22. What constitutes completion?

The resulting documentation should describe an **executable system**, not merely an architectural concept.

---

# 3. Documentation Design Principle

Use this principle throughout:

> **Separate "what the system is", "how the system behaves", and "how each part is implemented".**

Do not put everything into one giant Markdown file.

Do not create a file merely because a heading exists in the source specification.

Create a separate document only when the information represents a meaningful implementation boundary.

---

# 4. Recommended Documentation Structure

Use the following structure as the default starting point.

Adapt it to the source specification rather than forcing content into irrelevant files.

```text
README.md

CLAUDE.md

SYSTEM.md
IMPLEMENTATION-SPEC.md
AGENT-WORKFLOW-RULES.md

states/
    project-states.md
    task-states.md
    gates.md

workflows/
    00-lifecycle.md
    01-inspect-and-plan.md
    02-execute-task.md
    03-recovery.md
    04-replan.md
    05-human-gate.md
    06-completion.md

agents/
    planner.md
    worker.md
    states.md

toolsets/
    repository-inspector.md
    git.md
    java-build.md
    openrewrite.md
    scope.md
    verification.md

orchestrator/
    ORCHESTRATOR.md
    recovery-policy.md

contracts/
    task.yaml
    planner.yaml
    worker.yaml
    verifier.yaml
    evidence.yaml

commands/
    <command>.md
```

Do not create every file automatically.

Only create files whose contents are supported and useful.

---

# 5. Purpose of Each Documentation Layer

Use the following conceptual hierarchy.

```text
IMPLEMENTATION-SPEC
        ↓
What the system is and why it is designed this way
        ↓
AGENT-WORKFLOW-RULES
        ↓
How agentic execution is constructed
        ↓
CLAUDE.md
        ↓
What Claude Code must obey
        ↓
States / Workflows / Agents / Toolsets / Contracts
        ↓
Detailed executable rules
        ↓
Orchestrator / Commands
        ↓
How the implementation is operated
```

The documentation must maintain these boundaries.

---

# 6. README.md

Create a concise developer entry point.

It should explain:

- what the system does;
- the core architecture;
- the major components;
- how the documentation is organized;
- where implementation should begin;
- the primary commands/workflows;
- the most important architectural rule.

Do not duplicate the entire specification.

---

# 7. SYSTEM.md

Create a system-level view explaining:

- system purpose;
- architectural model;
- major components;
- component responsibilities;
- control flow;
- data/state flow;
- agent boundaries;
- deterministic vs reasoning-oriented responsibilities;
- persistence;
- verification;
- recovery;
- major invariants.

This should be understandable without reading every detailed document.

---

# 8. IMPLEMENTATION-SPEC.md

Preserve the authoritative implementation specification.

It should capture:

- architecture;
- design principles;
- implementation constraints;
- component boundaries;
- non-goals;
- performance requirements;
- persistence model;
- testing expectations;
- definition of done.

Do not dilute this document by turning every detail into another file.

Other documents may reference it.

---

# 9. CLAUDE.md

Create implementation instructions specifically for Claude Code.

It must contain explicit rules such as:

- architectural laws;
- forbidden architectural changes;
- state ownership;
- agent ownership;
- workspace authority;
- scope restrictions;
- persistence rules;
- testing expectations;
- dependency rules;
- implementation priorities;
- instructions to prefer simplicity;
- instructions not to introduce unsupported abstractions.

Use imperative language.

Examples:

```text
DO:
- Keep Frontier deterministic.
- Route workflow transitions through Frontier.
- Validate actual workspace changes.
- Keep agent capabilities explicitly bounded.

DO NOT:
- Add direct agent-to-agent control.
- Add distributed orchestration.
- Add automatic scope expansion.
- Introduce an agent where deterministic logic is sufficient.
```

---

# 10. AGENT-WORKFLOW-RULES.md

This document is mandatory whenever the architecture contains agents.

It must explicitly define:

- Agent Definition;
- Agent Role;
- Agent Invocation;
- Invocation Context;
- Capability Binding;
- Authorization Scope;
- Agent Result;
- Evidence;
- Frontier Validation;
- State Transition;
- Agent termination;
- bounded agent loops;
- agent isolation;
- agent-to-agent communication rules;
- context requests;
- capability requests;
- recovery;
- next-agent selection.

The canonical model should be:

```text
Agent Definition
      ↓
Agent Invocation
      ↓
Bound Execution Context
      ↓
Agent Execution
      ↓
Agent Result
      ↓
Frontier Validation
      ↓
State Transition
```

Make it explicit that:

> Agents perform bounded work. The orchestrator owns workflow control.

Do not allow wording that implies autonomous workflow ownership unless the source specification explicitly requires it.

---

# 11. Agent Documentation

For every reasoning-oriented agent, create a dedicated document.

Each agent document should define:

```text
Purpose
Role
When Invoked
Inputs
Context
Capabilities
Read Scope
Write Scope
Responsibilities
Non-Responsibilities
Expected Output
Failure Modes
Termination
Interaction with Frontier
```

Clearly distinguish:

```text
Agent recommendation
```

from:

```text
Frontier decision
```

Clearly distinguish:

```text
Agent result
```

from:

```text
Workflow state
```

---

# 12. State Documentation

Extract explicit state machines into dedicated documents.

For each state machine define:

- states;
- meaning of each state;
- legal transitions;
- transition owner;
- entry conditions;
- exit conditions;
- failure transitions;
- persistence requirements.

Use diagrams/tables where useful.

Never allow documentation to imply that agents directly mutate authoritative workflow state unless explicitly required.

---

# 13. Workflow Documentation

Every significant workflow should have a dedicated Markdown document.

Each workflow must define:

```text
Purpose
Entry Condition
Initial State
Preconditions
Actors/Agents
Context
Capabilities
Authorization
Steps
Validation
Verification
Success Path
Failure Path
Recovery
Persistence
State Transitions
Exit Conditions
Next Workflow
```

Use a consistent structure across all workflows.

For agent-backed workflows explicitly show:

```text
Frontier
   ↓
Agent Invocation
   ↓
Agent Result
   ↓
Validation
   ↓
State Transition
```

Do not describe workflows merely as prose.

They must be executable enough that Claude Code can implement them.

---

# 14. Toolset / Capability Documentation

Create a dedicated document for each meaningful capability boundary.

Each capability document should define:

```text
Purpose
Operations
Inputs
Outputs
Preconditions
Side Effects
Authorization
Failure Modes
Determinism
Agent Access
Frontier Access
Restrictions
```

Clearly identify whether the capability:

- is deterministic;
- mutates the repository;
- reads the repository;
- is available to Planner;
- is available to Worker;
- is controlled directly by Frontier.

Do not turn every utility function into a "toolset".

---

# 15. Contract Documentation

Every important boundary should have an explicit structured contract.

Document:

```text
Input
Output
Required Fields
Optional Fields
Validation Rules
Error Representation
Authority
Examples
```

For agent boundaries, prefer explicit contracts such as:

```text
PlannerContext
PlannerResult

WorkerContext
WorkerResult

VerifierInput
VerifierResult
```

Do not rely on free-form agent output for workflow control.

---

# 16. Orchestrator Documentation

The orchestrator document must explain:

- what Frontier owns;
- how workflow execution proceeds;
- how eligible tasks are selected;
- how agents are invoked;
- how results are validated;
- how state transitions occur;
- how recovery is selected;
- how persistence is performed;
- how execution resumes;
- how completion is determined.

The orchestrator must remain the control plane.

Do not allow agents to become implicit orchestrators.

---

# 17. Recovery Documentation

Document recovery as an explicit decision model.

At minimum distinguish:

```text
RETRY
REPAIR
REPLAN
BLOCK
HUMAN_GATE
FAIL
```

For each define:

- when it applies;
- who decides;
- what state changes;
- what context is preserved;
- what gets persisted;
- what happens next.

Do not use "retry" as a generic solution to every failure.

---

# 18. Command Documentation

For each reusable terminal command, document:

```text
Purpose
Syntax
Inputs
Preconditions
Workflow Started
State Effects
Agent Invocation
Output
Failure Behavior
Examples
```

Commands should be thin entry points into Frontier workflows, not alternative orchestration mechanisms.

---

# 19. Language Rules

Use precise implementation language.

Prefer:

```text
Frontier invokes the Worker.
```

over:

```text
The Worker handles the task.
```

Prefer:

```text
The Planner proposes a plan.
```

over:

```text
The Planner decides the plan.
```

Prefer:

```text
Frontier determines the resulting task state.
```

over:

```text
The Worker marks the task complete.
```

Prefer:

```text
Frontier passes the Worker result to the next workflow operation.
```

over:

```text
The agents communicate.
```

Prefer:

```text
The Worker is authorized to write within the task scope.
```

over:

```text
The Worker can modify the necessary files.
```

Prefer:

```text
The workspace/Git diff is authoritative for actual changes.
```

over:

```text
The Worker reports which files changed.
```

---

# 20. Agentic vs Deterministic Language

Explicitly distinguish:

### Agentic

Used for:

- interpretation;
- planning;
- semantic reasoning;
- code transformation;
- semantic analysis.

### Deterministic

Used for:

- state transitions;
- DAG validation;
- scope validation;
- persistence;
- Git diff inspection;
- compilation;
- command execution;
- workflow eligibility;
- recovery policy;
- completion gates.

Do not describe deterministic components as agents merely because they participate in an agentic workflow.

---

# 21. Avoid Documentation Fragmentation

Do not create unnecessary documents.

Use this test:

> Does this topic represent a distinct implementation responsibility, lifecycle, boundary, contract, or workflow?

If **no**, keep it in an existing document.

If **yes**, consider a separate document.

The objective is:

```text
Maximum clarity
with
Minimum documentation fragmentation
```

Do not optimize for the number of Markdown files.

---

# 22. Cross-Document Consistency

After generating the documentation, perform a consistency pass.

Check for:

```text
[ ] Component names are consistent
[ ] Agent names are consistent
[ ] State names are consistent
[ ] Workflow names are consistent
[ ] Contract names are consistent
[ ] Capability names are consistent
[ ] State ownership is consistent
[ ] Agent boundaries are consistent
[ ] Authorization rules are consistent
[ ] Recovery semantics are consistent
[ ] Persistence semantics are consistent
[ ] No document contradicts IMPLEMENTATION-SPEC
[ ] No document silently introduces architecture
```

If contradictions exist, identify them rather than silently choosing one interpretation.

---

# 23. Traceability

Every significant architectural requirement should be traceable to at least one documentation location.

Create a traceability section or matrix if useful:

```text
Requirement
    ↓
Architecture Rule
    ↓
Workflow / State / Agent / Contract
    ↓
Implementation Responsibility
```

This is especially important for:

- state ownership;
- agent authorization;
- write scope;
- verification;
- recovery;
- persistence;
- completion criteria.

---

# 24. Anti-Overengineering Rules

The generated documentation must not accidentally encourage over-engineering.

Unless explicitly required by the source specification, do not introduce:

- microservices;
- distributed workers;
- message brokers;
- event sourcing;
- workflow engines;
- agent registries;
- agent pools;
- schedulers;
- distributed locks;
- capability marketplaces;
- persistent autonomous agents;
- dynamic agent discovery;
- automatic dependency inference;
- speculative parallel execution;
- complex reconciliation engines;
- multi-tenant infrastructure;
- high-availability infrastructure.

The documentation must preserve the intended implementation scale.

---

# 25. Final Architecture Review

Before finalizing the documentation, perform a final architecture review.

Answer:

### Architecture
- Is every major component clearly defined?
- Is ownership unambiguous?
- Are deterministic and agentic responsibilities separated?

### Agents
- Is every agent explicitly defined?
- Is every invocation bounded?
- Is every capability explicit?
- Is every write scope explicit?
- Can an agent accidentally control workflow state?

### Workflow
- Can Claude Code determine exactly what happens next?
- Are state transitions explicit?
- Are recovery paths explicit?
- Are completion conditions explicit?

### Implementation
- Can Claude Code implement the system without inventing missing architecture?
- Are contracts sufficiently explicit?
- Are commands sufficiently explicit?
- Are persistence boundaries clear?

### Complexity
- Did documentation introduce unnecessary abstractions?
- Did any deterministic responsibility become an unnecessary agent?
- Did any simple workflow become an artificial framework?

---

# 26. Required Output

Produce:

```text
1. Documentation directory tree
2. All Markdown documentation files
3. Any YAML/JSON contracts required by the specification
4. Cross-document references
5. Documentation consistency review
6. List of assumptions/TBDs
7. Documentation purpose map
```

For every generated document, provide:

```text
Filename
Purpose
Primary Audience
Depends On
Defines
Does Not Define
```

---

# 27. Documentation Purpose Map

Finally create:

```text
DOCUMENTATION-PURPOSE-MAP.md
```

with a table:

| Document | One-sentence purpose |
|---|---|
| README.md | ... |
| CLAUDE.md | ... |
| SYSTEM.md | ... |
| IMPLEMENTATION-SPEC.md | ... |
| AGENT-WORKFLOW-RULES.md | ... |
| ... | ... |

The purpose map must make it immediately obvious why each file exists.

---

# 28. Final Principle

The generated documentation must satisfy this principle:

> **The Implementation Specification explains the intended system; the detailed Markdown documentation decomposes that intent into explicit, bounded, implementation-ready responsibilities without changing the architecture.**

Do not maximize the number of documents.

Maximize **clarity, traceability, implementation precision, and architectural consistency**.

---

## Source Specification

Use the following Implementation Specification & Architecture Brief as the source of truth:

```text
    PRIMARY SOURCE
    └── Frontier — Claude Code Implementation Brief V1.md

    OPTIONAL REFERENCE
    ├── Frontier-Agentic-Wording-Map-V1.md
    └── Frontier-Agent-Workflow-Rules-V1.md
```

Now analyze the source, derive the documentation boundaries, generate the documentation set, and perform the consistency/ambiguity review described above.