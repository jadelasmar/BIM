const variantClasses = {
  standard: "h-10 bg-black px-3 text-sm text-zinc-200 placeholder:text-zinc-600",
  auth: "min-h-9 bg-nexus-panel2 px-3 py-2 text-xs text-white placeholder:text-zinc-500"
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
  const input = (
    <input
      className={`w-full rounded-md border border-nexus-line outline-none focus:border-nexus-orange focus:ring-2 focus:ring-nexus-orange/20 disabled:bg-zinc-800/80 disabled:text-zinc-500 ${variantClasses[variant]} ${className}`.trim()}
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
      {helperText ? <p className="mt-2 text-xs text-zinc-500">{helperText}</p> : null}
      {error ? <p className="mt-2 text-xs font-semibold text-red-300">{error}</p> : null}
    </label>
  );
}
