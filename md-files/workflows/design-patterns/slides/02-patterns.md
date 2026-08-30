# The Six Core Patterns

> These are reusable orchestration shapes. They can stand alone or be combined.

## 01 — Classify → Act

- Classify an input before taking action.
- Route it to the appropriate handler.
- Think of the classifier as a receptionist or router.

**Example:** inbox or ticket triage.

```text
Input → Classifier → Task Type → Handler → Action
```

## 02 — Fan Out → Synthesize

- Break a large problem into independent sub-problems.
- Give each part its own context.
- Run agents independently or in parallel.
- Merge structured results at the end.

**Examples:**
- Deep research
- Due diligence
- Multi-area codebase analysis

```text
Large Task
   ↓
A1  A2  A3  A4
   ↓
Synthesize
   ↓
Final Result
```

## 03 — Adversarial Verification

- Use independent skeptics or devil's advocates.
- Check output against a predefined rubric.
- Avoid relying on the original creator to be the sole reviewer.

**Examples:**
- Fact checking
- Technical claims
- Code review
- Quality assurance

```text
Created Output
      ↓
Independent Critics
      ↓
Rubric
      ↓
Verified Result
```

## 04 — Generate → Filter

- Overgenerate possible solutions.
- Evaluate many candidates.
- Filter down to the strongest options.

**Examples:**
- Video titles
- Product names
- Brand ideas
- Marketing concepts
- UX ideas

```text
Many Ideas → Judge → Filter → Best Candidates
```

A more advanced implementation separates generators from judges.

## 05 — Tournament

- Compare candidates pairwise.
- Winners advance to the next round.
- Continue until a final winner remains.
- Each comparison can use a fresh context.

**Example:** ranking a very large set of resumes.

```text
Round 1 → Round 2 → Round 3 → ... → Final
```

Different rounds can use different rubrics.

## 06 — Loop → Done

- Do not specify an arbitrary number of attempts.
- Define the condition that means the task is complete.
- Continue until that condition is reached.

**Example:** finding a flaky test that fails only occasionally.

```text
Attempt
  ↓
Analyze
  ↓
Form Hypothesis
  ↓
Test
  ↓
Done?
 ├─ No → Try Again
 └─ Yes → Finish
```

## Navigation

- [← Mechanics](01-mechanics.md)
- [Next: Composition →](03-composition.md)
