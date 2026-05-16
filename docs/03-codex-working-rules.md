# Codex Working Rules

Codex should focus on implementation and keep replies short.

## Response Style

Only summarize:
- files changed
- important decisions
- commands run or commands to run
- blockers

Do not explain every change unless asked.

## Before Editing

- Read relevant files first.
- Understand current structure and naming.
- Follow existing project patterns.
- Avoid unrelated refactors.
- Avoid model changes unless needed.
- Ask before destructive actions.
- Preserve user changes in the working tree.

## Project Rules

- Product name: BIM Nexus.
- Active module: BIM Stock.
- Keep BIM modular.
- Work one session/task at a time.
- Django is the source of truth.
- Django admin must remain usable.
- Use Django auth, groups, and permissions.
- Do not build custom insecure authentication.
- Do not remove Django admin.
- Preserve SKU logic unless explicitly asked.
- Preserve current naming unless there is a clear migration reason.
- Avoid unnecessary migrations.

## Current Naming Conventions

Current code uses:
- `descript`
- `printed`
- `crdate`
- `isactive`
- `ProductUnit`
- `ProductModel`

Do not rename these casually. Renames require a deliberate model/migration session.

## Scope Rules

Do not add:
- accounting workflows
- invoicing workflows
- payment workflows
- ticketing or Tasklogger replacement workflows

Do not mark planned modules as completed until implementation exists.

## Django Rules

Use `.venv` if available. Use global Python only if `.venv` is unavailable or blocked.

After model changes:
- run `python manage.py makemigrations`
- run `python manage.py migrate`
- run `python manage.py check`
- update docs

After template/view/admin changes:
- run `python manage.py check`
- run relevant tests when available

## UI Rules

- Current UI is Django templates and CSS.
- No React app exists yet.
- React should be introduced only in a dedicated setup session.
- Figma UI should be inspected before implementation when a Figma URL or usable design asset is provided.
- Match BIM Nexus branding: black, white, orange accent.
- Build modern enterprise SaaS/admin screens.
- Build compact, information-dense, desktop-first responsive screens.
- Use a dark collapsible left sidebar, top navigation/header, and clear main content area for the main operational UI.
- Prefer reusable components for cards, tables, forms, status badges, search/filter bars, page headers, quick actions, and module shortcuts.
- Do not add mock data when real model data exists.

## Documentation Rules

When behavior, workflow, roadmap, or structure changes:
- update the related file in `docs/`
- keep `docs/01-current-structure.md` aligned with code
- keep `docs/02-roadmap.md` realistic
- keep `docs/current-focus.md` aligned with the active task

## Tool Use

Use available tools/plugins only when relevant:
- GitHub for repo, issues, PRs, and version-control workflows
- Figma for design inspection and UI implementation
- Codex Security for security review
- Superpowers for coding workflow support when useful
