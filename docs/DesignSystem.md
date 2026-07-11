# Design System

BIM Nexus uses a compact enterprise dashboard style: dark-first, restrained, operational, and built around black, white, zinc neutrals, and orange accent.

## Brand

- Product name: BIM Nexus
- Built for: BIMPOS
- Subtitle: Internal IT Operations Platform

Editable logos:

- `frontend/src/assets/brand/logo-primary.svg`
- `frontend/src/assets/brand/logo-white.svg`

Rules:

- Use white logo on dark backgrounds.
- Use primary logo on light backgrounds.
- Use alt text `BIM Nexus`.
- Use `Built for BIMPOS` consistently.

## Colors

Tailwind color tokens are backed by CSS variables in `frontend/src/styles.css`.

Core tokens:

- `bg-nexus-page`
- `bg-nexus-panel`
- `bg-nexus-panel2`
- `border-nexus-line`
- `text-nexus-orange`
- `text-nexus-green`
- `text-nexus-red`
- `text-nexus-blue`
- `text-nexus-purple`

Use orange for primary actions and active states. Use red for danger/error. Use green for success/available.

For dashboard KPIs and System Overview cards, use orange only for active, hover/focus, or warning states such as Low Stock. Normal operational counts, including Reserved Stock, should use neutral card styling by default unless they are actively selected as a filter. Warning/problem counts such as Low Stock, Out of Stock, and Repair use muted/neutral icon styling when the count is zero and warning color only when the count is greater than zero.

## Icons

Source:

- `frontend/src/constants/icons.js`
- `frontend/src/components/common/Icon.jsx`

Rules:

- Use `lucide-react` only through `constants/icons.js`.
- Do not import `lucide-react` directly in pages.
- Password visibility controls use `Eye` while hidden and `EyeOff` while visible, with matching accessible labels and titles.
- Default icon size: `h-4 w-4`.
- Card/action icon size: `h-5 w-5`.
- Status icon size: `h-3.5 w-3.5`.

## Typography

Common classes:

- Page title: `text-2xl font-bold text-white`
- Page description: `mt-1 text-sm text-zinc-400`
- Section label: `text-xs font-bold uppercase tracking-[0.24em] text-zinc-400`
- Card title: `text-sm font-bold text-white`
- Body text: `text-sm`
- Muted helper: `text-xs text-zinc-500`
- Error text: `text-xs text-red-300`
- Identifiers: `font-mono text-xs text-nexus-orange`

Avoid one-off font sizes unless a current pattern requires it.

## Spacing And Layout

Shell:

- Main page padding: `px-4 py-5 sm:px-6 lg:px-7`
- Sidebar width: `248px`
- Page header spacing: `mb-5`
- Section spacing: `mt-4` or `mt-5`

Cards:

- Default: `rounded-lg border border-nexus-line bg-nexus-panel`
- Dense padding: `p-3` or `p-4`
- Form/detail padding: `p-5`

## Buttons

Reusable component:

- `frontend/src/components/ui/Button.jsx`

Primary:

```text
inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black
```

Secondary:

```text
inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel
```

Outline:

```text
inline-flex h-9 items-center gap-2 rounded-md border border-nexus-line px-3 font-semibold text-zinc-200 hover:bg-nexus-panel
```

Icon-only buttons need an `aria-label`.

## Forms

Reusable component:

- `frontend/src/components/ui/Input.jsx`
- `frontend/src/components/ui/SearchBar.jsx`

Standard input:

```text
h-10 w-full rounded-md border border-nexus-line bg-black px-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600
```

Auth input:

```text
min-h-9 w-full rounded-md border border-nexus-line bg-nexus-panel2 px-3 py-2 text-xs text-white outline-none placeholder:text-zinc-500
```

Use `text-nexus-orange` for required markers.

Invalid inputs reuse the shared `Input` error state, including a red border/focus ring, adjacent error text, `aria-invalid`, and `aria-describedby`. Authentication alerts preserve the dark-mode treatment and use the `auth-error-alert` light-theme override for a pale red surface, visible red border, and dark red text.

## Tables

- Wrapper: `overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel`
- Inner: `overflow-x-auto`
- Table: `min-w-full text-left text-sm`
- Header: `bg-zinc-800/80 text-zinc-400`
- Header cells: `px-4 py-3 font-medium`
- Body cells: `px-4 py-4`
- Row hover: `hover:bg-zinc-900/70`

## Status Badges

Source:

- `frontend/src/constants/statusStyles.js`
- `frontend/src/components/ui/Badge.jsx`

Badge shape:

```text
inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold
```

Do not invent per-page status colors.

Current ProductUnit status badges:

- `available`
- `reserved`
- `issued`
- `sold`
- `repair`
- `inactive`

Do not expose `returned` or `damaged` as active stock-unit badge statuses.

## Cards And Empty States

Reusable components:

- `frontend/src/components/ui/Card.jsx`
- `frontend/src/components/ui/EmptyState.jsx`

Use `Card` for repeated panel surfaces. Use `EmptyState` for repeated empty panels. Do not create new UI primitives until the pattern is repeated and needed by current work.

## Themes

Theme helpers live in:

- `frontend/src/hooks/useTheme.js`

Storage key:

- `bim-nexus-theme`

Light theme is implemented with CSS variable overrides in `frontend/src/styles.css`.

## Accessibility

- Icon-only buttons need `aria-label`.
- Decorative icons use `aria-hidden="true"`.
- Images need useful `alt` text.
- Keyboard navigation must work for clickable table rows.
- Use text and icons, not color alone, for status.

## Future Page Rules

- Follow existing shell, header, card, button, form, table, and status patterns.
- Use reusable components from `frontend/src/components/ui/` when one already matches the needed pattern.
- Keep pages compact and operational.
- Use real backend data where available.
- Do not add fake/demo data as production UI data.
- Add reusable components only when they remove real duplication.
