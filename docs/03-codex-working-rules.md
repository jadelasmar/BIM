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