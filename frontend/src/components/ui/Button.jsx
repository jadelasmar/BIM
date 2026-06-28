const variantClasses = {
  primary: "bg-nexus-orange px-4 font-semibold text-black",
  secondary: "px-3 font-semibold text-zinc-200 hover:bg-nexus-panel",
  ghost: "px-3 font-semibold text-zinc-200 hover:bg-nexus-panel",
  outline: "border border-nexus-line px-3 font-semibold text-zinc-200 hover:bg-nexus-panel",
  danger: "border border-nexus-red/60 bg-red-500/10 px-3 font-semibold text-red-200 hover:bg-red-500/15"
};

const sizeClasses = {
  sm: "min-h-9 text-xs",
  md: "h-9 text-sm",
  lg: "h-10 text-sm"
};

export default function Button({
  as: Component = "button",
  variant = "secondary",
  size = "md",
  iconLeft,
  iconRight,
  loading = false,
  disabled = false,
  className = "",
  children,
  ...props
}) {
  const isButton = Component === "button";
  const disabledProps = isButton ? { disabled: disabled || loading } : { "aria-disabled": disabled || loading };
  const stateClass = disabled || loading ? "cursor-not-allowed opacity-60" : "";

  return (
    <Component
      className={`inline-flex items-center justify-center gap-2 rounded-md ${sizeClasses[size]} ${variantClasses[variant]} ${stateClass} ${className}`.trim()}
      {...disabledProps}
      {...props}
    >
      {iconLeft}
      {loading ? "Loading..." : children}
      {iconRight}
    </Component>
  );
}
