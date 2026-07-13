export function Card({ as: Component = "section", className = "", children, ...props }) {
  return (
    <Component className={`bim-surface border ${className}`.trim()} {...props}>
      {children}
    </Component>
  );
}

export function CardHeader({ className = "", children, ...props }) {
  return (
    <div className={`border-b border-nexus-line px-4 py-4 ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ as: Component = "h2", className = "", children, ...props }) {
  return (
    <Component className={`bim-section-title ${className}`.trim()} {...props}>
      {children}
    </Component>
  );
}

export function CardDescription({ className = "", children, ...props }) {
  return (
    <p className={`mt-1 text-sm leading-6 text-zinc-500 ${className}`.trim()} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className = "", children, ...props }) {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className = "", children, ...props }) {
  return (
    <div className={`border-t border-nexus-line ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}
