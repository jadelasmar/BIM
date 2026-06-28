import { LayoutDashboard, iconComponents } from "../../constants/icons";

export default function Icon({ name, className = "h-4 w-4" }) {
  const Component = iconComponents[name] || LayoutDashboard;
  return <Component className={className} aria-hidden="true" />;
}
