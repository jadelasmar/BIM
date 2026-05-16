# Current Focus

## Current Work

- Keep documentation aligned with the current Django implementation.
- BIM Stock is the active implemented module.
- Login UI refinement from Figma is the next UI task once a usable Figma URL, screenshot, or generated code is provided.

## Do Not Modify Unnecessarily

- SKU generation logic on `Product`.
- Existing model field names such as `descript`, `printed`, `crdate`, and `isactive`.
- Current `ProductUnit` statuses unless a focused status migration is planned.
- Django auth behavior.
- Django admin availability and staff usability.
- BIM Stock templates while working on unrelated modules.

## Immediate Next Implementation Goals

1. Implement the BIM Nexus login UI from Figma in the existing Django login template.
2. Harden BIM Stock permissions and status behavior.
3. Add stock movement audit history.
4. Add Companies / Sites before workflows that need company/site references.
5. Plan React, APIs, and reusable operational UI components in a dedicated session after current Django workflows are stable.
