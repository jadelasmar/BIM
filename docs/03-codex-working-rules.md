# Codex Working Rules

Codex should focus on implementation, not long explanations.

## Response Style

Keep replies concise.

Only include:
- files changed
- important decisions
- commands to run
- errors or blockers

Do not explain every line of code unless asked.

## Development Rules

Before changing code:
- inspect current files
- understand existing model names
- avoid renaming unless requested
- avoid large unrelated changes
- apply requested changes directly
- ask before destructive operations

After changing models:
- run makemigrations
- run migrate
- run python manage.py check

## Important

Do not use checked-in virtual environments.

Use:
- system Python
or
- create a fresh .venv

Install requirements with:

pip install -r requirements.txt

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
- Codex Security for security review
- Figma for design inspection and UI implementation
- Superpowers for extra coding workflow support

For UI/design sessions, check whether Figma is relevant before implementing the UI.

## Documentation Rule

When code changes affect models, workflows, app structure, or roadmap:
- update the related docs in `docs/`
- keep `docs/01-current-structure.md` matching the actual code
- keep `docs/02-roadmap.md` matching the current plan
- do not update docs for tiny internal code cleanup unless behavior or structure changes
