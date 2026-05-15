# Start Here

This is the first file to read before any Codex work on the project.

Before making changes, read these files in order:

1. docs/00-project-overview.md
2. docs/01-current-structure.md
3. docs/02-roadmap.md
4. docs/03-codex-working-rules.md
5. docs/04-session-prompts.md
6. docs/05-bim-stock-session-plan.md

Rules:
- Keep replies short
- Focus on implementation
- BIMPOS is an internal IT stock and operations platform
- Do not add accounting, invoicing, payment, or Tasklogger/ticketing features
- Do not explain every change
- Only show files changed, important decisions, commands to run, and blockers
- Read the docs before editing code
- Keep BIM modular
- One feature per session
- Use available plugins/tools when relevant
- For UI/design tasks, check Figma if available
- For security tasks, use Codex Security if available
- Use Superpowers if available when it helps the coding workflow
- Use GitHub if available for repo, issue, PR, or version-control tasks
- Work only on the requested session unless told otherwise
- After each completed item, update its status in `docs/05-bim-stock-session-plan.md`
- If you discover a needed item for the current session, add it under that same session
- Keep replies short

Session prompt:

```text
Read docs/START-HERE.md first, then do this task:

[task here]
```

Default BIMPOS session prompt:

```text
Read docs/START-HERE.md first.
Use the available tools/plugins when relevant.
Continue with the next unfinished BIMPOS session from docs/05-bim-stock-session-plan.md.
```
