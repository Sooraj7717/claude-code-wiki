# Package, Save & Share

> Workflows can be treated as reusable artifacts rather than one-off prompts.

## Workflow Package

A reusable workflow can contain:
- Workflow logic
- Instructions
- Evaluation material
- Supporting documents

## Typical Structure

```text
workflow/
├── SKILL.md
├── workflow.js
├── rubric.md
└── supporting files
```

## Why Package Workflows?

- Reuse a proven workflow.
- Share the same process with a team.
- Keep execution logic and evaluation rules together.
- Make complex workflows easier to maintain.

## Operational Consideration

Dynamic workflows can consume substantial token budget.

Therefore:
- Use them deliberately.
- Reserve them for larger or layered problems.
- Avoid turning every small task into a multi-agent workflow.

## Navigation

- [← Composition](03-composition.md)
- [Next: When to Use →](05-when-to-use.md)
