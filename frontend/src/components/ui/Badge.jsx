import Icon from "../common/Icon";
import { statusMeta } from "../../constants/statusStyles";
import { TONE_COLORS } from "../../constants/toneColors";

const toneClasses = {
  neutral: TONE_COLORS.zincSoft15,
  primary: TONE_COLORS.amberSoft15Nexus,
  success: TONE_COLORS.greenSoft15,
  warning: TONE_COLORS.amberSoft15Amber,
  danger: TONE_COLORS.redSoft15,
  info: TONE_COLORS.blueSoft15
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
