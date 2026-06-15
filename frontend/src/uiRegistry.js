import {
  BarChart3,
  BookOpen,
  Box,
  ClipboardList,
  Cpu,
  Database,
  Download,
  Handshake,
  LayoutDashboard,
  Layers,
  MoreHorizontal,
  Package,
  Plus,
  RotateCcw,
  Save,
  Settings,
  ShieldAlert,
  Truck,
  TrendingUp,
  TriangleAlert,
  Upload
} from "lucide-react";

export const iconComponents = {
  "bar-chart-3": BarChart3,
  "book-open": BookOpen,
  box: Box,
  clipboard: ClipboardList,
  cpu: Cpu,
  database: Database,
  download: Download,
  delivery: Truck,
  "layout-dashboard": LayoutDashboard,
  layers: Layers,
  more: MoreHorizontal,
  package: Package,
  plus: Plus,
  receiving: Download,
  reset: RotateCcw,
  save: Save,
  settings: Settings,
  "shield-alert": ShieldAlert,
  suppliers: Handshake,
  "trending-up": TrendingUp,
  "triangle-alert": TriangleAlert,
  upload: Upload
};

export const toneClasses = {
  blue: "bg-blue-500/10 text-nexus-blue",
  danger: "bg-red-500/10 text-nexus-red",
  green: "bg-emerald-500/10 text-nexus-green",
  neutral: "bg-zinc-700/60 text-zinc-300",
  orange: "bg-amber-500/10 text-nexus-orange",
  purple: "bg-violet-500/10 text-nexus-purple",
  red: "bg-red-500/10 text-nexus-red",
  stock: "bg-zinc-700/60 text-zinc-300",
  warning: "bg-amber-500/10 text-nexus-orange",
  yellow: "bg-yellow-500/10 text-yellow-400"
};

export const statusStyles = {
  available: "bg-emerald-500/15 text-nexus-green",
  inactive: "bg-red-500/20 text-red-300",
  reserved: "bg-blue-500/15 text-nexus-blue",
  returned: "bg-amber-500/15 text-nexus-orange",
  sold: "bg-zinc-600/40 text-zinc-300"
};
