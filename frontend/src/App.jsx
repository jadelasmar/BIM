import {
  BarChart3,
  BookOpen,
  ChevronRight,
  Cpu,
  Database,
  Download,
  LayoutDashboard,
  Layers,
  Plus,
  RefreshCw,
  Search,
  Settings,
  TrendingUp,
  TriangleAlert,
  Upload
} from "lucide-react";

import logoWhite from "./assets/brand/logo-white.svg";

const icons = {
  "bar-chart-3": BarChart3,
  "book-open": BookOpen,
  cpu: Cpu,
  database: Database,
  download: Download,
  "layout-dashboard": LayoutDashboard,
  layers: Layers,
  plus: Plus,
  settings: Settings,
  "trending-up": TrendingUp,
  "triangle-alert": TriangleAlert,
  upload: Upload
};

const toneClasses = {
  blue: "bg-blue-500/10 text-nexus-blue",
  green: "bg-emerald-500/10 text-nexus-green",
  neutral: "bg-zinc-700/60 text-zinc-300",
  orange: "bg-amber-500/10 text-nexus-orange",
  purple: "bg-violet-500/10 text-nexus-purple",
  stock: "bg-zinc-700/60 text-zinc-300",
  warning: "bg-amber-500/10 text-nexus-orange",
  yellow: "bg-yellow-500/10 text-yellow-400"
};

function Icon({ name, className = "h-4 w-4" }) {
  const Component = icons[name] || LayoutDashboard;
  return <Component className={className} aria-hidden="true" />;
}

function formatCount(value) {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "number") {
    return value.toLocaleString();
  }

  return value;
}

function Shell({ data }) {
  return (
    <div className="min-h-screen bg-nexus-page text-zinc-100 lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      <aside className="border-b border-nexus-line bg-black/95 px-4 py-5 lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="px-2">
          <img
            src={logoWhite}
            alt="BIM Nexus"
            className="h-8 w-auto max-w-[196px]"
          />
          <p className="mt-2 text-xs text-zinc-500">Internal IT Operations</p>
        </div>

        <nav className="mt-8 space-y-2" aria-label="Primary navigation">
          {data.navigation.primary.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="flex min-h-11 items-center gap-3 rounded-lg border border-nexus-line bg-nexus-panel px-3 text-sm font-semibold text-white"
            >
              <Icon name={item.icon} className="h-4 w-4 text-nexus-orange" />
              {item.name}
            </a>
          ))}
        </nav>

        <div className="my-5 h-px bg-nexus-line" />

        <nav className="space-y-2" aria-label="Settings navigation">
          {data.navigation.secondary.map((item) =>
            item.enabled && item.href ? (
              <a
                key={item.name}
                href={item.href}
                className="flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-semibold text-zinc-300 hover:bg-nexus-panel"
              >
                <Icon name={item.icon} className="h-4 w-4 text-zinc-500" />
                {item.name}
              </a>
            ) : (
              <span
                key={item.name}
                className="flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-semibold text-zinc-600"
              >
                <Icon name={item.icon} className="h-4 w-4" />
                {item.name}
              </span>
            )
          )}
        </nav>
      </aside>

      <main className="min-w-0 px-4 py-5 sm:px-6 lg:px-7">
        <Header data={data} />
        <KpiGrid items={data.kpis} />
        <Overview items={data.overview} />
        <Modules modules={data.modules} />

        <section className="mt-4 grid gap-4 xl:grid-cols-[260px_minmax(0,1fr)]">
          <QuickActions actions={data.quickActions} />
          <RecentActivity items={data.recentActivity} />
        </section>

        <section className="mt-4 grid gap-4 xl:grid-cols-3">
          <LowStockPanel />
          <RecentDeliveries />
          <RecentReceiving />
        </section>
      </main>
    </div>
  );
}

function Header({ data }) {
  return (
    <header className="flex flex-col gap-4 pb-5 xl:flex-row xl:items-start xl:justify-between">
      <div className="min-w-0">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">
          <span className="h-2 w-2 rounded-full border border-nexus-blue" />
          {data.hero.greeting}
        </p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
          {data.hero.title}
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          {data.hero.subtitle} - Built for{" "}
          <span className="font-semibold text-zinc-200">{data.hero.tenant}</span>
        </p>
        <label className="mt-4 flex h-10 max-w-xl items-center gap-3 rounded-lg border border-nexus-line bg-nexus-panel px-3 text-zinc-500">
          <Search className="h-4 w-4" aria-hidden="true" />
          <input
            className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-500"
            type="search"
            placeholder={data.hero.searchPlaceholder}
          />
        </label>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs">
        <span className="text-zinc-500">Last sync 20:11</span>
        <button className="inline-flex h-9 items-center gap-2 rounded-md px-2 font-semibold text-zinc-200 hover:bg-nexus-panel">
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </button>
        <QuickAddMenu actions={data.quickActions} />
        <form method="post" action={data.logoutHref}>
          <input type="hidden" name="csrfmiddlewaretoken" value={data.csrfToken} />
          <button className="h-9 rounded-md border border-nexus-line px-3 font-semibold text-zinc-300 hover:bg-nexus-panel">
            Log out
          </button>
        </form>
      </div>
    </header>
  );
}

function QuickAddMenu({ actions }) {
  return (
    <details className="relative">
      <summary className="inline-flex h-9 cursor-pointer list-none items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black marker:hidden">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Quick Add
      </summary>
      <div className="absolute right-0 z-20 mt-2 w-64 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
        {actions.map((action) =>
          action.enabled && action.href ? (
            <a
              key={action.label}
              href={action.href}
              className="flex items-start gap-3 border-b border-nexus-line px-3 py-3 last:border-b-0 hover:bg-nexus-panel2"
            >
              <ActionIcon name={action.icon} />
              <span>
                <span className="block text-sm font-semibold text-white">{action.label}</span>
                <span className="block text-xs text-zinc-500">{action.description}</span>
              </span>
            </a>
          ) : (
            <span
              key={action.label}
              className="flex items-start gap-3 border-b border-nexus-line px-3 py-3 opacity-50 last:border-b-0"
            >
              <ActionIcon name={action.icon} />
              <span>
                <span className="block text-sm font-semibold text-white">{action.label}</span>
                <span className="block text-xs text-zinc-500">{action.description}</span>
              </span>
            </span>
          )
        )}
      </div>
    </details>
  );
}

function KpiGrid({ items }) {
  return (
    <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4" aria-label="Key metrics">
      {items.map((item) => (
        <article
          key={item.label}
          className={`min-h-32 rounded-lg border bg-nexus-panel p-4 shadow-panel ${
            item.tone === "warning" ? "border-nexus-orange/70" : "border-nexus-line"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm text-zinc-400">{item.label}</p>
            <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
              <Icon name={item.icon} />
            </span>
          </div>
          <p className={`mt-6 text-3xl font-bold ${item.tone === "warning" ? "text-nexus-orange" : "text-white"}`}>
            {item.value}
          </p>
          <p className="mt-1 text-sm text-zinc-400">{item.detail}</p>
          <p className={`mt-2 text-xs font-semibold ${item.tone === "stock" ? "text-nexus-red" : "text-nexus-green"}`}>
            {item.trend}
          </p>
        </article>
      ))}
    </section>
  );
}

function Overview({ items }) {
  return (
    <section className="mt-5" aria-label="System overview">
      <SectionTitle title="System Overview" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        {items.map((item) => (
          <article key={item.label} className="flex items-center gap-3 rounded-lg border border-nexus-line bg-nexus-panel p-4">
            <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
              <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-bold text-white">{item.value}</p>
              <p className="text-xs text-zinc-300">{item.label}</p>
              <p className="text-xs text-zinc-500">{item.detail}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Modules({ modules }) {
  return (
    <section className="mt-5" aria-label="Modules">
      <SectionTitle title="Modules" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {modules.map((module) => {
          const content = (
            <>
              <span className={`inline-flex rounded-lg p-3 ${toneClasses[module.tone] || toneClasses.neutral}`}>
                <Icon name={module.icon} className="h-5 w-5" />
              </span>
              <h2 className="mt-4 text-sm font-bold text-white">{module.name}</h2>
              <p className="mt-1 min-h-10 text-sm text-zinc-400">{module.description}</p>
              <div className="mt-4 flex items-center justify-between border-t border-nexus-line pt-3 text-xs">
                <span className="font-mono text-zinc-500">
                  {module.count !== null && module.count !== undefined
                    ? `${formatCount(module.count)} ${module.meta}`
                    : module.meta}
                </span>
                <span className="inline-flex items-center gap-1 font-semibold text-nexus-orange">
                  Open <ChevronRight className="h-4 w-4" />
                </span>
              </div>
            </>
          );

          if (module.enabled && module.href) {
            return (
              <a key={module.name} href={module.href} className="rounded-lg border border-nexus-line bg-nexus-panel p-4 hover:border-nexus-orange/80">
                {content}
              </a>
            );
          }

          return (
            <article key={module.name} className="rounded-lg border border-nexus-line bg-nexus-panel p-4 opacity-75">
              {content}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function QuickActions({ actions }) {
  return (
    <aside className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Quick Actions" />
      <div className="space-y-2 p-3">
        {actions.map((action, index) => {
          const className = `flex w-full items-center gap-3 rounded-lg border px-3 py-3 text-left ${
            index === 0
              ? "border-nexus-orange/60 bg-nexus-orange/10"
              : "border-transparent"
          } ${action.enabled ? "hover:bg-nexus-panel2" : "opacity-50"}`;

          const inner = (
            <>
              <ActionIcon name={action.icon} />
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-bold text-white">{action.label}</span>
                <span className="block text-xs text-zinc-500">{action.description}</span>
              </span>
              <ChevronRight className="h-4 w-4 text-zinc-600" aria-hidden="true" />
            </>
          );

          return action.enabled && action.href ? (
            <a key={action.label} href={action.href} className={className}>
              {inner}
            </a>
          ) : (
            <button key={action.label} type="button" disabled className={className}>
              {inner}
            </button>
          );
        })}
      </div>
    </aside>
  );
}

function RecentActivity({ items }) {
  const rows = items.length
    ? items
    : [
        {
          reference: "PO-2024-0891",
          type: "Stock Received",
          user: "Admin workflow",
          date: "Today, 08:14",
          status: "Completed",
          status_class: "available"
        },
        {
          reference: "AST-2024-106",
          type: "Asset Assigned",
          user: "Ahmad Al-Rashidi",
          date: "Today, 07:52",
          status: "Completed",
          status_class: "available"
        },
        {
          reference: "DLV-2024-044",
          type: "Delivery Created",
          user: "Admin workflow",
          date: "Today, 07:30",
          status: "Completed",
          status_class: "available"
        }
      ];

  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Activity" action="View all" />
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Ref</th>
              <th className="px-4 py-3 font-medium">Activity</th>
              <th className="px-4 py-3 font-medium">Performed by</th>
              <th className="px-4 py-3 font-medium">When</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={`${item.reference}-${item.type}`} className="border-t border-nexus-line">
                <td className="px-4 py-4 font-mono text-xs text-nexus-orange">{item.reference}</td>
                <td className="px-4 py-4 font-semibold text-white">{item.type}</td>
                <td className="px-4 py-4 text-zinc-400">{item.user}</td>
                <td className="px-4 py-4 text-zinc-400">{String(item.date)}</td>
                <td className="px-4 py-4">
                  <Status status={item.status} statusClass={item.status_class} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function LowStockPanel() {
  const rows = [
    ["HP LaserJet Toner 26", "Office A", "Critical", "2", "red"],
    ["Cat6 Ethernet Cable 2m", "Server Room", "Critical", "5", "red"],
    ["USB Keyboard Dell KB21", "Office B", "Warning", "3", "orange"],
    ["Wireless Mouse Logitech M185", "Office B", "Info", "8", "blue"]
  ];

  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Low Stock Alerts" badge="4" />
      <ListRows rows={rows} cta="Reorder all items" />
    </section>
  );
}

function RecentDeliveries() {
  const rows = [
    ["DLV-2024-044", "Office A - Floor 2", "Delivered", "Today, 07:30", "green"],
    ["DLV-2024-043", "Server Room - Site 3", "Delivered", "Yesterday, 14:20", "green"],
    ["DLV-2024-042", "Office B - Reception", "Partial", "Yesterday, 11:05", "orange"],
    ["DLV-2024-041", "Warehouse - Site 1", "Failed", "2 days ago", "red"]
  ];

  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Deliveries" action="View all" />
      <ListRows rows={rows} cta="Create delivery note" />
    </section>
  );
}

function RecentReceiving() {
  const rows = [
    ["PO-2024-0891", "Gulf Networks LLC", "+24 units", "Today, 08:14", "green"],
    ["PO-2024-0890", "Al Futtaim Tech", "+6 units", "Yesterday, 15:40", "green"],
    ["PO-2024-0889", "Emitac Group", "+12 units", "Yesterday, 09:00", "green"],
    ["PO-2024-0888", "Gulf Networks LLC", "+30 units", "2 days ago", "orange"]
  ];

  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Receiving" action="View all" />
      <ListRows rows={rows} cta="Record new receipt" />
    </section>
  );
}

function ListRows({ rows, cta }) {
  return (
    <div>
      {rows.map(([title, detail, status, meta, tone]) => (
        <div key={`${title}-${detail}`} className="flex items-center justify-between gap-3 border-t border-nexus-line px-4 py-3">
          <div>
            <p className="text-sm font-semibold text-white">{title}</p>
            <p className="mt-1 text-xs text-zinc-500">{detail}</p>
          </div>
          <div className="text-right">
            <p className={`text-xs font-bold ${tone === "red" ? "text-nexus-red" : tone === "orange" ? "text-nexus-orange" : tone === "blue" ? "text-nexus-blue" : "text-nexus-green"}`}>
              {status}
            </p>
            <p className="mt-1 text-xs text-zinc-500">{meta}</p>
          </div>
        </div>
      ))}
      <button className="w-full border-t border-nexus-line px-4 py-4 text-sm font-semibold text-nexus-orange hover:bg-nexus-panel2">
        {cta}
      </button>
    </div>
  );
}

function Status({ status, statusClass }) {
  const className =
    statusClass === "damaged"
      ? "text-nexus-red"
      : statusClass === "reserved"
        ? "text-nexus-orange"
        : "text-nexus-green";

  return <span className={`text-xs font-semibold ${className}`}>{status}</span>;
}

function PanelHeader({ title, action, badge }) {
  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3">
      <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">{title}</h2>
      {badge ? (
        <span className="rounded-full bg-nexus-orange px-2 py-1 text-xs font-bold text-white">
          {badge}
        </span>
      ) : null}
      {action ? (
        <button className="text-xs font-semibold text-nexus-orange">{action}</button>
      ) : null}
    </div>
  );
}

function SectionTitle({ title }) {
  return <h2 className="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">{title}</h2>;
}

function ActionIcon({ name }) {
  return (
    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-zinc-800 text-nexus-orange">
      <Icon name={name} className="h-5 w-5" />
    </span>
  );
}

export default function App({ initialData }) {
  if (!initialData) {
    return (
      <div className="grid min-h-screen place-items-center bg-nexus-page text-white">
        BIM Nexus could not load dashboard data.
      </div>
    );
  }

  return <Shell data={initialData} />;
}
