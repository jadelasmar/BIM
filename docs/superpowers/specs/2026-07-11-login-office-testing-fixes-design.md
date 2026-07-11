# Login Office Testing Fixes Design

## Scope

Apply the focused login-screen fixes identified during office testing without changing Django authentication behavior, page layout, branding, or permission rules.

## Configuration and Data Flow

- Add `BIM_ADMIN_EMAIL` to Django settings with `jad.alasmar@bimpos.com` as the fallback.
- Allow deployments to override it through the environment.
- Pass the configured address to the login page through the existing Django initial-data payload.
- Preserve the submitted username/email in that payload after an unsuccessful POST. Never return the submitted password.

## Login Form Behavior

- Keep Django authentication authoritative and retain the generic invalid-credentials message.
- Use controlled React state for the login identifier and password.
- Before native form submission, trim and validate the identifier and verify the password is non-empty.
- Show `Email or username is required.` and `Password is required.` beside the relevant fields.
- Block submission while either required value is missing and preserve both entered values.
- Clear a field's client validation error when the user edits that field.
- On a backend authentication failure, preserve the submitted identifier and render an empty password field.
- Preserve standard form submission so Enter, CSRF handling, `next`, and successful Django login continue to work.

## Accessibility and Styling

- Reuse the shared `Input` error API and add the necessary invalid-input border state there.
- Associate each field error with its input using `aria-invalid` and `aria-describedby`.
- Use centralized `Eye` and `EyeOff` icons. The hidden state shows `Eye`; the visible state shows `EyeOff`.
- Toggle both the password button's accessible label and title between `Show password` and `Hide password` without changing the password value.
- Keep the current dark-mode authentication alert and add light-theme overrides for a pale red background, visible red border, and darker readable text.

## Administrator Email Link

- Build the `mailto:` URL in the login component from the configured administrator address and current identifier.
- Use the specified subject and body, encoded with `URLSearchParams` or equivalent browser URL encoding.
- Populate only the Email line when the identifier contains `@`; otherwise populate only the Username line. When empty, leave both values blank.
- Keep the existing visible copy and link styling.

## Testing and Documentation

- Add Django regression tests first for the configurable administrator address, preserved submitted identifier, generic authentication error, and absence of password data in the response payload.
- Verify the new tests fail before implementation and pass afterward.
- Run `python manage.py check`, `python manage.py test`, `python manage.py makemigrations --check --dry-run`, `npm run build`, and `git diff --check`.
- The frontend has no current test or lint script; do not add a new test framework or lint tool for this focused fix. Report `npm run lint` as unavailable.
- Update `.env.example`, `docs/Development.md`, `docs/Frontend.md`, `docs/DesignSystem.md`, and `docs/CodeMap.md` only where the implemented configuration or durable behavior needs documenting.
