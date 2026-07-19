import { TONE_COLORS } from "./toneColors";

export const statusStyles = {
  available: TONE_COLORS.greenSoft15,
  cancelled: TONE_COLORS.redSoft15,
  delivered: TONE_COLORS.blueSoft15,
  inactive: TONE_COLORS.zincSoft15,
  issued: TONE_COLORS.indigoSoft15,
  low_stock: TONE_COLORS.amberSoft15Amber,
  out_of_stock: TONE_COLORS.redSoft15,
  received: TONE_COLORS.emeraldSoft15,
  released: TONE_COLORS.cyanSoft15,
  repair: TONE_COLORS.redSoft15,
  reserved: TONE_COLORS.amberSoft15Amber,
  sold: TONE_COLORS.purpleSoft15,
  transfer: TONE_COLORS.skySoft15
};

export const statusMeta = {
  active: { icon: "check-circle-2", className: statusStyles.available },
  available: { icon: "check-circle-2", className: statusStyles.available },
  cancelled: { icon: "package-x", className: statusStyles.cancelled },
  delivered: { icon: "package-check", className: statusStyles.delivered },
  inactive: { icon: "package-x", className: statusStyles.inactive },
  issued: { icon: "user-check", className: statusStyles.issued },
  low_stock: { icon: "triangle-alert", className: statusStyles.low_stock },
  out_of_stock: { icon: "package-x", className: statusStyles.out_of_stock },
  received: { icon: "inbox", className: statusStyles.received },
  released: { icon: "reset", className: statusStyles.released },
  repair: { icon: "wrench", className: statusStyles.repair },
  reserved: { icon: "clock-3", className: statusStyles.reserved },
  sold: { icon: "shopping-bag", className: statusStyles.sold },
  transfer: { icon: "arrow-right-left", className: statusStyles.transfer }
};
