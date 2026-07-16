import { TONE_COLORS } from "./toneColors";

export const toneClasses = {
  blue: TONE_COLORS.blueSoft10Nexus,
  cyan: TONE_COLORS.cyanSoft10,
  danger: TONE_COLORS.redSoft10Nexus,
  green: TONE_COLORS.emeraldSoft10Nexus,
  gray: TONE_COLORS.zincSoft10,
  indigo: TONE_COLORS.indigoSoft10,
  neutral: TONE_COLORS.zinc70060,
  orange: TONE_COLORS.amberSoft10Nexus,
  purple: TONE_COLORS.violetSoft10Nexus,
  red: TONE_COLORS.redSoft10Nexus,
  sky: TONE_COLORS.skySoft10,
  stock: TONE_COLORS.zinc70060,
  warning: TONE_COLORS.amberSoft10Nexus,
  yellow: TONE_COLORS.yellowSoft10
};

export const workflowMeta = {
  add_product: { icon: "plus", tone: "blue" },
  add_stock_unit: { icon: "package-plus", tone: "green" },
  receive_stock: { icon: "download", tone: "green" },
  create_delivery: { icon: "delivery", tone: "indigo" },
  create_reservation: { icon: "clock-3", tone: "warning" },
  create_issue: { icon: "user-check", tone: "indigo" },
  create_repair: { icon: "wrench", tone: "danger" },
  create_client_return: { icon: "reset", tone: "green" },
  add_supplier: { icon: "suppliers", tone: "purple" },
  add_client: { icon: "clients", tone: "blue" },
  stock_movement: { icon: "trending-up", tone: "neutral" }
};
