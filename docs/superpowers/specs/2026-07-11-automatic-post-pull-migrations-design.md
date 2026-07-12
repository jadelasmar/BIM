# Automatic Post-Pull Migrations Design

## Goal

Keep the local BIM Nexus SQLite schema current by applying existing Django migrations automatically after a successful merge-based `git pull`.

## Design

- Store a versioned Git hook at `.githooks/post-merge`.
- Force `.githooks/*` to LF line endings in `.gitattributes` so Git for Windows preserves executable shebang lines when `core.autocrlf=true`.
- Configure this repository clone with `core.hooksPath=.githooks` once.
- The hook resolves the repository root instead of depending on the caller's working directory.
- On Windows, it runs `.venv/Scripts/python.exe backend/manage.py migrate --noinput`.
- If the virtual-environment interpreter is missing, the hook prints a clear setup error and exits non-zero.
- If Django migration fails, the hook prints a clear failure message and exits non-zero so the outdated database is not silent.

## Scope

- No model, migration-file, application, or business-logic changes.
- No automatic migration creation; `makemigrations` remains an intentional development action.
- The hook applies migrations only after merge-based pulls. Rebase-based pulls do not invoke `post-merge` and remain outside this initial scope.

## Verification

- Confirm the hook is executable by Git for Windows.
- Confirm `git config --local core.hooksPath` returns `.githooks`.
- Invoke the hook directly and confirm migrations complete successfully.
- Confirm `manage.py migrate --plan` reports no pending operations.
- Run `manage.py check` and `git diff --check`.

## Documentation

Update `docs/Development.md` to explain the automatic post-pull migration behavior, its `.venv` dependency, and the one-time local Git configuration.
