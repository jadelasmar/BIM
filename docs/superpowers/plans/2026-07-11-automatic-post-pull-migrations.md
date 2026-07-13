# Automatic Post-Pull Migrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically apply existing Django migrations after successful merge-based pulls in this BIM Nexus clone.

**Architecture:** A versioned POSIX-style Git `post-merge` hook runs under Git for Windows, resolves its repository root with Git, and invokes the Windows virtual-environment Python executable. Local `core.hooksPath` activates the repository hook without changing application startup behavior.

**Tech Stack:** Git for Windows hook shell, Windows Python virtual environment, Django management commands, Markdown documentation.

## Global Constraints

- Change repository tooling and documentation only.
- Do not run `makemigrations` automatically.
- Do not create or modify migration files, models, application code, permissions, or business logic.
- A hook failure must be immediately visible but cannot undo a pull that already merged successfully.
- `post-merge` covers merge-based pulls only; rebase-based pulls remain outside scope.
- Do not commit automatically.

---

### Task 1: Versioned post-merge hook

**Files:**
- Create: `.githooks/post-merge`
- Modify: `.gitattributes`

**Interfaces:**
- Consumes: Git repository metadata, `.venv/Scripts/python.exe`, `backend/manage.py`.
- Produces: automatic `migrate --noinput` execution after successful merge-based pulls.

- [ ] **Step 1: Verify the hook does not exist**

Run: `Test-Path .githooks/post-merge`
Expected: `False`.

- [ ] **Step 2: Create the hook**

Create `.githooks/post-merge` with a `#!/bin/sh` entrypoint. Resolve the root using `git rev-parse --show-toplevel`, validate `$repo_root/.venv/Scripts/python.exe`, change to the repository root, run `backend/manage.py migrate --noinput`, and emit explicit stderr messages with non-zero exits for missing Python or migration failure.

- [ ] **Step 3: Validate failure-message coverage statically**

Run: `rg -n "virtual environment|Migration failed|migrate --noinput|rev-parse --show-toplevel" .githooks/post-merge`
Expected: all required behavior appears in the hook.

- [ ] **Step 4: Preserve hook line endings**

Add `.githooks/* text eol=lf` to `.gitattributes` and verify with `git check-attr eol -- .githooks/post-merge`.
Expected: `eol: lf`.

### Task 2: Activate and verify the hook

**Files:**
- Modify local Git configuration: `.git/config` through `git config --local`.

**Interfaces:**
- Consumes: `.githooks/post-merge`.
- Produces: `core.hooksPath=.githooks` for this clone.

- [ ] **Step 1: Activate repository hooks**

Run: `git config --local core.hooksPath .githooks`
Expected: exit code 0.

- [ ] **Step 2: Confirm configuration**

Run: `git config --local core.hooksPath`
Expected: `.githooks`.

- [ ] **Step 3: Invoke through Git for Windows shell**

Run: `git sh .githooks/post-merge` if supported; otherwise invoke the Git-bundled `sh.exe` directly.
Expected: Django reports no migrations to apply and the hook exits 0.

### Task 3: Development documentation

**Files:**
- Modify: `docs/Development.md`

**Interfaces:**
- Consumes: implemented hook behavior.
- Produces: setup and failure-handling guidance for developers.

- [ ] **Step 1: Document automatic migrations**

Add an `Automatic Migrations After Pull` section documenting the hook, merge-based scope, `.venv` dependency, one-time `git config --local core.hooksPath .githooks` command, visible failure behavior, inability to roll back an already completed pull, prohibition on automatic `makemigrations`, and rebase exclusion.

- [ ] **Step 2: Verify documented requirements**

Run: `rg -n "post-merge|core.hooksPath|makemigrations|rebase|virtual environment|cannot undo" docs/Development.md`
Expected: every required topic is present.

### Task 4: Final verification

**Files:**
- Verify only; no additional files.

**Interfaces:**
- Consumes: completed hook, local Git configuration, current database.
- Produces: evidence that the hook and repository remain healthy.

- [ ] **Step 1: Confirm no pending migrations**

Run: `.venv/Scripts/python.exe backend/manage.py migrate --plan`
Expected: `No planned migration operations.`

- [ ] **Step 2: Run Django system check**

Run: `.venv/Scripts/python.exe backend/manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Check whitespace and scope**

Run: `git diff --check` and `git status --short`.
Expected: no whitespace errors; changes limited to editor-session changes, `.githooks/post-merge`, the approved design/plan, and `docs/Development.md`.
