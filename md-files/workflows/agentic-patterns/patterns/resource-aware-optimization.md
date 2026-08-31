# 15. Resource-Aware Optimization← Back to all patternsPattern 15 of 20

> Source-derived summary from the supplied agentic design-pattern transcript.

Resource-Aware Optimization
Route simple tasks to cheaper/faster models and complex tasks to stronger models while tracking budget and latency.
All patternsCurrent
In plain English
Route simple tasks to cheaper/faster models and complex tasks to stronger models while tracking budget and latency.
When to use it
- High-volume.
- cost-sensitive enterprise systems..
Typical workflow
Input / Goal
→Analyze
→Execute
→Validate
→Continue / Retry / Escalate
Advantages- Cost.
- resource optimization..
Risks / limitations- Routing/tuning complexity and classification errors..
Architecture context
This pattern is best treated as a reusable building block. It can be combined with routing, planning, tools, RAG, evaluation, recovery, guardrails and human review depending on the workflow.
Source: supplied transcript summarizing agentic design patterns. This page preserves the transcript's framing rather than adding external claims.
