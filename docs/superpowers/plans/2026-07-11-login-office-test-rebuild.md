# Login Office-Test Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Django serve the already-implemented BIM Nexus login fixes by rebuilding the current React source and verifying the full requested behavior.

**Architecture:** Preserve the current Django and React source because it already implements the approved login behavior. Use the existing Vite build pipeline to refresh `backend/static/frontend/`, then verify backend regression tests, Django configuration, migration drift, frontend compilation, and whitespace.

**Tech Stack:** Django 6, React 19, Vite 8, Tailwind CSS, Django test runner.

## Global Constraints

- Do not redesign the login page or change business logic.
- Keep Django authentication, CSRF, redirects, branding, layout, theme, and permissions authoritative and unchanged.
- Do not add a frontend test framework, lint tool, models, or migrations.
- Do not edit generated frontend assets manually; generate them only with `npm run build`.
- Do not commit automatically.

---

### Task 1: Verify current login source and focused tests

**Files:**
- Test: `backend/apps/accounts/tests.py`
- Inspect: `backend/apps/accounts/views.py`
- Inspect: `frontend/src/pages/auth/AuthPages.jsx`

**Interfaces:**
- Consumes: current Django initial-data flow and React login page.
- Produces: evidence that the source already implements the requested behavior.

- [ ] **Step 1: Run focused account tests**

Run: `.venv/Scripts/python.exe backend/manage.py test apps.accounts`
Expected: all account tests pass, including configured administrator email, preserved trimmed identifier, generic authentication error, and no password payload.

- [ ] **Step 2: Confirm required frontend behavior exists**

Run: `rg -n "EyeOff|Email or username is required|Password is required|URLSearchParams|adminEmail|aria-describedby" frontend/src/pages/auth/AuthPages.jsx`
Expected: every required behavior is present in editable React source.

### Task 2: Rebuild Django-served frontend assets

**Files:**
- Generate: `backend/static/frontend/manifest.json`
- Generate: `backend/static/frontend/assets/*`

**Interfaces:**
- Consumes: `frontend/src/`.
- Produces: current hashed frontend bundle referenced by Django's Vite manifest integration.

- [ ] **Step 1: Build frontend**

Run: `npm run build` from `frontend/`.
Expected: Vite exits 0 and writes the current bundle to `backend/static/frontend/`.

- [ ] **Step 2: Confirm built bundle contains login behavior**

Run: search the generated JavaScript for the required validation and administrator-mail subject strings.
Expected: the built bundle contains both strings.

### Task 3: Full verification

**Files:**
- Verify only.

**Interfaces:**
- Consumes: current source and generated bundle.
- Produces: completion evidence.

- [ ] **Step 1: Run Django checks and full tests**

Run: `.venv/Scripts/python.exe backend/manage.py check` and `.venv/Scripts/python.exe backend/manage.py test`.
Expected: system check and all tests pass.

- [ ] **Step 2: Check migration drift**

Run: `.venv/Scripts/python.exe backend/manage.py makemigrations --check --dry-run`.
Expected: `No changes detected`.

- [ ] **Step 3: Check whitespace and scope**

Run: `git diff --check`, `git status --short`, and `git diff --stat`.
Expected: no whitespace errors; generated changes come only from the official Vite build, alongside pre-existing workspace changes.

- [ ] **Step 4: Report unavailable lint command**

Inspect `frontend/package.json`.
Expected: no `lint` script; report it as unavailable without adding tooling.
