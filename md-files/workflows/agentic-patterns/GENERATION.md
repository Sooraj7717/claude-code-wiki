# HTML Generation Notes

Use `README.md` as the parent/index content and `patterns/*.md` as the source content for the 20 detail pages.

## Expected output structure

```text
agentic-patterns/
├── index.html
├── assets/
│   ├── style.css
│   └── app.js
└── patterns/
    ├── prompt-chaining.html
    ├── routing.html
    └── ...
```

## Rendering rules

- Keep the parent page as the navigation hub.
- Generate one HTML page per Markdown pattern file.
- Preserve the same visual hierarchy as the supplied presentation.
- Convert Markdown headings to section headings.
- Convert bullet lists to readable cards/lists.
- Preserve workflow diagrams as Mermaid/ASCII/code-style blocks when present.
- Use relative links so the package works locally without a server.
