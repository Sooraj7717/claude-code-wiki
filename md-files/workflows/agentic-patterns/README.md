# Agentic Design Patterns

## Purpose

A plain-English reference for the 20 agentic design patterns covered in the source transcript.

The presentation is organized as:
- One parent overview/index.
- One Markdown file per pattern.
- Each pattern keeps the same context used by the HTML presentation:
  - What it means
  - Workflow
  - When to use
  - Good use cases
  - Advantages
  - Problems / limitations
  - Design notes

## Pattern Index

1. Prompt Chaining
2. Routing
3. Parallelization
4. Reflection
5. Tool Use
6. Planning
7. Multi-Agent Collaboration
8. Memory Management
9. Learning & Adaptation
10. Goal Setting & Monitoring
11. Exception Handling & Recovery
12. Human-in-the-Loop
13. RAG / Knowledge Retrieval
14. Inter-Agent Communication
15. Resource-Aware Optimization
16. Reasoning Techniques
17. Evaluation & Monitoring
18. Guardrails & Safety
19. Prioritization
20. Exploration & Discovery

## Overall Architecture

These patterns are reusable building blocks rather than mutually exclusive architectures.

A production workflow can combine:
- Guardrails
- Routing
- Planning
- Tool use / RAG
- Parallel execution
- Reflection / evaluation
- Recovery
- Human review

## Key Principles

- Do not make everything an agent.
- Prefer deterministic code where it is sufficient.
- Validate intermediate outputs.
- Treat failure handling as a first-class capability.
- Treat context as an expensive resource.
- Use human intervention intentionally for high-risk or ambiguous cases.
- Combine patterns only where they provide a concrete benefit.
