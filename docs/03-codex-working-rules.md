# Codex Working Rules

This file defines how Codex should work in this repository.

Codex should focus on implementation, not long explanations.

## Response Style

Keep replies short, precise, and practical.

Only include:
- files changed
- important decisions
- commands to run
- errors or blockers

Do not explain every line of code unless asked.
Avoid long answers unless the user explicitly asks for detailed explanation.

## Development Rules

Before changing code:
- inspect current files
- understand the current structure and naming
- follow existing project patterns
- understand existing model names
- avoid renaming unless requested
- avoid large unrelated changes
- avoid unrelated refactors
- avoid changing models unless needed
- apply requested changes directly
- ask before destructive operations

After changing models:
- run makemigrations
- run migrate
- run python manage.py check

## Important

Do not use checked-in virtual environments.

Use:
- `.venv` if available
- system Python only if `.venv` is unavailable or causing a blocker
- create a fresh `.venv` when needed

Install requirements with:

pip install -r requirements.txt

Codex / VS Code setup:
- Codex is not a Django dependency and should not be added to `requirements.txt`
- On another PC, install VS Code, install/configure the Codex or OpenAI developer tool used by the account, then open this repository
- Project setup still uses `pip install -r requirements.txt`

## Project Rules

- Keep BIM modular
- BIM Stock is only one module
- Do not overbuild too early
- Prefer small stable changes
- One feature per session
- Preserve existing architecture unless explicitly requested
- Avoid unnecessary migrations
- Prefer explicit readable code over clever abstractions

## Django / BIM Conventions

- Soft delete uses `isactive`
- SKU is auto-generated
- Preserve admin readability
- Keep Django admin optimized for non-technical staff
- Preserve SQL Anywhere compatibility considerations

## Optional Tools / Plugins

The following plugins may be available in Codex sessions:
- GitHub
- Superpowers
- Codex Security
- Figma

Use them only when relevant to the task.

Suggested use:
- GitHub for issues, PRs, repo review, and version-control workflows
- Superpowers for coding workflow support when useful
- Codex Security for security review
- Figma for design inspection and UI implementation

For UI/design sessions, check whether Figma is relevant before implementing the UI.

## Documentation Rule

When code changes affect models, workflows, app structure, or roadmap:
- update the related docs in `docs/`
- keep `docs/01-current-structure.md` matching the actual code
- keep `docs/02-roadmap.md` matching the current plan
- do not update docs for tiny internal code cleanup unless behavior or structure changes

## Session Progress Rule

During a session:
- keep working on the same session/model unless requested otherwise
- after each completed task inside the session, update the related status in `docs/05-bim-stock-session-plan.md`
- mark items as `pending`, `in progress`, `done`, or `blocked`
- add the next needed item under the same session when discovered
- do not jump to the next session unless the user asks or the current session is complete
