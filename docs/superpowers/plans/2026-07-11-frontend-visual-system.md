# Frontend Visual System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify BIM Nexus typography and reusable visual styling around the login screen without changing layout or behavior.

**Architecture:** Bundle four official Inter static Latin WOFF2 files and apply them through global CSS and Tailwind. Consolidate semantic visual tokens in `styles.css`, update shared primitives, then replace only repeated inconsistent typography patterns in current pages.

**Tech Stack:** React 19, Tailwind CSS 3, Vite 8, CSS custom properties, official Inter WOFF2 assets.

## Global Constraints

- Frontend visual consistency only; no backend, route, permission, API, data, or workflow changes.
- Bundle only Inter 400, 500, 600, and 700 Latin WOFF2 files plus the official license.
- No external font requests at runtime.
- Preserve monospace for technical values only.
- Keep existing responsive layouts and component APIs.
- Do not commit automatically.

---

### Task 1: Bundle and register Inter

**Files:**
- Create: `frontend/src/assets/fonts/inter/Inter-Regular.woff2`
- Create: `frontend/src/assets/fonts/inter/Inter-Medium.woff2`
- Create: `frontend/src/assets/fonts/inter/Inter-SemiBold.woff2`
- Create: `frontend/src/assets/fonts/inter/Inter-Bold.woff2`
- Create: `frontend/src/assets/fonts/inter/LICENSE.txt`
- Modify: `frontend/src/styles.css`
- Modify: `frontend/tailwind.config.js`

- [ ] Download the four official static WOFF2 files and license from the Inter project.
- [ ] Verify file names, non-zero sizes, and that no additional font assets exist.
- [ ] Add four `@font-face` declarations with `font-display: swap` and matching numeric weights.
- [ ] Align `--bim-font-family` and Tailwind `fontFamily.sans` with Inter and the existing fallback stack.

### Task 2: Standardize semantic tokens and shared primitives

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/components/ui/Button.jsx`
- Modify: `frontend/src/components/ui/Input.jsx`
- Modify: `frontend/src/components/ui/Card.jsx`
- Modify: `frontend/src/components/ui/Badge.jsx`
- Modify: `frontend/src/components/ui/EmptyState.jsx`
- Modify: `frontend/src/components/ui/SearchBar.jsx`

- [ ] Add semantic CSS variables for typography hierarchy, surfaces, borders, shadows, focus, disabled, and errors in both themes.
- [ ] Normalize button heights, focus-visible rings, hover/disabled states, and typography.
- [ ] Normalize input/search surfaces, focus-visible states, disabled states, and helper/error typography.
- [ ] Normalize card padding/title hierarchy, badges, and empty states using the shared tokens.

### Task 3: Align login and authenticated repeated patterns

**Files:**
- Modify: `frontend/src/pages/auth/AuthPages.jsx`
- Modify: `frontend/src/routes/AppRouter.jsx`

- [ ] Refine login spacing, title hierarchy, helper line height, focus states, and theme balance without changing layout.
- [ ] Replace repeated uppercase wide-tracking section labels with a shared mixed-case section-heading class.
- [ ] Replace obvious one-off button/input styles with existing shared primitives or shared token classes where behavior remains identical.
- [ ] Audit `font-mono` and remove it from non-technical display text only.

### Task 4: Document and verify

**Files:**
- Modify: `docs/DesignSystem.md`
- Generate: `backend/static/frontend/manifest.json`
- Generate: `backend/static/frontend/assets/*`

- [ ] Document Inter source, SIL OFL license, supported weights, fallback stack, and monospace rules.
- [ ] Run `npm run build` from `frontend/`.
- [ ] Run the smallest existing frontend source checks and `git diff --check`.
- [ ] Review representative login, Command Center, inventory/list, detail, and form pages in light and dark mode where available.
