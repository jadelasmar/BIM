import { useEffect, useState } from "react";
import { Eye, EyeOff, Moon, Sun } from "../../constants/icons";
import { Button, Input } from "../../components/ui";
import { DEFAULT_THEME_STORAGE_KEY, applyTheme, currentTheme } from "../../hooks/useTheme";

import logoPrimary from "../../assets/brand/logo-primary.svg";
import logoWhite from "../../assets/brand/logo-white.svg";

function AuthShell({ title, subtitle, children }) {
  const [theme, setThemeState] = useState(() => currentTheme());
  const isLight = theme === "light";

  useEffect(() => {
    function handleThemeChange(event) {
      setThemeState(event.detail === "light" ? "light" : "dark");
    }

    document.addEventListener("bim-nexus-theme-change", handleThemeChange);
    return () => document.removeEventListener("bim-nexus-theme-change", handleThemeChange);
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-nexus-page px-4 py-12 text-white">
      <div className="relative w-full max-w-[392px]">
        <button
          type="button"
          onClick={() => setThemeState(applyTheme(isLight ? "dark" : "light", DEFAULT_THEME_STORAGE_KEY))}
          className="absolute right-0 top-[-46px] grid h-9 w-9 place-items-center rounded-md border border-nexus-line bg-nexus-panel text-zinc-200 shadow-panel"
          aria-label={isLight ? "Switch to dark theme" : "Switch to light theme"}
          title="Switch theme"
        >
          {isLight ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <section className="rounded-xl border border-nexus-line bg-nexus-panel p-3 shadow-panel" aria-labelledby="auth-title">
          <header className="grid gap-4 pb-5 text-center">
            <img className="bim-sidebar-logo-dark mx-auto h-auto w-[min(221px,100%)]" src={logoWhite} alt="BIM Nexus" />
            <img className="bim-sidebar-logo-light mx-auto h-auto w-[min(221px,100%)]" src={logoPrimary} alt="BIM Nexus" />
            <div>
              <h1 id="auth-title" className="text-[21px] font-semibold leading-7 text-white">
                {title}
              </h1>
              {subtitle ? <p className="text-xs leading-5 text-zinc-400">{subtitle}</p> : null}
            </div>
          </header>
          {children}
        </section>
      </div>
    </main>
  );
}

function FieldErrorList({ errors = [], id }) {
  if (!errors.length) {
    return null;
  }

  return (
    <ul id={id} className="mb-2 list-disc pl-5 text-xs text-red-300">
      {errors.map((error) => (
        <li key={error}>{error}</li>
      ))}
    </ul>
  );
}

function AuthInput({ label, name, type = "text", autoComplete, placeholder, error, errors = [], ...props }) {
  const errorId = `id_${name}_error`;
  const hasError = Boolean(error || errors.length);

  return (
    <div className="grid gap-1.5">
      <label className="text-xs font-medium text-white" htmlFor={`id_${name}`}>
        {label}
      </label>
      <Input
        id={`id_${name}`}
        name={name}
        type={type}
        variant="auth"
        autoComplete={autoComplete}
        placeholder={placeholder}
        error={hasError}
        aria-invalid={hasError}
        aria-describedby={hasError ? errorId : undefined}
        {...props}
      />
      {error ? <p id={errorId} className="text-xs font-semibold text-red-300">{error}</p> : null}
      {!error ? <FieldErrorList id={errorId} errors={errors} /> : null}
    </div>
  );
}

export function LoginPage({ data }) {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState(data.username || "");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const next = data.next || "";
  const trimmedUsername = username.trim();
  const mailtoParams = new URLSearchParams({
    subject: "BIM Nexus - Account Access Request",
    body: `Hello,\n\nI need help accessing BIM Nexus.\n\nEmail: ${trimmedUsername.includes("@") ? trimmedUsername : ""}\nUsername: ${trimmedUsername && !trimmedUsername.includes("@") ? trimmedUsername : ""}\n\nPlease send me a secure account setup or password reset link.\n\nApplication: BIM Nexus\nRequest: Account setup / password reset\n\nThank you.`,
  });
  const administratorMailto = `mailto:${data.adminEmail}?${mailtoParams.toString()}`;

  function handleSubmit(event) {
    const errors = {};

    if (!trimmedUsername) {
      errors.username = "Email or username is required.";
    }
    if (!password) {
      errors.password = "Password is required.";
    }

    if (Object.keys(errors).length) {
      event.preventDefault();
      setFieldErrors(errors);
      return;
    }

    event.currentTarget.elements.username.value = trimmedUsername;
    setUsername(trimmedUsername);
  }

  return (
    <AuthShell title={data.title || "Welcome Back"} subtitle="Internal IT Operations Platform">
      {data.errors?.length ? (
        <p className="auth-error-alert mb-4 rounded-md border border-red-300/30 bg-red-950/25 px-3 py-2 text-xs leading-5 text-red-300" role="alert">
          {data.errors[0]}
        </p>
      ) : null}

      <form className="grid gap-4" method="post" action={data.action || "/accounts/login/"} onSubmit={handleSubmit} noValidate>
        <input type="hidden" name="csrfmiddlewaretoken" value={data.csrfToken} />
        <AuthInput
          label="Email or Username"
          name="username"
          autoComplete="username"
          placeholder="Enter your Email or Username"
          value={username}
          onChange={(event) => {
            setUsername(event.target.value);
            setFieldErrors((errors) => ({ ...errors, username: undefined }));
          }}
          error={fieldErrors.username}
        />

        <div className="grid gap-1.5">
          <label className="text-xs font-medium text-white" htmlFor="id_password">
            Password
          </label>
          <div className="relative">
            <Input
              id="id_password"
              name="password"
              type={showPassword ? "text" : "password"}
              variant="auth"
              autoComplete="current-password"
              placeholder="Enter your Password"
              className="pl-3 pr-10"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setFieldErrors((errors) => ({ ...errors, password: undefined }));
              }}
              error={fieldErrors.password}
              aria-invalid={Boolean(fieldErrors.password)}
              aria-describedby={fieldErrors.password ? "id_password_error" : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              aria-label={showPassword ? "Hide password" : "Show password"}
              title={showPassword ? "Hide password" : "Show password"}
              aria-pressed={showPassword}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {fieldErrors.password ? (
            <p id="id_password_error" className="text-xs font-semibold text-red-300">
              {fieldErrors.password}
            </p>
          ) : null}
        </div>

        <p className="text-xs leading-5 text-zinc-400">
          First login or forgot password?{" "}
          <a
            href={administratorMailto}
            className="font-semibold text-nexus-orange hover:underline"
          >
            Ask an administrator
          </a>{" "}
          for a secure setup link.
        </p>

        <input type="hidden" name="next" value={next} />
        <Button className="px-3 py-2 text-xs font-medium text-white" size="sm" type="submit" variant="primary">
          Sign In
        </Button>
      </form>

      <p className="mt-5 text-center text-[10px] leading-4 text-zinc-500">
        Built for <strong className="font-medium text-white">BIMPOS</strong>
      </p>
    </AuthShell>
  );
}

export function PasswordSetupPage({ data }) {
  if (!data.validlink) {
    return (
      <AuthShell title={data.title || "This password setup link is invalid"}>
        <p className="mb-4 text-sm leading-6 text-zinc-400">Ask your BIM Nexus administrator to send a new password setup link.</p>
        <Button as="a" className="px-3 py-2 text-sm font-bold text-white" href="/accounts/login/" size="sm" variant="primary">
          Back to Login
        </Button>
      </AuthShell>
    );
  }

  const errors = data.errors || {};

  return (
    <AuthShell title={data.title || "Create your BIM Nexus account"}>
      <p className="mb-4 text-sm leading-6 text-zinc-400">
        Confirm your name, choose your username and password. Leave username blank to use the suggested username from your email.
      </p>

      <form className="grid gap-3.5" method="post" action={data.action}>
        <input type="hidden" name="csrfmiddlewaretoken" value={data.csrfToken} />
        <FieldErrorList errors={errors.__all__} />
        <AuthInput label="Username" name="username" autoComplete="username" placeholder={data.usernamePlaceholder} errors={errors.username} />
        <AuthInput label="First name" name="first_name" autoComplete="given-name" errors={errors.first_name} />
        <AuthInput label="Last name" name="last_name" autoComplete="family-name" errors={errors.last_name} />
        <AuthInput label="New password" name="new_password1" type="password" autoComplete="new-password" errors={errors.new_password1} />
        <AuthInput label="Confirm password" name="new_password2" type="password" autoComplete="new-password" errors={errors.new_password2} />
        <Button className="px-3 py-2 text-sm font-bold text-white" size="lg" type="submit" variant="primary">
          Create Account
        </Button>
      </form>
    </AuthShell>
  );
}
