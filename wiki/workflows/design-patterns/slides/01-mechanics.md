# Why Dynamic Workflows?

> The workflow model exists to reduce common failure modes of long, complex single-session tasks.

## The Problems

### 1. Context Degradation
- Long conversations can reach very large contexts.
- Earlier requirements become less prominent.
- Summarization and compaction can weaken the original context.

### 2. Agent Laziness
- Large batches of requested work may not all be completed.
- An agent can claim completion without actually finishing every requested item.

### 3. Self-Preference
- The same agent may create and review its own output.
- This can introduce bias toward its own work.
- Independent reviewers provide a stronger check.

### 4. Goal Drift
- Tool calls, summaries, and long-running interactions can dilute the original objective.
- Important details from the beginning of the task may gradually disappear from active reasoning.

## The Shift

```text
One giant session
        ↓
Many focused agents
        ↓
Independent contexts
        ↓
Controlled synthesis
```

## Core Idea

Dynamic workflows move the architecture from one long-running conversation toward multiple focused execution contexts coordinated by a workflow.

## Navigation

- [← Overview](../presentation.md)
- [Next: Six Patterns →](02-patterns.md)
