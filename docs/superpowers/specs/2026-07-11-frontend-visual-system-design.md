# Frontend Visual System Design

## Goal

Align the authenticated BIM Nexus interface with the login screen through one locally bundled typeface, shared visual tokens, and reusable primitives without changing layouts or behavior.

## Typography

- Bundle official Inter Latin WOFF2 files for weights 400, 500, 600, and 700 under `frontend/src/assets/fonts/inter/`.
- Include the official SIL Open Font License beside the font files.
- Define each weight once in `frontend/src/styles.css` with `font-display: swap`.
- Apply Inter globally through `--bim-font-family` and Tailwind `fontFamily.sans`, followed by the existing system fallback stack.
- Retain monospace only for references, SKUs, serial numbers, IDs, and technical codes.

## Shared Tokens And Primitives

- Extend existing CSS variables for surfaces, borders, text hierarchy, shadows, focus rings, disabled states, radii, and spacing.
- Standardize Button, Input, SearchBar, Card, Badge, and EmptyState before changing repeated page-level patterns.
- Keep existing component APIs and application layouts unchanged.
- Replace repeated uppercase wide-tracking section labels with a calmer mixed-case shared heading style aligned with login typography.

## Themes And Responsiveness

- Keep both themes driven by the same semantic variables.
- Strengthen light-mode surface hierarchy without changing layout.
- Preserve existing responsive grids, table overflow wrappers, and mobile navigation behavior.

## Verification

- Inspect typography utilities so monospace remains technical only.
- Run the existing focused frontend source check where applicable.
- Run `npm run build` and `git diff --check`.
- Manually review representative login, dashboard, list, detail, and form screens in both themes and responsive widths where the environment permits.

## Documentation

Update `docs/DesignSystem.md` with the official Inter source, SIL OFL license, supported weights, fallback stack, and typography usage rules.
