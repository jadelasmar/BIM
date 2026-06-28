export const statusStyles = {
  available: "bg-green-500/15 text-green-400",
  damaged: "bg-red-500/15 text-red-400",
  delivered: "bg-blue-500/15 text-blue-400",
  inactive: "bg-zinc-500/15 text-zinc-400",
  issued: "bg-indigo-500/15 text-indigo-400",
  low_stock: "bg-amber-500/15 text-amber-400",
  out_of_stock: "bg-red-500/15 text-red-400",
  received: "bg-emerald-500/15 text-emerald-400",
  reserved: "bg-amber-500/15 text-amber-400",
  returned: "bg-cyan-500/15 text-cyan-400",
  sold: "bg-purple-500/15 text-purple-400",
  transfer: "bg-sky-500/15 text-sky-400"
};

export const statusMeta = {
  active: { icon: "check-circle-2", className: statusStyles.available },
  available: { icon: "check-circle-2", className: statusStyles.available },
  damaged: { icon: "package-x", className: statusStyles.damaged },
  delivered: { icon: "package-check", className: statusStyles.delivered },
  inactive: { icon: "package-x", className: statusStyles.inactive },
  issued: { icon: "user-check", className: statusStyles.issued },
  low_stock: { icon: "triangle-alert", className: statusStyles.low_stock },
  out_of_stock: { icon: "package-x", className: statusStyles.out_of_stock },
  received: { icon: "package-plus", className: statusStyles.received },
  reserved: { icon: "clock-3", className: statusStyles.reserved },
  returned: { icon: "reset", className: statusStyles.returned },
  sold: { icon: "shopping-bag", className: statusStyles.sold },
  transfer: { icon: "arrow-right-left", className: statusStyles.transfer }
};
