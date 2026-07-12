import Icon from "../common/Icon";
import { statusMeta } from "../../constants/statusStyles";

const toneClasses = {
  neutral: "bg-zinc-500/15 text-zinc-400",
  primary: "bg-amber-500/15 text-nexus-orange",
  success: "bg-green-500/15 text-green-400",
  warning: "bg-amber-500/15 text-amber-400",
  danger: "bg-red-500/15 text-red-400",
  info: "bg-blue-500/15 text-blue-400"
};

export default function Badge({ status, tone = "neutral", icon, children, className = "" }) {
  const meta = status ? statusMeta[status] || statusMeta.available : null;
  const iconName = icon || meta?.icon;
  const colorClass = meta?.className || toneClasses[tone] || toneClasses.neutral;

  return (
    <span className={`inline-flex items-center gap-1 rounded-control px-2 py-1 text-xs font-medium leading-4 ${colorClass} ${className}`.trim()}>
      {iconName ? <Icon name={iconName} className="h-3.5 w-3.5" /> : null}
      {children}
    </span>
  );
}
