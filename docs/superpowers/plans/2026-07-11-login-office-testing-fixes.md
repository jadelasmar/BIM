# Login Office Testing Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the office-tested login validation, password visibility, authentication failure, alert contrast, and administrator-contact behavior without changing Django authentication semantics or redesigning the page.

**Architecture:** Django remains responsible for authentication and supplies the configurable administrator email plus the safe submitted identifier in the existing initial-data payload. React adds controlled form state and pre-submit required validation, then uses native form submission for CSRF, Enter-key behavior, redirects, and authentication.

**Tech Stack:** Django 6, Django test runner, React 19, Vite 8, Tailwind CSS 3, Lucide React.

## Global Constraints

- Default `BIM_ADMIN_EMAIL` to `jad.alasmar@bimpos.com` and allow environment override.
- Never expose or restore a submitted password.
- Keep the generic message `Invalid username/email or password.`.
- Keep Django authentication authoritative; client-side validation is UX only.
- Preserve layout, branding, authentication semantics, dark/light themes, CSRF, `next`, Enter submission, and logical tab order.
- Reuse the shared `Input` component and centralized icon exports.
- Do not add dependencies, a frontend test framework, lint tooling, migrations, unrelated refactors, or commits.

---

### Task 1: Django login payload regression coverage

**Files:**
- Create: `backend/apps/accounts/tests.py`
- Modify: `backend/bim/settings.py`
- Modify: `backend/apps/accounts/views.py`

**Interfaces:**
- Consumes: Django setting `settings.BIM_ADMIN_EMAIL` and POST field `username`.
- Produces: login page payload keys `adminEmail: str` and `username: str`; password is never included.

- [ ] **Step 1: Write failing Django tests**

Create `LoginViewTests` using `TestCase`, `override_settings`, and `reverse`. Assert a GET exposes the overridden administrator email. Post invalid credentials and assert the response retains a trimmed username, keeps the generic error, and contains no `password` key or submitted password in `response.context["initial_data"]["page"]`.

- [ ] **Step 2: Run the focused tests red**

Run from `backend/`:

```powershell
python manage.py test apps.accounts.tests.LoginViewTests
```

Expected: failures for missing `adminEmail` and `username` payload keys.

- [ ] **Step 3: Add minimal backend implementation**

In settings:

```python
BIM_ADMIN_EMAIL = os.environ.get(
    "BIM_ADMIN_EMAIL",
    "jad.alasmar@bimpos.com",
)
```

In the login view, import `settings`, compute `submitted_username = request.POST.get("username", "").strip()` only for payload restoration, and add:

```python
"adminEmail": settings.BIM_ADMIN_EMAIL,
"username": submitted_username,
```

Do not add a password payload field and do not alter form authentication.

- [ ] **Step 4: Run the focused tests green**

Run the same focused test command. Expected: all `LoginViewTests` pass.

### Task 2: Login form UX and accessibility

**Files:**
- Modify: `frontend/src/pages/auth/AuthPages.jsx`
- Modify: `frontend/src/components/ui/Input.jsx`
- Modify: `frontend/src/constants/icons.js`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `data.adminEmail`, `data.username`, shared `Input` error props, and centralized `Eye`/`EyeOff` exports.
- Produces: client validation messages, accessible invalid states, state-aware visibility icon, and encoded mailto URL.

- [ ] **Step 1: Add centralized `EyeOff` export**

Import and export `EyeOff` only through `frontend/src/constants/icons.js`.

- [ ] **Step 2: Extend shared input invalid styling**

Have `Input` apply a red border/ring class when its existing `error` prop is truthy while preserving current variants and focus behavior.

- [ ] **Step 3: Implement controlled login state and validation**

Initialize `username` from `data.username || ""` and password as empty. On submit, use `username.trim()` for validation and submission by assigning the trimmed value to state/input only at submit time. If either field is empty, prevent submission and set exactly:

```text
Email or username is required.
Password is required.
```

Keep typed values on client validation failure and clear each field's error when that field changes. Bind `aria-invalid` and `aria-describedby` to visible field errors.

- [ ] **Step 4: Implement visibility and authentication alert changes**

Render `Eye` for password type and `EyeOff` for text type. Toggle `aria-label` and `title` between `Show password` and `Hide password`. Keep the password state unchanged. Add an `auth-error-alert` class and a focused `[data-theme="light"]` override in `styles.css` for a pale red background, red border, and dark red text while preserving current dark classes.

- [ ] **Step 5: Build the configured mailto link**

Build the body with both `Email:` and `Username:` lines. Populate Email only when the trimmed identifier contains `@`; otherwise populate Username. Use `URLSearchParams` to encode the exact approved subject and body, and use `data.adminEmail` as the recipient.

- [ ] **Step 6: Build frontend**

Run from `frontend/`:

```powershell
npm run build
```

Expected: Vite build succeeds without compile errors.

### Task 3: Configuration and durable documentation

**Files:**
- Modify: `.env.example`
- Modify: `docs/Development.md`
- Modify: `docs/Frontend.md`
- Modify: `docs/DesignSystem.md`
- Modify: `docs/CodeMap.md`

**Interfaces:**
- Documents: `BIM_ADMIN_EMAIL`, login payload restoration, client validation, shared invalid input styling, and centralized `EyeOff` usage.

- [ ] **Step 1: Document environment configuration**

Add `BIM_ADMIN_EMAIL=jad.alasmar@bimpos.com` to `.env.example` and describe the fallback/override in `docs/Development.md`.

- [ ] **Step 2: Update frontend and design-system behavior**

Document the controlled login validation, safe identifier restoration, configured administrator mailto, input invalid styling, and state-aware password icons in `docs/Frontend.md` and `docs/DesignSystem.md`.

- [ ] **Step 3: Update code map carefully**

Add only the relevant settings/view/auth-page responsibilities to `docs/CodeMap.md`, preserving any pre-existing user edits.

### Task 4: Full verification

**Files:**
- Verify only; fix only failures caused by this change.

- [ ] **Step 1: Run backend system check**

```powershell
cd backend
python manage.py check
```

Expected: no system-check issues.

- [ ] **Step 2: Run full Django suite**

```powershell
cd backend
python manage.py test
```

Expected: all tests pass.

- [ ] **Step 3: Confirm no migrations**

```powershell
cd backend
python manage.py makemigrations --check --dry-run
```

Expected: no changes detected.

- [ ] **Step 4: Run production frontend build**

```powershell
cd frontend
npm run build
```

Expected: build succeeds. `npm run lint` is unavailable because `frontend/package.json` defines no lint script; do not add tooling for this fix.

- [ ] **Step 5: Run diff hygiene check**

```powershell
git diff --check
```

Expected: no whitespace errors. Review `git status --short` and final diffs to confirm scope and preservation of user-owned changes.
