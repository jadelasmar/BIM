import Icon from "../common/Icon";

export default function EmptyState({ icon, title, description, action, className = "" }) {
  return (
    <div className={`grid min-h-40 place-items-center px-4 py-8 text-center ${className}`.trim()}>
      <div>
        {icon ? <Icon name={icon} className="mx-auto mb-3 h-8 w-8 text-zinc-600" /> : null}
        <p className="text-sm font-semibold leading-5 text-zinc-300">{title}</p>
        {description ? <p className="mt-1 bim-helper-text">{description}</p> : null}
        {action ? <div className="mt-4">{action}</div> : null}
      </div>
    </div>
  );
}
