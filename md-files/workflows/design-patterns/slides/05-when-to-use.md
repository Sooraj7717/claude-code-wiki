# When to Use Dynamic Workflows

> The goal is not maximum agent count; it is the simplest architecture that reliably reaches the desired outcome.

## Use a Workflow When

- The task is large or complex.
- Work can be split into independent parts.
- Independent verification matters.
- There are many candidates to rank or filter.
- The investigation has an unknown path to success.
- You need repeated attempts until a meaningful condition is satisfied.

## Don't Use One When

- The task is trivial.
- A single focused agent can reliably finish it.
- Extra agents add more cost than value.
- Orchestration creates unnecessary complexity.

## Decision Rule

> **Complexity should earn its place.**

Use dynamic workflows when isolation, parallelism, independent judgment, breadth, or iterative verification materially improves the result.

## Final Mental Model

| Situation | Preferred Approach |
|---|---|
| Simple task | Single agent |
| Complex task | Orchestrated workflow |
| High-quality / verification-heavy output | Independent verification |
| Large search space | Generate/filter or tournament |
| Unknown path to success | Loop until completion condition |

## Navigation

- [← Sharing](04-sharing.md)
- [Back to Overview →](../presentation.md)
