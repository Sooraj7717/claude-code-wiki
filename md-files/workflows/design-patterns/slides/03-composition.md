# Compose the Patterns

> The real power comes from stacking the patterns around a specific problem.

## Composite Workflow

```text
Fan Out
   ↓
Independent Analysis
   ↓
Adversarial Verification
   ↓
Filter / Judge
   ↓
Loop Until Done
   ↓
Final Verified Result
```

## Example — CRM Audit

### Step 1: Fan Out
Inspect separate areas such as:
- Frontend
- Backend
- Database
- Onboarding flow
- UX
- Error handling

### Step 2: Collect Findings

Each agent returns:
- Finding
- Reason
- File
- Line
- Suggested improvement

### Step 3: Adversarial Verification

Independent agents attempt to:
- Disprove findings.
- Identify false positives.
- Validate findings against the code.
- Challenge assumptions.

### Step 4: Loop Until Done

Continue searching until a clean pass finds no new meaningful issues.

## General Architecture

```text
Input
  ↓
Classify (optional)
  ↓
Fan Out → Isolated Agents
  ↓
Synthesize
  ↓
Adversarial Verification (optional)
  ↓
Filter / Judge
  ↓
Loop Until Completion Condition
  ↓
Final Result
```

## Design Principle

Patterns are building blocks, not mandatory stages.

Choose only the stages that improve:
- correctness
- coverage
- parallelism
- decision quality
- verification

## Navigation

- [← Six Patterns](02-patterns.md)
- [Next: Sharing →](04-sharing.md)
