# 1. Prompt Chaining← Back to all patternsPattern 1 of 20

> Source-derived summary from the supplied agentic design-pattern transcript.

Prompt Chaining
Break a large task into sequential steps; validate each step before passing its output onward.
All patternsCurrent
In plain English
Break a large task into sequential steps; validate each step before passing its output onward.
When to use it
- Complex multi-step processing.
- ETL.
- documents.
- code and content..
Typical workflow
Input / Goal
→Analyze
→Execute
→Validate
→Continue / Retry / Escalate
Advantages- Modular; easier validation.
- debugging..
Risks / limitations- Context explosion.
- error propagation.
- cost and latency..
Architecture context
This pattern is best treated as a reusable building block. It can be combined with routing, planning, tools, RAG, evaluation, recovery, guardrails and human review depending on the workflow.
Source: supplied transcript summarizing agentic design patterns. This page preserves the transcript's framing rather than adding external claims.
