const variantClasses = {
  standard: "h-10 bg-black px-3 text-sm text-zinc-200 placeholder:text-zinc-600",
  auth: "min-h-10 bg-nexus-panel2 px-3 text-sm text-white placeholder:text-zinc-400"
};

// Auth inputs use a deeper focus accent (--bim-orange-focus) than the standard
// nexus-orange token, which drops to ~2:1 against light-mode surfaces and fails
// the 3:1 non-text contrast minimum for a focus indicator.
const focusClasses = {
  standard: "focus:border-nexus-orange focus:ring-nexus-orange/20",
  auth: "focus:border-[var(--bim-orange-focus)] focus:ring-[var(--bim-orange-focus)]/30"
};

export default function Input({
  label,
  helperText,
  error,
  variant = "standard",
  wrapperClassName = "",
  labelClassName = "text-sm font-semibold text-white",
  className = "",
  ...props
}) {
  const errorClasses = error
    ? "border-nexus-red focus:border-nexus-red focus:ring-red-500/20"
    : `border-nexus-line ${focusClasses[variant]}`;
  const input = (
    <input
      className={`w-full rounded-control border outline-none transition-colors focus:ring-2 disabled:cursor-not-allowed disabled:bg-[var(--bim-disabled-surface)] disabled:text-[var(--bim-muted)] ${errorClasses} ${variantClasses[variant]} ${className}`.trim()}
      {...props}
    />
  );

  if (!label) {
    return input;
  }

  return (
    <label className={`block ${wrapperClassName}`.trim()}>
      <span className={labelClassName}>{label}</span>
      <span className="mt-2 block">{input}</span>
      {helperText ? <p className="mt-2 bim-helper-text">{helperText}</p> : null}
      {error ? <p className="mt-2 text-xs font-medium leading-5 text-red-300">{error}</p> : null}
    </label>
  );
}
