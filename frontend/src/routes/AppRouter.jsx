import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Camera,
  ChevronRight,
  Edit3,
  Eye,
  Filter,
  Menu,
  Moon,
  Package,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Settings,
  Sun,
  X
} from "../constants/icons";

import Icon from "../components/common/Icon";
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  EmptyState,
  Input,
  SearchBar
} from "../components/ui";
import { statusMeta } from "../constants/statusStyles";
import { toneClasses, workflowMeta } from "../constants/uiRegistry";
import { DEFAULT_THEME_STORAGE_KEY, applyTheme, currentTheme } from "../hooks/useTheme";
import { LoginPage, PasswordSetupPage } from "../pages/auth/AuthPages";
import { formatCount, formatCurrency, formatDate } from "../utils/formatters";
import logoPrimary from "../assets/brand/logo-primary.svg";
import logoWhite from "../assets/brand/logo-white.svg";

function greetingPeriodForHour(hour) {
  if (hour >= 5 && hour < 12) {
    return "Good morning";
  }
  if (hour >= 12 && hour < 17) {
    return "Good afternoon";
  }
  if (hour >= 17 && hour < 22) {
    return "Good evening";
  }
  return "Good night";
}

function browserGreeting(name) {
  return `${greetingPeriodForHour(new Date().getHours())}, ${name || "User"}`;
}

function Shell({ data, children, onRefresh }) {
  const secondaryNavigation = data.navigation.secondary || [];
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);

  return (
    <div className="min-h-screen bg-nexus-page text-zinc-100 lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      {sidebarOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/70 lg:hidden"
          aria-label="Close navigation"
          onClick={closeSidebar}
        />
      ) : null}

      <Sidebar
        data={data}
        secondaryNavigation={secondaryNavigation}
        isOpen={sidebarOpen}
        onClose={closeSidebar}
      />

      <main className="min-w-0 px-4 py-5 sm:px-6 lg:px-7">
        <Topbar
          data={data}
          onRefresh={onRefresh}
          onOpenSidebar={() => setSidebarOpen(true)}
        />
        {children}
      </main>
    </div>
  );
}

function Sidebar({ data, secondaryNavigation, isOpen, onClose }) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 w-[min(82vw,248px)] overflow-y-auto border-r border-nexus-line bg-black/95 px-4 py-5 transition-transform duration-200 lg:static lg:z-auto lg:block lg:min-h-screen lg:w-auto lg:translate-x-0 ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
      aria-label="Main navigation"
    >
      <div className="flex items-start justify-between gap-3 px-2">
        <div>
          <a href="/" className="inline-flex" aria-label="BIM Nexus Command Center" onClick={onClose}>
            <img src={logoWhite} alt="BIM Nexus" className="bim-sidebar-logo bim-sidebar-logo-dark h-8 w-auto max-w-[196px]" />
            <img src={logoPrimary} alt="BIM Nexus" className="bim-sidebar-logo bim-sidebar-logo-light h-8 w-auto max-w-[196px]" />
          </a>
          <p className="mt-2 text-xs text-zinc-500">Internal IT Operations</p>
        </div>
        <button
          type="button"
          className="grid h-9 w-9 shrink-0 place-items-center rounded-md border border-nexus-line text-zinc-300 hover:bg-nexus-panel lg:hidden"
          aria-label="Close navigation"
          onClick={onClose}
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <nav className="mt-8 space-y-2" aria-label="Primary navigation">
        {data.navigation.primary.map((item) =>
          item.enabled === false || !item.href ? (
            <span
              key={item.name}
              className="flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-semibold text-zinc-600"
            >
              <Icon name={item.icon} className="h-4 w-4" />
              {item.name}
            </span>
          ) : (
            <a
              key={item.name}
              href={item.href}
              onClick={onClose}
              className={`group flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-semibold ${
                item.active
                  ? "border border-nexus-line bg-nexus-panel text-white"
                  : "text-zinc-400 hover:bg-nexus-panel hover:text-zinc-200"
              }`}
            >
              <Icon
                name={item.icon}
                className={`h-4 w-4 ${item.active ? "text-nexus-orange" : "text-zinc-500 group-hover:text-zinc-300"}`}
              />
              {item.name}
            </a>
          )
        )}
      </nav>

      {secondaryNavigation.length ? (
        <>
          <div className="my-5 h-px bg-nexus-line" />

          <nav className="space-y-2" aria-label="Secondary navigation">
            {secondaryNavigation.map((item) =>
              item.enabled && item.href ? (
                <a
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`group flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-semibold ${
                    item.active
                      ? "border border-nexus-line bg-nexus-panel text-white"
                      : "text-zinc-400 hover:bg-nexus-panel hover:text-zinc-200"
                  }`}
                >
                  <Icon
                    name={item.icon}
                    className={`h-4 w-4 ${item.active ? "text-nexus-orange" : "text-zinc-500 group-hover:text-zinc-300"}`}
                  />
                  {item.name}
                </a>
              ) : (
                <span
                  key={item.name}
                  className="flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-semibold text-zinc-600"
                  title={item.detail || undefined}
                >
                  <Icon name={item.icon} className="h-4 w-4" />
                  {item.name}
                </span>
              )
            )}
          </nav>
        </>
      ) : null}
    </aside>
  );
}

function Topbar({ data, onRefresh, onOpenSidebar }) {
  return (
    <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-nexus-line pb-4 text-xs">
      <Button
        type="button"
        onClick={onOpenSidebar}
        className="lg:hidden"
        aria-label="Open navigation"
        variant="outline"
      >
        <Menu className="h-4 w-4" aria-hidden="true" />
        Menu
      </Button>
      <div className="flex flex-wrap items-center justify-end gap-3">
        <ThemeToggle storageKey={data.theme?.storageKey} />
        <Button
          type="button"
          onClick={onRefresh || (() => window.location.reload())}
          variant="outline"
        >
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </Button>
        <QuickAddMenu actions={data.quickActions || []} />
        <LogoutForm data={data} />
      </div>
    </div>
  );
}

function ThemeToggle({ storageKey = DEFAULT_THEME_STORAGE_KEY }) {
  const [theme, setThemeState] = useState(() => currentTheme());

  useEffect(() => {
    function handleThemeChange(event) {
      setThemeState(event.detail === "light" ? "light" : "dark");
    }

    document.addEventListener("bim-nexus-theme-change", handleThemeChange);
    return () => document.removeEventListener("bim-nexus-theme-change", handleThemeChange);
  }, []);

  const isLight = theme === "light";

  return (
    <Button
      type="button"
      onClick={() => setThemeState(applyTheme(isLight ? "dark" : "light", storageKey))}
      aria-label="Toggle dark and light mode"
      title="Toggle dark and light mode"
      variant="outline"
    >
      {isLight ? <Sun className="h-4 w-4" aria-hidden="true" /> : <Moon className="h-4 w-4" aria-hidden="true" />}
      {isLight ? "Light" : "Dark"}
    </Button>
  );
}

function CommandCenter({ data }) {
  const [dashboardData, setDashboardData] = useState(data);
  const commandCenterEndpoint = data.api?.commandCenter;
  const pollIntervalMs = Number(data.pollIntervalMs) || 60000;

  const refreshDashboardData = useCallback(async () => {
    if (!commandCenterEndpoint) {
      return;
    }

    try {
      const response = await fetch(commandCenterEndpoint, {
        headers: { Accept: "application/json" }
      });

      if (!response.ok) {
        return;
      }

      setDashboardData(await response.json());
    } catch {
      // Keep the current dashboard data if a background refresh fails.
    }
  }, [commandCenterEndpoint]);

  useEffect(() => {
    if (!commandCenterEndpoint) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      if (!document.hidden) {
        refreshDashboardData();
      }
    }, pollIntervalMs);
    return () => window.clearInterval(intervalId);
  }, [commandCenterEndpoint, pollIntervalMs, refreshDashboardData]);

  return (
    <Shell data={dashboardData} onRefresh={refreshDashboardData}>
      <Header data={dashboardData} />
      <KpiGrid items={dashboardData.kpis} />
      <Overview items={dashboardData.overview} />

      <section className="mt-4">
        <RecentActivity items={dashboardData.recentActivity} />
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-2">
        <RecentDeliveries items={dashboardData.recentDeliveries} />
        <RecentReceiving items={dashboardData.recentReceiving} />
      </section>
    </Shell>
  );
}
function SettingsPage({ data }) {
  const storageKey = data.theme?.storageKey || "bim-nexus-theme";
  const [theme, setThemeState] = useState(() => currentTheme());

  useEffect(() => {
    function handleThemeChange(event) {
      setThemeState(event.detail === "light" ? "light" : "dark");
    }

    document.addEventListener("bim-nexus-theme-change", handleThemeChange);
    return () => document.removeEventListener("bim-nexus-theme-change", handleThemeChange);
  }, []);

  function setTheme(nextTheme) {
    setThemeState(applyTheme(nextTheme, storageKey));
  }

  return (
    <Shell data={data}>
      <header className="mb-5">
        <h1 className="bim-page-title">Settings</h1>
        <p className="bim-page-description">Manage BIM Nexus display preferences.</p>
      </header>

      <section className="max-w-xl rounded-lg border border-nexus-line bg-nexus-panel p-5">
        <div className="flex items-start gap-3 border-b border-nexus-line pb-5">
          <span className="rounded-lg bg-nexus-orange/10 p-2 text-nexus-orange">
            <Settings className="h-5 w-5" />
          </span>
          <div>
            <h2 className="font-bold text-white">Appearance</h2>
            <p className="mt-1 text-sm text-zinc-500">Choose the interface theme used across BIM Nexus pages.</p>
          </div>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {[
            ["dark", "Dark Mode", "Black operational dashboard"],
            ["light", "Light Mode", "Bright administrative interface"]
          ].map(([value, label, detail]) => (
            <button
              key={value}
              type="button"
              onClick={() => setTheme(value)}
              className={`rounded-lg border p-4 text-left ${
                theme === value
                  ? "border-nexus-orange bg-nexus-orange/10"
                  : "border-nexus-line bg-nexus-panel2"
              }`}
            >
              <span className="block text-sm font-bold text-white">{label}</span>
              <span className="mt-1 block text-xs text-zinc-500">{detail}</span>
            </button>
          ))}
        </div>

        {data.user?.canAccessAdmin ? (
          <a
            href="/admin/"
            className="mt-5 inline-flex h-10 items-center rounded-md border border-nexus-line px-4 text-sm font-semibold text-zinc-200 hover:bg-nexus-panel2"
          >
            Open Django Admin
          </a>
        ) : null}
      </section>
    </Shell>
  );
}

function PlaceholderPage({ data, title }) {
  return (
    <Shell data={data}>
      <header className="mb-5">
        <h1 className="bim-page-title">{title}</h1>
      </header>

      <section className="rounded-lg border border-nexus-line bg-nexus-panel p-6">
        <p className="text-sm text-zinc-400">This module will be implemented in a later phase.</p>
      </section>
    </Shell>
  );
}

const MASTER_DATA_CONFIG = {
  suppliers: {
    title: "Suppliers",
    singular: "Supplier",
    icon: "suppliers",
    apiKey: "suppliers",
    routeKey: "suppliers",
    newRouteKey: "supplierNew",
    createPermission: "canCreateSupplier",
    editPermission: "canEditSupplier",
    path: "/suppliers/",
    searchPlaceholder: "Search suppliers by name, contact, phone, or email...",
    description: "Maintain supplier source details for receiving stock."
  },
  clients: {
    title: "Clients",
    singular: "Client",
    icon: "clients",
    apiKey: "clients",
    routeKey: "clients",
    newRouteKey: "clientNew",
    createPermission: "canCreateClient",
    editPermission: "canEditClient",
    path: "/clients/",
    searchPlaceholder: "Search clients by name, contact, phone, or email...",
    description: "Maintain client details used by delivery and return records."
  }
};

function MasterDataListPage({ data, type }) {
  const config = MASTER_DATA_CONFIG[type];
  const canCreate = Boolean(data.permissions?.[config.createPermission]);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadRecords() {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set("q", query.trim());
        const endpoint = params.toString()
          ? `${data.api[config.apiKey]}?${params.toString()}`
          : data.api[config.apiKey];
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Could not load ${config.title.toLowerCase()}.`);
        }
        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
    return () => controller.abort();
  }, [config.apiKey, config.title, data.api, query]);

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">{config.title}</h1>
          <p className="bim-page-description">{config.description}</p>
        </div>
        {canCreate ? (
          <Button as="a" href={data.routes[config.newRouteKey]} variant="primary">
            <Plus className="h-4 w-4" />
            Add {config.singular}
          </Button>
        ) : null}
      </header>

      <section className="rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={config.searchPlaceholder}
          />
          <span className="text-xs text-zinc-500">{records.length} active</span>
        </div>
      </section>

      <MasterDataTable config={config} records={records} loading={loading} error={error} />
    </Shell>
  );
}

function MasterDataTable({ config, records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">{config.singular}</th>
              <th className="px-4 py-3 font-medium">Contact</th>
              <th className="px-4 py-3 font-medium">Phone</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message={`Loading ${config.title.toLowerCase()}...`} />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`${config.path}${record.id}/`} className="font-semibold text-white hover:text-nexus-orange">
                      {record.name}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">{record.notes || "Operational master data"}</p>
                  </td>
                  <td className="px-4 py-4 text-zinc-300">{record.contact_person || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{record.phone || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{record.email || "-"}</td>
                  <td className="px-4 py-4">
                    <Status status={record.isactive ? "Active" : "Inactive"} statusClass={record.isactive ? "available" : "inactive"} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title={`No ${config.title.toLowerCase()} yet.`}
                    description={`Add a ${config.singular.toLowerCase()} to use it in stock workflows.`}
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function MasterDataDetailPage({ data, type, isNew = false }) {
  const config = MASTER_DATA_CONFIG[type];
  const recordId = isNew ? "" : (data.currentPath || window.location.pathname).match(new RegExp(`${config.path}(\\d+)/`))?.[1];
  const canSave = Boolean(data.permissions?.[isNew ? config.createPermission : config.editPermission]);
  const [form, setForm] = useState({
    name: "",
    contact_person: "",
    phone: "",
    email: "",
    notes: "",
    isactive: true
  });
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isNew || !recordId) return undefined;
    const controller = new AbortController();

    async function loadRecord() {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(`${data.api[config.apiKey]}${recordId}/`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`${config.singular} was not found.`);
        }
        const record = await response.json();
        setForm({
          name: record.name || "",
          contact_person: record.contact_person || "",
          phone: record.phone || "",
          email: record.email || "",
          notes: record.notes || "",
          isactive: record.isactive !== false
        });
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadRecord();
    return () => controller.abort();
  }, [config.apiKey, config.singular, data.api, isNew, recordId]);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function saveRecord() {
    if (!canSave) return;
    setSaving(true);
    setError("");
    try {
      if (!form.name.trim()) {
        throw new Error(`${config.singular} name is required.`);
      }
      const endpoint = isNew ? data.api[config.apiKey] : `${data.api[config.apiKey]}${recordId}/`;
      const response = await fetch(endpoint, {
        method: isNew ? "POST" : "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify(form)
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || `Could not save ${config.singular.toLowerCase()}.`);
      }
      const saved = await response.json();
      window.location.assign(`${config.path}${saved.id}/`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href={data.routes[config.routeKey]} className="mb-2 inline-flex text-sm font-semibold text-nexus-orange hover:text-orange-300">
            Back to {config.title}
          </a>
          <h1 className="bim-page-title">{isNew ? `Add ${config.singular}` : config.singular}</h1>
          <p className="bim-page-description">{config.description}</p>
        </div>
        {canSave ? (
          <Button type="button" variant="primary" loading={saving} onClick={saveRecord}>
            <Save className="h-4 w-4" />
            Save {config.singular}
          </Button>
        ) : null}
      </header>

      {error ? (
        <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
          {error}
        </div>
      ) : null}
      {!canSave ? (
        <div className="mb-4 rounded-lg border border-nexus-line bg-nexus-panel2 px-4 py-3 text-sm font-semibold text-zinc-300">
          You can view this {config.singular.toLowerCase()}, but your role cannot {isNew ? "create" : "edit"} {config.title.toLowerCase()}.
        </div>
      ) : null}

      {loading ? (
        <section className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-sm text-zinc-500">
          Loading {config.singular.toLowerCase()}...
        </section>
      ) : (
        <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
          <FormSection icon={config.icon} title={`${config.singular} Information`} subtitle="Operational master data only. No accounting or CRM behavior is created here.">
            <div className="grid gap-5 md:grid-cols-2">
              <Field label={`${config.singular} Name`} required>
                <TextInput disabled={!canSave} value={form.name} onChange={(value) => updateField("name", value)} placeholder={`${config.singular} name`} />
              </Field>
              <Field label="Contact Person">
                <TextInput disabled={!canSave} value={form.contact_person} onChange={(value) => updateField("contact_person", value)} placeholder="Contact name" />
              </Field>
              <Field label="Phone">
                <TextInput disabled={!canSave} value={form.phone} onChange={(value) => updateField("phone", value)} placeholder="Phone number" />
              </Field>
              <Field label="Email">
                <TextInput disabled={!canSave} type="email" value={form.email} onChange={(value) => updateField("email", value)} placeholder="Email address" />
              </Field>
            </div>
            <div className="mt-5">
              <Field label="Notes">
                <TextInput disabled={!canSave} value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Internal notes" />
              </Field>
            </div>
            <label className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-zinc-300">
              <input
                type="checkbox"
                disabled={!canSave}
                checked={form.isactive}
                onChange={(event) => updateField("isactive", event.target.checked)}
                className="h-4 w-4 rounded border-nexus-line bg-black"
              />
              Active
            </label>
          </FormSection>
        </section>
      )}
    </Shell>
  );
}

function OperationsPage({ data }) {
  const workflows = [
    {
      title: "Receive Stock",
      detail: "Record supplier receipts with delivery or reference details.",
      href: data.routes.receiveStock,
      enabled: data.quickActions.some((action) => action.label === "Receive Stock" && action.enabled),
      icon: workflowMeta.receive_stock.icon,
      tone: workflowMeta.receive_stock.tone
    },
    {
      title: "Add Unit",
      detail: "Create manual stock units from count or correction.",
      href: data.routes.addStockUnit,
      enabled: data.quickActions.some((action) => action.label === "Add Unit" && action.enabled),
      icon: workflowMeta.add_stock_unit.icon,
      tone: workflowMeta.add_stock_unit.tone
    },
    {
      title: "Create Delivery",
      detail: "Dispatch available stock units.",
      href: data.routes.createDelivery,
      enabled: data.quickActions.some((action) => action.label === "Create Delivery" && action.enabled),
      icon: workflowMeta.create_delivery.icon,
      tone: workflowMeta.create_delivery.tone
    },
    {
      title: "Create Reservation",
      detail: "Hold available units for a person, client, or job.",
      href: data.routes.createReservation,
      enabled: data.quickActions.some((action) => action.label === "Create Reservation" && action.enabled),
      icon: workflowMeta.create_reservation.icon,
      tone: workflowMeta.create_reservation.tone
    },
    {
      title: "Create Issue",
      detail: "Temporarily issue available units that are expected to come back.",
      href: data.routes.createIssue,
      enabled: data.quickActions.some((action) => action.label === "Create Issue" && action.enabled),
      icon: workflowMeta.create_issue.icon,
      tone: workflowMeta.create_issue.tone
    },
    {
      title: "Create Repair",
      detail: "Move available units into repair, testing, or diagnosis.",
      href: data.routes.createRepair,
      enabled: data.quickActions.some((action) => action.label === "Create Repair" && action.enabled),
      icon: workflowMeta.create_repair.icon,
      tone: workflowMeta.create_repair.tone
    },
    {
      title: "Create Client Return",
      detail: "Record sold stock that came back from a client.",
      href: data.routes.createClientReturn,
      enabled: data.quickActions.some((action) => action.label === "Create Client Return" && action.enabled),
      icon: workflowMeta.create_client_return.icon,
      tone: workflowMeta.create_client_return.tone
    },
    {
      title: "Stock Movement",
      detail: "Manual adjustments and exceptions.",
      href: null,
      enabled: false,
      icon: workflowMeta.stock_movement.icon,
      tone: workflowMeta.stock_movement.tone
    }
  ];
  const visibleWorkflows = workflows.filter((workflow) => workflow.enabled || !workflow.href);

  return (
    <Shell data={data}>
      <header className="mb-5">
        <h1 className="bim-page-title">Operations</h1>
        <p className="bim-page-description">Run stock entry and stock exit workflows.</p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {visibleWorkflows.map((workflow) => {
          const content = (
            <>
              <span className={`inline-flex rounded-lg p-3 ${toneClasses[workflow.tone] || toneClasses.neutral}`}>
                <Icon name={workflow.icon} className="h-5 w-5" />
              </span>
              <h2 className={`mt-4 text-base font-bold ${workflow.enabled ? "text-white" : "text-zinc-500"}`}>
                {workflow.title}
              </h2>
              <p className={`mt-2 text-sm ${workflow.enabled ? "text-zinc-400" : "text-zinc-600"}`}>
                {workflow.detail}
              </p>
              <div className="mt-5 border-t border-nexus-line pt-3 text-sm font-semibold">
                <span className={workflow.enabled ? "text-nexus-orange" : "text-zinc-600"}>
                  {workflow.enabled ? "Open" : "Pending"}
                </span>
              </div>
            </>
          );

          return workflow.enabled && workflow.href ? (
            <a key={workflow.title} href={workflow.href} className="rounded-lg border border-nexus-line bg-nexus-panel p-5 hover:border-nexus-orange/80">
              {content}
            </a>
          ) : (
            <article key={workflow.title} aria-disabled="true" className="cursor-not-allowed rounded-lg border border-nexus-line bg-nexus-panel p-5 opacity-45 grayscale">
              {content}
            </article>
          );
        })}
      </section>
    </Shell>
  );
}

function ReceivingRecordsPage({ data }) {
  const canReceiveStock = Boolean(data.permissions?.canReceiveStock);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());

    async function loadReceivingRecords() {
      setLoading(true);
      setError("");
      try {
        const endpoint = params.toString()
          ? `${data.api.receivingRecords}?${params.toString()}`
          : data.api.receivingRecords;
        const response = await fetch(endpoint, { signal: controller.signal });

        if (!response.ok) {
          throw new Error("Could not load receiving records.");
        }

        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadReceivingRecords();
    return () => controller.abort();
  }, [data.api.receivingRecords, query]);

  const totalQuantity = records.reduce((sum, record) => sum + Number(record.total_quantity || 0), 0);
  const manualCount = records.filter((record) => !record.supplier_name).length;
  const recentRecord = records[0];
  const receivingKpis = [
    {
      label: "Receiving Records",
      value: formatCount(records.length),
      detail: "stock entry records",
      icon: "download",
      tone: "green"
    },
    {
      label: "Received Quantity",
      value: formatCount(totalQuantity),
      detail: "items recorded",
      icon: "layers",
      tone: "blue"
    },
    {
      label: "Supplier Sources",
      value: formatCount(records.length - manualCount),
      detail: `${formatCount(manualCount)} manual entries`,
      icon: "suppliers",
      tone: "purple"
    },
    {
      label: "Latest Receipt",
      value: recentRecord ? formatDate(recentRecord.received_date) : "-",
      detail: recentRecord?.receiving_number || "no receiving yet",
      icon: "clock",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Receiving Records</h1>
          <p className="bim-page-description">Review operational stock-entry records.</p>
        </div>
        {canReceiveStock ? (
          <Button as="a" href={data.routes.receiveStock} variant="primary">
            <Plus className="h-4 w-4" />
            Receive Stock
          </Button>
        ) : null}
      </header>

      <KpiGrid items={receivingKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search receiving number, supplier, reference, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <ReceivingRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function ReceivingRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Receiving</th>
              <th className="px-4 py-3 font-medium">Source</th>
              <th className="px-4 py-3 font-medium">Received Date</th>
              <th className="px-4 py-3 font-medium">Reference</th>
              <th className="px-4 py-3 font-medium">Items</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading receiving records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <p className="font-mono text-xs font-bold text-nexus-orange">{record.receiving_number}</p>
                    <p className="mt-1 text-xs text-zinc-500">Created by {record.created_by_name || "-"}</p>
                  </td>
                  <td className="px-4 py-4">
                    <p className="font-semibold text-white">{record.supplier_name || "Manual source"}</p>
                    <p className="mt-1 text-xs text-zinc-500">
                      {record.supplier_name ? "Supplier receiving" : "Direct stock entry"}
                    </p>
                  </td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.received_date)}</td>
                  <td className="px-4 py-4 font-mono text-xs text-zinc-400">{record.reference_number || "-"}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_quantity || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={record.status === "cancelled" || !record.isactive ? "Cancelled" : "Recorded"} statusClass={record.status === "cancelled" || !record.isactive ? "inactive" : "received"} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No receiving records yet."
                    description="Use Receive Stock to create the first operational receiving record."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ReceivingRecordDetailPage({ data }) {
  const receivingId = (data.currentPath || window.location.pathname).match(/\/operations\/receiving\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [editing, setEditing] = useState(false);
  const [savingCorrection, setSavingCorrection] = useState(false);
  const [correctionError, setCorrectionError] = useState("");
  const [correctionMessage, setCorrectionMessage] = useState("");
  const [correctionForm, setCorrectionForm] = useState({
    supplier: "",
    receivedDate: "",
    referenceNumber: "",
    notes: "",
    items: []
  });
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState("");

  const isCancelled = record?.status === "cancelled" || record?.isactive === false;
  const canEditReceiving = Boolean(data.permissions?.canEditReceiving);
  const canCancelReceiving = Boolean(data.permissions?.canCancelReceiving);

  useEffect(() => {
    const controller = new AbortController();

    async function loadReceivingRecord() {
      setLoading(true);
      setError("");
      setNotFound(false);
      try {
        const endpoint = data.api.receivingRecordDetail.replace("{id}", receivingId);
        const [response, suppliersResponse] = await Promise.all([
          fetch(endpoint, { signal: controller.signal }),
          fetch(data.api.suppliers, { signal: controller.signal })
        ]);

        if (response.status === 404) {
          setNotFound(true);
          setRecord(null);
          return;
        }
        if (!response.ok) {
          throw new Error("Could not load receiving record.");
        }

        setRecord(await response.json());
        setSuppliers(suppliersResponse.ok ? await suppliersResponse.json() : []);
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadReceivingRecord();
    return () => controller.abort();
  }, [data.api.receivingRecordDetail, data.api.suppliers, receivingId, reloadKey]);

  useEffect(() => {
    if (!record) return;
    setCorrectionForm({
      supplier: record.supplier ? String(record.supplier) : "",
      receivedDate: record.received_date || "",
      referenceNumber: record.reference_number || "",
      notes: record.notes || "",
      items: (record.items || []).map((item) => ({
        id: item.id,
        cost: item.cost || "0.00",
        notes: item.notes || ""
      }))
    });
  }, [record]);

  function updateCorrectionField(field, value) {
    setCorrectionForm((current) => ({ ...current, [field]: value }));
  }

  function updateCorrectionItem(itemId, field, value) {
    setCorrectionForm((current) => ({
      ...current,
      items: current.items.map((item) =>
        item.id === itemId ? { ...item, [field]: value } : item
      )
    }));
  }

  async function saveCorrection() {
    if (!canEditReceiving) return;
    setSavingCorrection(true);
    setCorrectionError("");
    setCorrectionMessage("");
    try {
      const endpoint = data.api.receivingRecordDetail.replace("{id}", receivingId);
      const response = await fetch(endpoint, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          supplier: correctionForm.supplier || null,
          received_date: correctionForm.receivedDate,
          reference_number: correctionForm.referenceNumber,
          notes: correctionForm.notes,
          items: correctionForm.items.map((item) => ({
            id: item.id,
            cost: item.cost || "0.00",
            notes: item.notes || ""
          }))
        })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not update receiving record.");
      }
      setEditing(false);
      setCorrectionMessage("Receiving details updated.");
      setReloadKey((current) => current + 1);
    } catch (saveError) {
      setCorrectionError(saveError.message);
    } finally {
      setSavingCorrection(false);
    }
  }

  async function cancelReceivingRecord() {
    if (!canCancelReceiving) return;
    setCancelling(true);
    setCancelError("");
    setCorrectionMessage("");
    try {
      if (!cancelReason.trim()) {
        throw new Error("Enter a cancellation reason.");
      }
      const endpoint = data.api.receivingRecordDetail.replace("{id}", receivingId).replace(/\/$/, "/cancel/");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({ cancel_reason: cancelReason })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not cancel receiving record.");
      }
      setCancelOpen(false);
      setCancelReason("");
      setCorrectionMessage("Receiving record cancelled. Linked available stock units were made inactive.");
      setReloadKey((current) => current + 1);
    } catch (cancelSaveError) {
      setCancelError(cancelSaveError.message);
    } finally {
      setCancelling(false);
    }
  }

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href={data.routes.receivingRecords} className="inline-flex items-center gap-2 text-sm font-semibold text-nexus-orange hover:text-orange-300">
            <ChevronRight className="h-4 w-4 rotate-180" />
            Back to Receiving Records
          </a>
          <h1 className="mt-3 bim-page-title">Receiving Record</h1>
          <p className="bim-page-description">Operational stock-entry detail.</p>
        </div>
        {record ? (
          <div className="flex flex-wrap items-center gap-3">
            <Status status={isCancelled ? "Cancelled" : "Recorded"} statusClass={isCancelled ? "inactive" : "received"} />
            {!isCancelled && (canEditReceiving || canCancelReceiving) ? (
              <>
                {canEditReceiving ? (
                  <Button type="button" variant="outline" onClick={() => setEditing((current) => !current)}>
                    <Edit3 className="h-4 w-4" />
                    Edit Details
                  </Button>
                ) : null}
                {canCancelReceiving ? (
                  <Button type="button" variant="secondary" onClick={() => setCancelOpen((current) => !current)}>
                    <RotateCcw className="h-4 w-4" />
                    Cancel Record
                  </Button>
                ) : null}
              </>
            ) : null}
          </div>
        ) : null}
      </header>

      {correctionMessage ? (
        <section className="mb-4 rounded-lg border border-nexus-green/50 bg-green-500/10 px-4 py-3 text-sm font-semibold text-green-200">
          {correctionMessage}
        </section>
      ) : null}

      {loading ? (
        <section className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-sm text-zinc-500">
          Loading receiving record...
        </section>
      ) : error ? (
        <section className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-sm font-semibold text-red-200">
          {error}
        </section>
      ) : notFound ? (
        <EmptyState
          className="rounded-lg border border-nexus-line bg-nexus-panel"
          title="Receiving record not found."
          description="The record may have been removed or you may not have access."
        />
      ) : record ? (
        <>
        {editing && canEditReceiving ? (
          <ReceivingCorrectionPanel
            form={correctionForm}
            suppliers={suppliers}
            items={record.items || []}
            saving={savingCorrection}
            error={correctionError}
            onFieldChange={updateCorrectionField}
            onItemChange={updateCorrectionItem}
            onCancel={() => {
              setEditing(false);
              setCorrectionError("");
            }}
            onSave={saveCorrection}
          />
        ) : null}

        {cancelOpen && canCancelReceiving ? (
          <section className="mb-5 rounded-lg border border-nexus-red/60 bg-red-500/10 p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <h2 className="text-sm font-bold text-red-100">Cancel receiving record</h2>
                <p className="mt-1 text-sm text-red-200/80">
                  Cancellation is only allowed while linked stock units are still available and unused. Wrong product, quantity, or serial entries should be cancelled and recreated when safe.
                </p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setCancelOpen(false)}>
                <X className="h-4 w-4" />
                Close
              </Button>
            </div>
            <div className="mt-4">
              <Field label="Cancellation reason" required>
                <TextInput value={cancelReason} onChange={setCancelReason} placeholder="Explain the receiving mistake" />
              </Field>
            </div>
            {cancelError ? <p className="mt-3 text-sm font-semibold text-red-200">{cancelError}</p> : null}
            <div className="mt-4 flex flex-wrap gap-3">
              <Button type="button" variant="danger" loading={cancelling} onClick={cancelReceivingRecord}>
                <RotateCcw className="h-4 w-4" />
                Confirm Cancel
              </Button>
              <Button type="button" variant="secondary" onClick={() => setCancelOpen(false)}>
                Keep Record
              </Button>
            </div>
          </section>
        ) : null}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
          <div className="min-w-0 space-y-5">
            <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="bim-section-title">Receiving Number</p>
                  <h2 className="mt-2 font-mono text-2xl font-bold text-nexus-orange">{record.receiving_number}</h2>
                </div>
                <div className="grid gap-3 text-sm md:min-w-48 md:text-right">
                  <div>
                    <p className="bim-helper-text">Received Date</p>
                    <p className="mt-1 text-zinc-300">{formatDate(record.received_date)}</p>
                  </div>
                  <div>
                    <p className="bim-helper-text">Reference Number</p>
                    <p className="mt-1 font-mono text-xs text-zinc-300">{record.reference_number || "No reference"}</p>
                  </div>
                </div>
              </div>

              <dl className="mt-5 grid gap-4 md:grid-cols-2">
                <DetailRow label="Source" value={record.supplier_name || "Manual source"} strong />
                <DetailRow label="Received Date" value={formatDate(record.received_date)} />
                <DetailRow label="Reference Number" value={record.reference_number || "-"} />
                <DetailRow label="Created By" value={record.created_by_name || "-"} />
                <DetailRow label="Total Quantity" value={formatCount(record.total_quantity || 0)} highlight />
                <DetailRow label="Status" value={isCancelled ? "Cancelled" : "Recorded"} />
              </dl>

              {record.notes ? (
                <div className="mt-5 rounded-lg border border-nexus-line bg-nexus-panel2 p-4">
                  <p className="bim-helper-text">Notes</p>
                  <p className="mt-2 text-sm text-zinc-300">{record.notes}</p>
                </div>
              ) : null}
            </section>

            <ReceivingItemsTable items={record.items || []} />
          </div>

          <aside className="rounded-lg border border-nexus-line bg-nexus-panel p-4 xl:sticky xl:top-5 xl:self-start">
            <h2 className="bim-section-title">Activity</h2>
            <div className="mt-4 space-y-3 text-sm">
              <DetailRow label="Record Status" value={isCancelled ? "Cancelled" : "Recorded"} highlight />
              <DetailRow label="Created" value={formatDate(record.crdate)} />
              <DetailRow label="Item Lines" value={formatCount(record.items?.length || 0)} />
              <DetailRow label="Reference Cost" value="Reference cost only" />
              {isCancelled ? (
                <>
                  <DetailRow label="Cancelled" value={formatDate(record.cancelled_at)} />
                  <DetailRow label="Reason" value={record.cancel_reason || "-"} />
                </>
              ) : null}
            </div>
          </aside>
        </div>
        </>
      ) : null}
    </Shell>
  );
}

function ReceivingCorrectionPanel({
  form,
  suppliers,
  items,
  saving,
  error,
  onFieldChange,
  onItemChange,
  onCancel,
  onSave
}) {
  return (
    <section className="mb-5 rounded-lg border border-nexus-line bg-nexus-panel p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-sm font-bold text-white">Edit receiving details</h2>
          <p className="bim-page-description">
            Safe edits are limited to supplier, reference, date, notes, line cost, and line notes. For wrong product, quantity, or serial, cancel and recreate the record when the linked units are still unused.
          </p>
        </div>
        <Button type="button" variant="ghost" onClick={onCancel}>
          <X className="h-4 w-4" />
          Close
        </Button>
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <Field label="Supplier">
          <SelectInput
            value={form.supplier}
            onChange={(value) => onFieldChange("supplier", value)}
            options={suppliers.map((supplier) => [supplier.id, supplier.name])}
            placeholder="Manual source"
          />
        </Field>
        <Field label="Received Date">
          <TextInput type="date" value={form.receivedDate} onChange={(value) => onFieldChange("receivedDate", value)} />
        </Field>
        <Field label="Reference Number">
          <TextInput value={form.referenceNumber} onChange={(value) => onFieldChange("referenceNumber", value)} placeholder="Supplier reference" />
        </Field>
        <Field label="Notes">
          <TextInput value={form.notes} onChange={(value) => onFieldChange("notes", value)} placeholder="Receiving notes" />
        </Field>
      </div>

      {items.length ? (
        <div className="mt-5 overflow-hidden rounded-lg border border-nexus-line">
          <div className="grid gap-3 bg-zinc-800/80 px-4 py-3 bim-label md:grid-cols-[minmax(0,1fr)_130px_minmax(0,1fr)]">
            <span>Line</span>
            <span>Cost</span>
            <span>Notes</span>
          </div>
          {items.map((item) => {
            const formItem = form.items.find((entry) => entry.id === item.id) || {};
            return (
              <div key={item.id} className="grid gap-3 border-t border-nexus-line p-4 md:grid-cols-[minmax(0,1fr)_130px_minmax(0,1fr)]">
                <div>
                  <p className="font-semibold text-white">{item.product_name}</p>
                  <p className="mt-1 font-mono text-xs text-zinc-500">{item.serial_number || item.product_unit_serial_number || "No serial"}</p>
                </div>
                <TextInput value={formItem.cost || "0.00"} onChange={(value) => onItemChange(item.id, "cost", value)} />
                <TextInput value={formItem.notes || ""} onChange={(value) => onItemChange(item.id, "notes", value)} placeholder="Line notes" />
              </div>
            );
          })}
        </div>
      ) : null}

      {error ? <p className="mt-3 text-sm font-semibold text-red-200">{error}</p> : null}
      <div className="mt-5 flex flex-wrap gap-3">
        <Button type="button" variant="primary" loading={saving} onClick={onSave}>
          <Save className="h-4 w-4" />
          Save Details
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </section>
  );
}

function ReceivingItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Received Items" badge={formatCount(items.length)} />
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Product</th>
              <th className="px-4 py-3 font-medium">Quantity</th>
              <th className="px-4 py-3 font-medium">Serial / Unit</th>
              <th className="px-4 py-3 font-medium">Reference Cost</th>
              <th className="px-4 py-3 font-medium">Notes</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line">
                  <td className="px-4 py-4">
                    <p className="font-semibold text-white">{item.product_name}</p>
                    <p className="mt-1 font-mono text-xs text-zinc-500">{item.product_sku || "-"}</p>
                  </td>
                  <td className="px-4 py-4 font-bold text-white">{formatCount(item.quantity || 0)}</td>
                  <td className="px-4 py-4">
                    <p className="font-mono text-xs text-zinc-300">{item.serial_number || item.product_unit_serial_number || "-"}</p>
                    <p className="mt-1 text-xs text-zinc-500">{item.product_unit ? `Unit #${item.product_unit}` : "No unit link"}</p>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-xs text-zinc-300">{formatCurrency(item.cost)}</p>
                    <p className="mt-1 text-xs text-zinc-500">Reference cost only</p>
                  </td>
                  <td className="px-4 py-4 text-zinc-400">{item.notes || "-"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No item lines on this record."
                    description="This receiving record has no active item rows."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ReservationRecordsPage({ data }) {
  const canCreateReservation = Boolean(data.permissions?.canCreateReservation);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadReservations() {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set("q", query.trim());
        const endpoint = params.toString()
          ? `${data.api.reservations}?${params.toString()}`
          : data.api.reservations;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error("Could not load reservation records.");
        }
        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadReservations();
    return () => controller.abort();
  }, [data.api.reservations, query]);

  const activeCount = records.filter((record) => record.status === "active").length;
  const totalUnits = records.reduce((sum, record) => sum + Number(record.total_units || 0), 0);
  const latestRecord = records[0];
  const reservationKpis = [
    {
      label: "Reservations",
      value: formatCount(records.length),
      detail: "operational hold records",
      icon: "clock-3",
      tone: "warning"
    },
    {
      label: "Active Holds",
      value: formatCount(activeCount),
      detail: "not yet released",
      icon: "box",
      tone: "orange"
    },
    {
      label: "Reserved Units",
      value: formatCount(totalUnits),
      detail: "units in these records",
      icon: "layers",
      tone: "blue"
    },
    {
      label: "Latest Reservation",
      value: latestRecord ? formatDate(latestRecord.reserved_at) : "-",
      detail: latestRecord?.reservation_number || "no reservations yet",
      icon: "clock-3",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Reservation Records</h1>
          <p className="bim-page-description">Hold available stock for upcoming work without delivering it.</p>
        </div>
        {canCreateReservation ? (
          <Button as="a" href={data.routes.createReservation} variant="primary">
            <Plus className="h-4 w-4" />
            Create Reservation
          </Button>
        ) : null}
      </header>

      <KpiGrid items={reservationKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search reservation number, reserved for, reason, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <ReservationRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function ReservationRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Reservation</th>
              <th className="px-4 py-3 font-medium">Reserved For</th>
              <th className="px-4 py-3 font-medium">Reason</th>
              <th className="px-4 py-3 font-medium">Expected Release</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading reservation records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`/operations/reservations/${record.id}/`} className="font-mono text-xs font-bold text-nexus-orange hover:text-orange-300">
                      {record.reservation_number}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">Reserved by {record.reserved_by_name || "-"}</p>
                  </td>
                  <td className="px-4 py-4 font-semibold text-white">{record.reserved_for || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{record.reason || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.expected_release_date)}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_units || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={reservationStatusLabel(record)} statusClass={record.status} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No reservation records yet."
                    description="Create Reservation will hold available stock without delivering it."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ReservationRecordDetailPage({ data }) {
  const reservationId = (data.currentPath || window.location.pathname).match(/\/operations\/reservations\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [releaseReason, setReleaseReason] = useState("");
  const [releasing, setReleasing] = useState(false);
  const [releaseError, setReleaseError] = useState("");
  const [message, setMessage] = useState("");
  const canReleaseReservation = Boolean(data.permissions?.canReleaseReservation);

  useEffect(() => {
    const controller = new AbortController();

    async function loadReservation() {
      setLoading(true);
      setError("");
      try {
        const endpoint = data.api.reservationDetail.replace("{id}", reservationId);
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(response.status === 404 ? "Reservation record was not found." : "Could not load reservation record.");
        }
        setRecord(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadReservation();
    return () => controller.abort();
  }, [data.api.reservationDetail, reservationId, reloadKey]);

  async function releaseReservation() {
    if (!canReleaseReservation) return;
    setReleasing(true);
    setReleaseError("");
    setMessage("");
    try {
      if (!releaseReason.trim()) {
        throw new Error("Enter a release reason.");
      }
      const endpoint = data.api.reservationDetail.replace("{id}", reservationId).replace(/\/$/, "/release/");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({ release_reason: releaseReason })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not release reservation.");
      }
      setReleaseReason("");
      setMessage("Reservation released. Linked reserved units were moved back to available stock.");
      setReloadKey((current) => current + 1);
    } catch (releaseSaveError) {
      setReleaseError(releaseSaveError.message);
    } finally {
      setReleasing(false);
    }
  }

  if (loading) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-zinc-400">
          Loading reservation record...
        </div>
      </Shell>
    );
  }

  if (error || !record) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-red-200">
          {error || "Reservation record was not found."}
        </div>
      </Shell>
    );
  }

  const isActive = record.status === "active";

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href="/operations/reservations/" className="mb-2 inline-flex text-sm font-semibold text-nexus-orange hover:text-orange-300">
            Back to reservations
          </a>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="bim-page-title">{record.reservation_number}</h1>
            <Status status={reservationStatusLabel(record)} statusClass={record.status} />
          </div>
          <p className="bim-page-description">Reserved stock must be released before delivery.</p>
        </div>
      </header>

      {message ? (
        <div className="mb-4 rounded-lg border border-nexus-green/60 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-200">
          {message}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
            <SectionTitle title="Reservation Details" />
            <dl className="mt-4 divide-y divide-nexus-line">
              <DetailRow label="Reserved For" value={record.reserved_for || "-"} />
              <DetailRow label="Reason" value={record.reason || "-"} />
              <DetailRow label="Expected Release" value={formatDate(record.expected_release_date)} />
              <DetailRow label="Reserved By" value={record.reserved_by_name || "-"} />
              <DetailRow label="Reserved At" value={formatDate(record.reserved_at)} />
              <DetailRow label="Notes" value={record.notes || "-"} />
              {record.released_at ? <DetailRow label="Released At" value={formatDate(record.released_at)} /> : null}
              {record.release_reason ? <DetailRow label="Release Reason" value={record.release_reason} /> : null}
            </dl>
          </section>

          <ReservationItemsTable items={record.items || []} />
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Reservation Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value={record.reservation_number} />
              <DetailRow label="Status" value={reservationStatusLabel(record)} />
              <DetailRow label="Units" value={record.total_units || 0} strong />
            </dl>
          </section>

          {canReleaseReservation ? (
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-4">
            <h2 className="bim-section-title">Release Reservation</h2>
            <p className="mt-3 text-sm text-zinc-500">
              Release only when this hold is no longer needed. Units return to available stock.
            </p>
            <div className="mt-4">
              <Field label="Release Reason" required>
                <TextInput
                  value={releaseReason}
                  onChange={setReleaseReason}
                  placeholder="Why is this reservation being released?"
                  disabled={!isActive}
                />
              </Field>
            </div>
            {releaseError ? <p className="mt-3 text-sm font-semibold text-red-300">{releaseError}</p> : null}
            <Button type="button" onClick={releaseReservation} disabled={!isActive || releasing} className="mt-4 w-full" variant="primary">
              <RotateCcw className="h-4 w-4" />
              {releasing ? "Releasing..." : "Release Reservation"}
            </Button>
          </section>
          ) : null}
        </aside>
      </div>
    </Shell>
  );
}

function ReservationItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Reserved Units" badge={`${formatCount(items.length)} units`} />
      {items.length ? (
        <div className="overflow-x-auto border-t border-nexus-line">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-800/80 text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">SKU</th>
                <th className="px-4 py-3 font-medium">Unit ID</th>
                <th className="px-4 py-3 font-medium">Serial</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                  <td className="px-4 py-3 font-semibold text-white">{item.product_name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{item.product_sku || "-"}</td>
                  <td className="px-4 py-3 text-zinc-400">#{item.product_unit}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-300">{item.serial_number || "-"}</td>
                  <td className="px-4 py-3">
                    <Status status={item.product_unit_status_label || item.product_unit_status} statusClass={item.product_unit_status} />
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{item.notes || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No reserved units are linked to this record.
        </p>
      )}
    </section>
  );
}

function CreateReservationPage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    reservedFor: "",
    reason: "",
    expectedReleaseDate: today,
    notes: ""
  });
  const [units, setUnits] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadUnits() {
      const response = await fetch(`${data.api.productUnits}?status=available`, {
        signal: controller.signal
      });
      setUnits(response.ok ? await response.json() : []);
    }

    loadUnits().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load available stock units.");
      }
    });

    return () => controller.abort();
  }, [data.api.productUnits]);

  const selectedIds = new Set(selectedUnits.map((unit) => unit.id));
  const filteredUnits = units
    .filter((unit) => !selectedIds.has(unit.id))
    .filter((unit) => {
      const text = `${unit.product_name} ${unit.product_sku} ${unit.product_barcode || ""} ${unit.serial_number}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 8);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addUnit(unit) {
    setSelectedUnits((current) => [...current, unit]);
    setQuery("");
  }

  function removeUnit(unitId) {
    setSelectedUnits((current) => current.filter((unit) => unit.id !== unitId));
  }

  async function saveReservation() {
    setSaving(true);
    setError("");
    try {
      if (!form.reservedFor.trim() || !selectedUnits.length) {
        throw new Error("Reserved for and at least one available stock unit are required.");
      }

      const response = await fetch(data.api.reservations, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          reserved_for: form.reservedFor,
          reason: form.reason,
          expected_release_date: form.expectedReleaseDate || null,
          notes: form.notes,
          unit_ids: selectedUnits.map((unit) => unit.id)
        })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not create reservation.");
      }

      const created = await response.json();
      window.location.assign(created.id ? `/operations/reservations/${created.id}/` : data.routes.reservationRecords);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">Create Reservation</h1>
              <p className="bim-page-description">Hold available stock without delivering it.</p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/operations/reservations/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled={saving} onClick={saveReservation} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Icon name="clock-3" className="h-4 w-4" />
                Save Reservation
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="clock-3" title="Reservation Information" subtitle="Operational hold details for selected stock units.">
            <div className="grid gap-5 md:grid-cols-2">
              <Field label="Reserved For" required>
                <TextInput value={form.reservedFor} onChange={(value) => updateField("reservedFor", value)} placeholder="Client, person, department, or job" />
              </Field>
              <Field label="Expected Release Date">
                <TextInput type="date" value={form.expectedReleaseDate} onChange={(value) => updateField("expectedReleaseDate", value)} />
              </Field>
              <Field label="Reason">
                <TextInput value={form.reason} onChange={(value) => updateField("reason", value)} placeholder="Why this stock is being held" />
              </Field>
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Operational notes" />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Available Units" subtitle="Only active available units can be reserved.">
            <SearchBar
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search product, SKU, barcode, or serial..."
            />
            {filteredUnits.length ? (
              <div className="mt-2 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
                {filteredUnits.map((unit) => (
                  <button
                    key={unit.id}
                    onClick={() => addUnit(unit)}
                    type="button"
                    className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                  >
                    <span>
                      <span className="block text-sm font-bold text-white">{unit.product_name}</span>
                      <span className="font-mono text-xs text-nexus-orange">{unit.serial_number}</span>
                    </span>
                    <Plus className="h-4 w-4 text-zinc-500" />
                  </button>
                ))}
              </div>
            ) : null}

            <SelectedUnitsTable units={selectedUnits} onRemove={removeUnit} emptyText="No units selected for reservation yet." />
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Reservation Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reserved For" value={form.reservedFor || "-"} />
              <DetailRow label="Expected Release" value={formatDate(form.expectedReleaseDate)} />
              <DetailRow label="Selected Units" value={selectedUnits.length} strong />
              <DetailRow label="Status" value="Draft" />
            </dl>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function SelectedUnitsTable({ units, onRemove, emptyText }) {
  return (
    <div className="mt-4 overflow-hidden rounded-lg border border-dashed border-nexus-line bg-black/30">
      {units.length ? (
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Product</th>
              <th className="px-4 py-3 font-medium">SKU</th>
              <th className="px-4 py-3 font-medium">Serial</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Remove</th>
            </tr>
          </thead>
          <tbody>
            {units.map((unit) => (
              <tr key={unit.id} className="border-t border-nexus-line">
                <td className="px-4 py-3 font-semibold text-white">{unit.product_name}</td>
                <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{unit.product_sku || "-"}</td>
                <td className="px-4 py-3 font-mono text-xs text-zinc-300">{unit.serial_number}</td>
                <td className="px-4 py-3">
                  <Status status={unit.status_label || unit.status} statusClass={unit.status} />
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => onRemove(unit.id)} type="button" className="text-zinc-500 hover:text-nexus-red" aria-label={`Remove ${unit.serial_number}`}>
                    <X className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="grid min-h-32 place-items-center text-center text-sm text-zinc-600">
          {emptyText}
        </div>
      )}
    </div>
  );
}

function IssueRecordsPage({ data }) {
  const canCreateIssue = Boolean(data.permissions?.canCreateIssue);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadIssues() {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set("q", query.trim());
        const endpoint = params.toString()
          ? `${data.api.issues}?${params.toString()}`
          : data.api.issues;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error("Could not load issue records.");
        }
        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadIssues();
    return () => controller.abort();
  }, [data.api.issues, query]);

  const activeCount = records.filter((record) => record.status === "active").length;
  const totalUnits = records.reduce((sum, record) => sum + Number(record.total_units || 0), 0);
  const latestRecord = records[0];
  const issueKpis = [
    {
      label: "Issue Records",
      value: formatCount(records.length),
      detail: "temporary handoffs",
      icon: "user-check",
      tone: "indigo"
    },
    {
      label: "Active Issues",
      value: formatCount(activeCount),
      detail: "not yet returned",
      icon: "box",
      tone: "warning"
    },
    {
      label: "Issued Units",
      value: formatCount(totalUnits),
      detail: "units in these records",
      icon: "layers",
      tone: "blue"
    },
    {
      label: "Latest Issue",
      value: latestRecord ? formatDate(latestRecord.issue_date) : "-",
      detail: latestRecord?.issue_number || "no issues yet",
      icon: "clock-3",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Issue Records</h1>
          <p className="bim-page-description">Track temporary stock handoffs expected to come back.</p>
        </div>
        {canCreateIssue ? (
          <Button as="a" href={data.routes.createIssue} variant="primary">
            <Plus className="h-4 w-4" />
            Create Issue
          </Button>
        ) : null}
      </header>

      <KpiGrid items={issueKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search issue number, issued to, department, site, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <IssueRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function IssueRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Issue</th>
              <th className="px-4 py-3 font-medium">Issued To</th>
              <th className="px-4 py-3 font-medium">Department / Site</th>
              <th className="px-4 py-3 font-medium">Expected Return</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading issue records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`/operations/issues/${record.id}/`} className="font-mono text-xs font-bold text-nexus-orange hover:text-orange-300">
                      {record.issue_number}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">Issued by {record.issued_by_name || "-"}</p>
                  </td>
                  <td className="px-4 py-4 font-semibold text-white">{record.issued_to || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{[record.department, record.branch_or_site].filter(Boolean).join(" / ") || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.expected_return_date)}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_units || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={issueStatusLabel(record)} statusClass={record.status} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No issue records yet."
                    description="Create Issue will temporarily hand off available stock without delivering it."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function IssueRecordDetailPage({ data }) {
  const issueId = (data.currentPath || window.location.pathname).match(/\/operations\/issues\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [returnReason, setReturnReason] = useState("");
  const [returning, setReturning] = useState(false);
  const [returnError, setReturnError] = useState("");
  const [message, setMessage] = useState("");
  const canReturnIssue = Boolean(data.permissions?.canReturnIssue);

  useEffect(() => {
    const controller = new AbortController();

    async function loadIssue() {
      setLoading(true);
      setError("");
      try {
        const endpoint = data.api.issueDetail.replace("{id}", issueId);
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(response.status === 404 ? "Issue record was not found." : "Could not load issue record.");
        }
        setRecord(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadIssue();
    return () => controller.abort();
  }, [data.api.issueDetail, issueId, reloadKey]);

  async function returnIssue() {
    if (!canReturnIssue) return;
    setReturning(true);
    setReturnError("");
    setMessage("");
    try {
      if (!returnReason.trim()) {
        throw new Error("Enter a return reason.");
      }
      const endpoint = data.api.issueDetail.replace("{id}", issueId).replace(/\/$/, "/return/");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({ return_reason: returnReason })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not return issue.");
      }
      setReturnReason("");
      setMessage("Issue returned. Linked issued units were moved back to available stock.");
      setReloadKey((current) => current + 1);
    } catch (returnSaveError) {
      setReturnError(returnSaveError.message);
    } finally {
      setReturning(false);
    }
  }

  if (loading) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-zinc-400">
          Loading issue record...
        </div>
      </Shell>
    );
  }

  if (error || !record) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-red-200">
          {error || "Issue record was not found."}
        </div>
      </Shell>
    );
  }

  const isActive = record.status === "active";

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href="/operations/issues/" className="mb-2 inline-flex text-sm font-semibold text-nexus-orange hover:text-orange-300">
            Back to issues
          </a>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="bim-page-title">{record.issue_number}</h1>
            <Status status={issueStatusLabel(record)} statusClass={record.status} />
          </div>
          <p className="bim-page-description">Issued units must be returned before delivery.</p>
        </div>
      </header>

      {message ? (
        <div className="mb-4 rounded-lg border border-nexus-green/60 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-200">
          {message}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
            <SectionTitle title="Issue Details" />
            <dl className="mt-4 divide-y divide-nexus-line">
              <DetailRow label="Issued To" value={record.issued_to || "-"} />
              <DetailRow label="Department" value={record.department || "-"} />
              <DetailRow label="Branch / Site" value={record.branch_or_site || "-"} />
              <DetailRow label="Reason" value={record.reason || "-"} />
              <DetailRow label="Issue Date" value={formatDate(record.issue_date)} />
              <DetailRow label="Expected Return" value={formatDate(record.expected_return_date)} />
              <DetailRow label="Issued By" value={record.issued_by_name || "-"} />
              <DetailRow label="Notes" value={record.notes || "-"} />
              {record.returned_date ? <DetailRow label="Returned Date" value={formatDate(record.returned_date)} /> : null}
              {record.return_reason ? <DetailRow label="Return Reason" value={record.return_reason} /> : null}
            </dl>
          </section>

          <IssueItemsTable items={record.items || []} />
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Issue Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value={record.issue_number} />
              <DetailRow label="Status" value={issueStatusLabel(record)} />
              <DetailRow label="Units" value={record.total_units || 0} strong />
            </dl>
          </section>

          {canReturnIssue ? (
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-4">
            <h2 className="bim-section-title">Return Issue</h2>
            <p className="mt-3 text-sm text-zinc-500">
              Return only when all linked units are back and still untouched issued units.
            </p>
            <div className="mt-4">
              <Field label="Return Reason" required>
                <TextInput
                  value={returnReason}
                  onChange={setReturnReason}
                  placeholder="Why is this issue being returned?"
                  disabled={!isActive}
                />
              </Field>
            </div>
            {returnError ? <p className="mt-3 text-sm font-semibold text-red-300">{returnError}</p> : null}
            <Button type="button" onClick={returnIssue} disabled={!isActive || returning} className="mt-4 w-full" variant="primary">
              <RotateCcw className="h-4 w-4" />
              {returning ? "Returning..." : "Return Issue"}
            </Button>
          </section>
          ) : null}
        </aside>
      </div>
    </Shell>
  );
}

function IssueItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Issued Units" badge={`${formatCount(items.length)} units`} />
      {items.length ? (
        <div className="overflow-x-auto border-t border-nexus-line">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-800/80 text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">SKU</th>
                <th className="px-4 py-3 font-medium">Unit ID</th>
                <th className="px-4 py-3 font-medium">Serial</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                  <td className="px-4 py-3 font-semibold text-white">{item.product_name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{item.product_sku || "-"}</td>
                  <td className="px-4 py-3 text-zinc-400">#{item.product_unit}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-300">{item.serial_number || "-"}</td>
                  <td className="px-4 py-3">
                    <Status status={item.product_unit_status_label || item.product_unit_status} statusClass={item.product_unit_status} />
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{item.notes || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No issued units are linked to this record.
        </p>
      )}
    </section>
  );
}

function CreateIssuePage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    issuedTo: "",
    department: "",
    branchOrSite: "",
    reason: "",
    issueDate: today,
    expectedReturnDate: "",
    notes: ""
  });
  const [units, setUnits] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadUnits() {
      const response = await fetch(`${data.api.productUnits}?status=available`, {
        signal: controller.signal
      });
      setUnits(response.ok ? await response.json() : []);
    }

    loadUnits().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load available stock units.");
      }
    });

    return () => controller.abort();
  }, [data.api.productUnits]);

  const selectedIds = new Set(selectedUnits.map((unit) => unit.id));
  const filteredUnits = units
    .filter((unit) => !selectedIds.has(unit.id))
    .filter((unit) => {
      const text = `${unit.product_name} ${unit.product_sku} ${unit.product_barcode || ""} ${unit.serial_number}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 8);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addUnit(unit) {
    setSelectedUnits((current) => [...current, unit]);
    setQuery("");
  }

  function removeUnit(unitId) {
    setSelectedUnits((current) => current.filter((unit) => unit.id !== unitId));
  }

  async function saveIssue() {
    setSaving(true);
    setError("");
    try {
      if (!form.issuedTo.trim() || !selectedUnits.length) {
        throw new Error("Issued to and at least one available stock unit are required.");
      }

      const response = await fetch(data.api.issues, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          issued_to: form.issuedTo,
          department: form.department,
          branch_or_site: form.branchOrSite,
          reason: form.reason,
          issue_date: form.issueDate || null,
          expected_return_date: form.expectedReturnDate || null,
          notes: form.notes,
          unit_ids: selectedUnits.map((unit) => unit.id)
        })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not create issue.");
      }

      const created = await response.json();
      window.location.assign(created.id ? `/operations/issues/${created.id}/` : data.routes.issueRecords);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">Create Issue</h1>
              <p className="bim-page-description">Temporarily issue available stock that is expected to come back.</p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/operations/issues/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled={saving} onClick={saveIssue} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Icon name="user-check" className="h-4 w-4" />
                Save Issue
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="user-check" title="Issue Information" subtitle="Operational handoff details for selected stock units.">
            <div className="grid gap-5 md:grid-cols-2">
              <Field label="Issued To" required>
                <TextInput value={form.issuedTo} onChange={(value) => updateField("issuedTo", value)} placeholder="Person, team, branch, or site" />
              </Field>
              <Field label="Department">
                <TextInput value={form.department} onChange={(value) => updateField("department", value)} placeholder="Department or team" />
              </Field>
              <Field label="Branch / Site">
                <TextInput value={form.branchOrSite} onChange={(value) => updateField("branchOrSite", value)} placeholder="Branch, room, or site" />
              </Field>
              <Field label="Reason">
                <TextInput value={form.reason} onChange={(value) => updateField("reason", value)} placeholder="Why this stock is being issued" />
              </Field>
              <Field label="Issue Date">
                <TextInput type="date" value={form.issueDate} onChange={(value) => updateField("issueDate", value)} />
              </Field>
              <Field label="Expected Return">
                <TextInput type="date" value={form.expectedReturnDate} onChange={(value) => updateField("expectedReturnDate", value)} />
              </Field>
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Operational notes" />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Available Units" subtitle="Only active available units can be issued.">
            <SearchBar
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search product, SKU, barcode, or serial..."
            />
            {filteredUnits.length ? (
              <div className="mt-2 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
                {filteredUnits.map((unit) => (
                  <button
                    key={unit.id}
                    onClick={() => addUnit(unit)}
                    type="button"
                    className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                  >
                    <span>
                      <span className="block text-sm font-bold text-white">{unit.product_name}</span>
                      <span className="font-mono text-xs text-nexus-orange">{unit.serial_number}</span>
                    </span>
                    <Plus className="h-4 w-4 text-zinc-500" />
                  </button>
                ))}
              </div>
            ) : null}

            <SelectedUnitsTable units={selectedUnits} onRemove={removeUnit} emptyText="No units selected for issue yet." />
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Issue Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Issued To" value={form.issuedTo || "-"} />
              <DetailRow label="Issue Date" value={formatDate(form.issueDate)} />
              <DetailRow label="Expected Return" value={formatDate(form.expectedReturnDate)} />
              <DetailRow label="Selected Units" value={selectedUnits.length} strong />
              <DetailRow label="Status" value="Draft" />
            </dl>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function RepairRecordsPage({ data }) {
  const canCreateRepair = Boolean(data.permissions?.canCreateRepair);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadRepairs() {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set("q", query.trim());
        const endpoint = params.toString()
          ? `${data.api.repairs}?${params.toString()}`
          : data.api.repairs;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error("Could not load repair records.");
        }
        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadRepairs();
    return () => controller.abort();
  }, [data.api.repairs, query]);

  const activeCount = records.filter((record) => record.status === "active").length;
  const totalUnits = records.reduce((sum, record) => sum + Number(record.total_units || 0), 0);
  const latestRecord = records[0];
  const repairKpis = [
    {
      label: "Repair Records",
      value: formatCount(records.length),
      detail: "repair or testing records",
      icon: "wrench",
      tone: records.length > 0 ? "warning" : "neutral"
    },
    {
      label: "Active Repairs",
      value: formatCount(activeCount),
      detail: "not yet resolved",
      icon: "box",
      tone: activeCount > 0 ? "warning" : "neutral"
    },
    {
      label: "Repair Units",
      value: formatCount(totalUnits),
      detail: "units in these records",
      icon: "layers",
      tone: "blue"
    },
    {
      label: "Latest Repair",
      value: latestRecord ? formatDate(latestRecord.repair_date) : "-",
      detail: latestRecord?.repair_number || "no repairs yet",
      icon: "clock-3",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Repair Records</h1>
          <p className="bim-page-description">Track available stock moved into repair, testing, or diagnosis.</p>
        </div>
        {canCreateRepair ? (
          <Button as="a" href={data.routes.createRepair} variant="primary">
            <Plus className="h-4 w-4" />
            Create Repair
          </Button>
        ) : null}
      </header>

      <KpiGrid items={repairKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search repair number, reason, reporter, location, technician, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <RepairRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function RepairRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Repair</th>
              <th className="px-4 py-3 font-medium">Reason</th>
              <th className="px-4 py-3 font-medium">Location / Technician</th>
              <th className="px-4 py-3 font-medium">Expected Resolution</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading repair records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`/operations/repairs/${record.id}/`} className="font-mono text-xs font-bold text-nexus-orange hover:text-orange-300">
                      {record.repair_number}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">Sent by {record.sent_by_name || "-"}</p>
                  </td>
                  <td className="px-4 py-4 font-semibold text-white">{record.repair_reason || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{[record.repair_location, record.technician].filter(Boolean).join(" / ") || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.expected_resolution_date)}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_units || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={repairStatusLabel(record)} statusClass={record.status === "resolved" ? record.resolution || "available" : "repair"} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No repair records yet."
                    description="Create Repair moves active available units into repair without changing delivery, issue, or reservation records."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function RepairRecordDetailPage({ data }) {
  const repairId = (data.currentPath || window.location.pathname).match(/\/operations\/repairs\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [resolution, setResolution] = useState("available");
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState("");
  const [message, setMessage] = useState("");
  const canResolveRepair = Boolean(data.permissions?.canResolveRepair);

  useEffect(() => {
    const controller = new AbortController();

    async function loadRepair() {
      setLoading(true);
      setError("");
      try {
        const endpoint = data.api.repairDetail.replace("{id}", repairId);
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(response.status === 404 ? "Repair record was not found." : "Could not load repair record.");
        }
        setRecord(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadRepair();
    return () => controller.abort();
  }, [data.api.repairDetail, repairId, reloadKey]);

  async function resolveRepair() {
    if (!canResolveRepair) return;
    setResolving(true);
    setResolveError("");
    setMessage("");
    try {
      if (!resolutionNotes.trim()) {
        throw new Error("Enter resolution notes.");
      }
      const endpoint = data.api.repairDetail.replace("{id}", repairId).replace(/\/$/, "/resolve/");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          resolution,
          resolution_notes: resolutionNotes
        })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not resolve repair.");
      }
      setResolutionNotes("");
      setMessage(
        resolution === "available"
          ? "Repair resolved. Linked repair units were moved back to available stock."
          : "Repair resolved. Linked repair units were made inactive."
      );
      setReloadKey((current) => current + 1);
    } catch (resolveSaveError) {
      setResolveError(resolveSaveError.message);
    } finally {
      setResolving(false);
    }
  }

  if (loading) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-zinc-400">
          Loading repair record...
        </div>
      </Shell>
    );
  }

  if (error || !record) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-red-200">
          {error || "Repair record was not found."}
        </div>
      </Shell>
    );
  }

  const isActive = record.status === "active";

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href="/operations/repairs/" className="mb-2 inline-flex text-sm font-semibold text-nexus-orange hover:text-orange-300">
            Back to repairs
          </a>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="bim-page-title">{record.repair_number}</h1>
            <Status status={repairStatusLabel(record)} statusClass={record.status === "resolved" ? record.resolution || "available" : "repair"} />
          </div>
          <p className="bim-page-description">Reserved, issued, and sold units must use their own workflows before repair.</p>
        </div>
      </header>

      {message ? (
        <div className="mb-4 rounded-lg border border-nexus-green/60 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-200">
          {message}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
            <SectionTitle title="Repair Details" />
            <dl className="mt-4 divide-y divide-nexus-line">
              <DetailRow label="Reason" value={record.repair_reason || "-"} />
              <DetailRow label="Reported By" value={record.reported_by_name || "-"} />
              <DetailRow label="Location" value={record.repair_location || "-"} />
              <DetailRow label="Technician" value={record.technician || "-"} />
              <DetailRow label="Repair Date" value={formatDate(record.repair_date)} />
              <DetailRow label="Expected Resolution" value={formatDate(record.expected_resolution_date)} />
              <DetailRow label="Sent By" value={record.sent_by_name || "-"} />
              <DetailRow label="Notes" value={record.notes || "-"} />
              {record.resolved_date ? <DetailRow label="Resolved Date" value={formatDate(record.resolved_date)} /> : null}
              {record.resolution ? <DetailRow label="Resolution" value={record.resolution} /> : null}
              {record.resolution_notes ? <DetailRow label="Resolution Notes" value={record.resolution_notes} /> : null}
            </dl>
          </section>

          <RepairItemsTable items={record.items || []} />
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Repair Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value={record.repair_number} />
              <DetailRow label="Status" value={repairStatusLabel(record)} />
              <DetailRow label="Units" value={record.total_units || 0} strong />
            </dl>
          </section>

          {canResolveRepair ? (
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-4">
            <h2 className="bim-section-title">Resolve Repair</h2>
            <p className="mt-3 text-sm text-zinc-500">
              Resolve only when all linked units are still untouched repair units.
            </p>
            <div className="mt-4 space-y-4">
              <Field label="Resolution" required>
                <SelectInput
                  value={resolution}
                  onChange={setResolution}
                  options={[
                    ["available", "Return to available"],
                    ["inactive", "Deactivate unit"]
                  ]}
                  disabled={!isActive}
                />
              </Field>
              <Field label="Resolution Notes" required>
                <TextInput
                  value={resolutionNotes}
                  onChange={setResolutionNotes}
                  placeholder="How was this repair resolved?"
                  disabled={!isActive}
                />
              </Field>
            </div>
            {resolveError ? <p className="mt-3 text-sm font-semibold text-red-300">{resolveError}</p> : null}
            <Button type="button" onClick={resolveRepair} disabled={!isActive || resolving} className="mt-4 w-full" variant="primary">
              <RotateCcw className="h-4 w-4" />
              {resolving ? "Resolving..." : "Resolve Repair"}
            </Button>
          </section>
          ) : null}
        </aside>
      </div>
    </Shell>
  );
}

function RepairItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Repair Units" badge={`${formatCount(items.length)} units`} />
      {items.length ? (
        <div className="overflow-x-auto border-t border-nexus-line">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-800/80 text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">SKU</th>
                <th className="px-4 py-3 font-medium">Unit ID</th>
                <th className="px-4 py-3 font-medium">Serial</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                  <td className="px-4 py-3 font-semibold text-white">{item.product_name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{item.product_sku || "-"}</td>
                  <td className="px-4 py-3 text-zinc-400">#{item.product_unit}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-300">{item.serial_number || "-"}</td>
                  <td className="px-4 py-3">
                    <Status status={item.product_unit_status_label || item.product_unit_status} statusClass={item.product_unit_status} />
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{item.notes || item.resolution_notes || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No repair units are linked to this record.
        </p>
      )}
    </section>
  );
}

function CreateRepairPage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    repairReason: "",
    reportedByName: "",
    repairLocation: "",
    technician: "",
    repairDate: today,
    expectedResolutionDate: "",
    notes: ""
  });
  const [units, setUnits] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadUnits() {
      const response = await fetch(`${data.api.productUnits}?status=available`, {
        signal: controller.signal
      });
      setUnits(response.ok ? await response.json() : []);
    }

    loadUnits().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load available stock units.");
      }
    });

    return () => controller.abort();
  }, [data.api.productUnits]);

  const selectedIds = new Set(selectedUnits.map((unit) => unit.id));
  const filteredUnits = units
    .filter((unit) => !selectedIds.has(unit.id))
    .filter((unit) => {
      const text = `${unit.product_name} ${unit.product_sku} ${unit.product_barcode || ""} ${unit.serial_number}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 8);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addUnit(unit) {
    setSelectedUnits((current) => [...current, unit]);
    setQuery("");
  }

  function removeUnit(unitId) {
    setSelectedUnits((current) => current.filter((unit) => unit.id !== unitId));
  }

  async function saveRepair() {
    setSaving(true);
    setError("");
    try {
      if (!form.repairReason.trim() || !selectedUnits.length) {
        throw new Error("Repair reason and at least one available stock unit are required.");
      }

      const response = await fetch(data.api.repairs, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          repair_reason: form.repairReason,
          reported_by_name: form.reportedByName,
          repair_location: form.repairLocation,
          technician: form.technician,
          repair_date: form.repairDate || null,
          expected_resolution_date: form.expectedResolutionDate || null,
          notes: form.notes,
          unit_ids: selectedUnits.map((unit) => unit.id)
        })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not create repair.");
      }

      const created = await response.json();
      window.location.assign(created.id ? `/operations/repairs/${created.id}/` : data.routes.repairRecords);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">Create Repair</h1>
              <p className="bim-page-description">Move active available stock into repair, testing, or diagnosis.</p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/operations/repairs/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled={saving} onClick={saveRepair} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Icon name="wrench" className="h-4 w-4" />
                Save Repair
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="wrench" title="Repair Information" subtitle="Operational repair or testing details for selected stock units.">
            <div className="grid gap-5 md:grid-cols-2">
              <Field label="Repair Reason" required>
                <TextInput value={form.repairReason} onChange={(value) => updateField("repairReason", value)} placeholder="Why this stock is going to repair" />
              </Field>
              <Field label="Reported By">
                <TextInput value={form.reportedByName} onChange={(value) => updateField("reportedByName", value)} placeholder="Person, team, or branch" />
              </Field>
              <Field label="Repair Location">
                <TextInput value={form.repairLocation} onChange={(value) => updateField("repairLocation", value)} placeholder="Workshop, vendor, or shelf" />
              </Field>
              <Field label="Technician">
                <TextInput value={form.technician} onChange={(value) => updateField("technician", value)} placeholder="Responsible person or vendor" />
              </Field>
              <Field label="Repair Date">
                <TextInput type="date" value={form.repairDate} onChange={(value) => updateField("repairDate", value)} />
              </Field>
              <Field label="Expected Resolution">
                <TextInput type="date" value={form.expectedResolutionDate} onChange={(value) => updateField("expectedResolutionDate", value)} />
              </Field>
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Operational notes" />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Available Units" subtitle="Only active available units can be sent to repair. Reserved, issued, and sold units must use their own workflows before repair.">
            <SearchBar
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search product, SKU, barcode, or serial..."
            />
            {filteredUnits.length ? (
              <div className="mt-2 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
                {filteredUnits.map((unit) => (
                  <button
                    key={unit.id}
                    onClick={() => addUnit(unit)}
                    type="button"
                    className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                  >
                    <span>
                      <span className="block text-sm font-bold text-white">{unit.product_name}</span>
                      <span className="font-mono text-xs text-nexus-orange">{unit.serial_number}</span>
                    </span>
                    <Plus className="h-4 w-4 text-zinc-500" />
                  </button>
                ))}
              </div>
            ) : null}

            <SelectedUnitsTable units={selectedUnits} onRemove={removeUnit} emptyText="No units selected for repair yet." />
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Repair Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reason" value={form.repairReason || "-"} />
              <DetailRow label="Repair Date" value={formatDate(form.repairDate)} />
              <DetailRow label="Expected Resolution" value={formatDate(form.expectedResolutionDate)} />
              <DetailRow label="Selected Units" value={selectedUnits.length} strong />
              <DetailRow label="Status" value="Draft" />
            </dl>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function repairStatusLabel(record) {
  if (!record?.status) return "-";
  if (record.status === "resolved" && record.resolution) {
    return `Resolved to ${record.resolution}`;
  }
  return record.status.charAt(0).toUpperCase() + record.status.slice(1);
}

function issueStatusLabel(record) {
  if (!record?.status) return "-";
  return record.status.charAt(0).toUpperCase() + record.status.slice(1);
}

function reservationStatusLabel(record) {
  if (!record?.status) return "-";
  return record.status.charAt(0).toUpperCase() + record.status.slice(1);
}

function ClientReturnRecordsPage({ data }) {
  const canCreateClientReturn = Boolean(data.permissions?.canCreateClientReturn);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadClientReturns() {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set("q", query.trim());
        const endpoint = params.toString()
          ? `${data.api.clientReturns}?${params.toString()}`
          : data.api.clientReturns;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error("Could not load client return records.");
        }
        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadClientReturns();
    return () => controller.abort();
  }, [data.api.clientReturns, query]);

  const totalUnits = records.reduce((sum, record) => sum + Number(record.total_units || 0), 0);
  const repairCount = records.filter((record) => record.resolution === "repair").length;
  const latestRecord = records[0];
  const returnKpis = [
    {
      label: "Client Returns",
      value: formatCount(records.length),
      detail: "operational return records",
      icon: "reset",
      tone: "green"
    },
    {
      label: "Returned Units",
      value: formatCount(totalUnits),
      detail: "sold units brought back",
      icon: "layers",
      tone: "blue"
    },
    {
      label: "Sent To Repair",
      value: formatCount(repairCount),
      detail: "records resolved to repair",
      icon: "wrench",
      tone: repairCount > 0 ? "warning" : "neutral"
    },
    {
      label: "Latest Return",
      value: latestRecord ? formatDate(latestRecord.return_date) : "-",
      detail: latestRecord?.return_number || "no returns yet",
      icon: "clock-3",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Client Returns</h1>
          <p className="bim-page-description">Record sold units that came back from a client.</p>
        </div>
        {canCreateClientReturn ? (
          <Button as="a" href={data.routes.createClientReturn} variant="primary">
            <Plus className="h-4 w-4" />
            Create Client Return
          </Button>
        ) : null}
      </header>

      <KpiGrid items={returnKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search return number, delivery, client, received from, reason, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <ClientReturnRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function ClientReturnRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Return</th>
              <th className="px-4 py-3 font-medium">Client</th>
              <th className="px-4 py-3 font-medium">Received From</th>
              <th className="px-4 py-3 font-medium">Return Date</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Resolution</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading client return records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`/operations/client-returns/${record.id}/`} className="font-mono text-xs font-bold text-nexus-orange hover:text-orange-300">
                      {record.return_number}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">{record.delivery_number || "delivery linked by item"}</p>
                  </td>
                  <td className="px-4 py-4 font-semibold text-white">{record.client_name || record.customer_name || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{record.received_from || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.return_date)}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_units || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={clientReturnResolutionLabel(record.resolution)} statusClass={record.resolution} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No client returns yet."
                    description="Create Client Return records sold stock that came back without changing the original delivery."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ClientReturnRecordDetailPage({ data }) {
  const returnId = (data.currentPath || window.location.pathname).match(/\/operations\/client-returns\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadClientReturn() {
      setLoading(true);
      setError("");
      try {
        const endpoint = data.api.clientReturnDetail.replace("{id}", returnId);
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(response.status === 404 ? "Client return record was not found." : "Could not load client return record.");
        }
        setRecord(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadClientReturn();
    return () => controller.abort();
  }, [data.api.clientReturnDetail, returnId]);

  if (loading) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-zinc-400">
          Loading client return record...
        </div>
      </Shell>
    );
  }

  if (error || !record) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-red-200">
          {error || "Client return record was not found."}
        </div>
      </Shell>
    );
  }

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href={data.routes.clientReturnRecords} className="mb-2 inline-flex text-sm font-semibold text-nexus-orange hover:text-orange-300">
            Back to client returns
          </a>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="bim-page-title">{record.return_number}</h1>
            <Status status={clientReturnResolutionLabel(record.resolution)} statusClass={record.resolution} />
          </div>
          <p className="bim-page-description">
            Client return is not a delivery cancellation and not a financial refund or credit.
          </p>
        </div>
      </header>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
            <SectionTitle title="Return Details" />
            <dl className="mt-4 divide-y divide-nexus-line">
              <DetailRow label="Original Delivery" value={record.delivery_number || "-"} />
              <DetailRow label="Client" value={record.client_name || record.customer_name || "-"} />
              <DetailRow label="Received From" value={record.received_from || "-"} />
              <DetailRow label="Return Date" value={formatDate(record.return_date)} />
              <DetailRow label="Reason" value={record.reason || "-"} />
              <DetailRow label="Resolution" value={clientReturnResolutionLabel(record.resolution)} />
              <DetailRow label="Received By" value={record.received_by_name || "-"} />
              <DetailRow label="Notes" value={record.notes || "-"} />
            </dl>
          </section>

          <ClientReturnItemsTable items={record.items || []} />
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Return Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value={record.return_number} />
              <DetailRow label="Resolution" value={clientReturnResolutionLabel(record.resolution)} />
              <DetailRow label="Units" value={record.total_units || 0} strong />
            </dl>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function ClientReturnItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Returned Units" badge={`${formatCount(items.length)} units`} />
      {items.length ? (
        <div className="overflow-x-auto border-t border-nexus-line">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-800/80 text-zinc-400">
              <tr>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">SKU</th>
                <th className="px-4 py-3 font-medium">Original Delivery</th>
                <th className="px-4 py-3 font-medium">Serial</th>
                <th className="px-4 py-3 font-medium">Current Status</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                  <td className="px-4 py-3 font-semibold text-white">{item.product_name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{item.product_sku || "-"}</td>
                  <td className="px-4 py-3 text-zinc-400">{item.delivery_number || "-"}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-300">{item.serial_number || "-"}</td>
                  <td className="px-4 py-3">
                    <Status status={item.product_unit_status_label || item.product_unit_status} statusClass={item.product_unit_status} />
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{item.notes || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No returned units are linked to this record.
        </p>
      )}
    </section>
  );
}

function CreateClientReturnPage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const deliveryId = new URLSearchParams(window.location.search).get("delivery") || "";
  const [form, setForm] = useState({
    client: "",
    customerName: "",
    receivedFrom: "",
    returnDate: today,
    reason: "",
    resolution: "available",
    notes: ""
  });
  const [units, setUnits] = useState([]);
  const [clients, setClients] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadUnits() {
      const [response, clientsResponse] = await Promise.all([
        fetch(`${data.api.productUnits}?status=sold`, { signal: controller.signal }),
        fetch(data.api.clients, { signal: controller.signal })
      ]);
      setUnits(response.ok ? await response.json() : []);
      setClients(clientsResponse.ok ? await clientsResponse.json() : []);
    }

    loadUnits().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load sold stock units.");
      }
    });

    return () => controller.abort();
  }, [data.api.clients, data.api.productUnits]);

  const selectedIds = new Set(selectedUnits.map((unit) => unit.id));
  const filteredUnits = units
    .filter((unit) => !selectedIds.has(unit.id))
    .filter((unit) => {
      const text = `${unit.product_name} ${unit.product_sku} ${unit.product_barcode || ""} ${unit.serial_number}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 8);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addClientItem(item) {
    setClients((current) =>
      current.some((client) => client.id === item.id)
        ? current
        : [...current, item].sort((a, b) => a.name.localeCompare(b.name))
    );
  }

  async function createClientOption(name) {
    if (!name.trim()) {
      throw new Error("Enter a client name before creating it.");
    }
    const response = await fetch(data.api.clients, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": data.csrfToken
      },
      body: JSON.stringify({ name: name.trim() })
    });
    if (!response.ok) {
      const details = await response.json().catch(() => ({}));
      throw new Error(firstApiError(details) || "Could not create client.");
    }
    const created = await response.json();
    addClientItem(created);
    updateField("client", String(created.id));
    updateField("customerName", created.name);
    return created;
  }

  function addUnit(unit) {
    setSelectedUnits((current) => [...current, unit]);
    setQuery("");
  }

  function removeUnit(unitId) {
    setSelectedUnits((current) => current.filter((unit) => unit.id !== unitId));
  }

  async function saveClientReturn() {
    setSaving(true);
    setError("");
    try {
      const selectedClient = clients.find((client) => String(client.id) === String(form.client));
      if (!selectedClient || !selectedUnits.length) {
        throw new Error("Client name and at least one sold stock unit are required.");
      }

      const payload = {
        client: selectedClient.id,
        customer_name: selectedClient.name,
        received_from: form.receivedFrom,
        return_date: form.returnDate || null,
        reason: form.reason,
        resolution: form.resolution,
        notes: form.notes,
        unit_ids: selectedUnits.map((unit) => unit.id)
      };
      if (deliveryId) {
        payload.delivery = Number(deliveryId);
      }

      const response = await fetch(data.api.clientReturns, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not create client return.");
      }

      const created = await response.json();
      window.location.assign(created.id ? `/operations/client-returns/${created.id}/` : data.routes.clientReturnRecords);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">Create Client Return</h1>
              <p className="bim-page-description">
                Record sold stock returned by a client. This is not a delivery cancellation and not a financial refund or credit.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/operations/client-returns/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled={saving} onClick={saveClientReturn} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Icon name="reset" className="h-4 w-4" />
                Save Client Return
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="reset" title="Client Return Information" subtitle="Original delivery remains completed; this creates a separate operational return record.">
            <div className="grid gap-5 md:grid-cols-2">
              <SearchableCreatableSelect
                label="Client"
                required
                value={form.client}
                onChange={(value) => {
                  const selected = clients.find((client) => String(client.id) === String(value));
                  updateField("client", value);
                  updateField("customerName", selected?.name || "");
                }}
                options={clients}
                onCreate={createClientOption}
                placeholder="Search or create client..."
                helperText="Client Return is operational stock tracking only, not a refund or credit."
              />
              <Field label="Received From">
                <TextInput value={form.receivedFrom} onChange={(value) => updateField("receivedFrom", value)} placeholder="Person who returned the unit" />
              </Field>
              <Field label="Return Date">
                <TextInput type="date" value={form.returnDate} onChange={(value) => updateField("returnDate", value)} />
              </Field>
              <Field label="Resolution" required>
                <SelectInput
                  value={form.resolution}
                  onChange={(value) => updateField("resolution", value)}
                  options={[
                    ["available", "Return to available"],
                    ["repair", "Send to repair"]
                  ]}
                />
              </Field>
              <Field label="Reason">
                <TextInput value={form.reason} onChange={(value) => updateField("reason", value)} placeholder="Reason for the return" />
              </Field>
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Operational notes" />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Sold Units" subtitle="Only active sold units linked to completed delivery items can be returned. Reserved, issued, repair, inactive, or available units are blocked.">
            <SearchBar
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search product, SKU, barcode, or serial..."
            />
            {filteredUnits.length ? (
              <div className="mt-2 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
                {filteredUnits.map((unit) => (
                  <button
                    key={unit.id}
                    onClick={() => addUnit(unit)}
                    type="button"
                    className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                  >
                    <span>
                      <span className="block text-sm font-bold text-white">{unit.product_name}</span>
                      <span className="font-mono text-xs text-nexus-orange">{unit.serial_number}</span>
                    </span>
                    <Plus className="h-4 w-4 text-zinc-500" />
                  </button>
                ))}
              </div>
            ) : null}

            <SelectedUnitsTable units={selectedUnits} onRemove={removeUnit} emptyText="No sold units selected for client return yet." />
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Return Summary" />
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Client" value={clients.find((client) => String(client.id) === String(form.client))?.name || "-"} />
              <DetailRow label="Return Date" value={formatDate(form.returnDate)} />
              <DetailRow label="Resolution" value={clientReturnResolutionLabel(form.resolution)} />
              <DetailRow label="Selected Units" value={selectedUnits.length} strong />
            </dl>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function clientReturnResolutionLabel(resolution) {
  if (resolution === "repair") return "Send to repair";
  if (resolution === "available") return "Return to available";
  return resolution || "-";
}

function DeliveryRecordsPage({ data }) {
  const canCreateDelivery = Boolean(data.permissions?.canCreateDelivery);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());

    async function loadDeliveryRecords() {
      setLoading(true);
      setError("");
      try {
        const endpoint = params.toString()
          ? `${data.api.deliveries}?${params.toString()}`
          : data.api.deliveries;
        const response = await fetch(endpoint, { signal: controller.signal });

        if (!response.ok) {
          throw new Error("Could not load delivery records.");
        }

        setRecords(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadDeliveryRecords();
    return () => controller.abort();
  }, [data.api.deliveries, query]);

  const totalUnits = records.reduce((sum, record) => sum + Number(record.total_units || 0), 0);
  const recentRecord = records[0];
  const completedCount = records.filter((record) => record.status === "completed").length;
  const deliveryKpis = [
    {
      label: "Delivery Records",
      value: formatCount(records.length),
      detail: "stock exit records",
      icon: "delivery",
      tone: "indigo"
    },
    {
      label: "Delivered Units",
      value: formatCount(totalUnits),
      detail: "physical units issued",
      icon: "box",
      tone: "blue"
    },
    {
      label: "Completed",
      value: formatCount(completedCount),
      detail: "operational delivery records",
      icon: "check-circle-2",
      tone: "green"
    },
    {
      label: "Latest Delivery",
      value: recentRecord ? formatDate(recentRecord.delivery_date) : "-",
      detail: recentRecord?.delivery_number || "no deliveries yet",
      icon: "clock-3",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="bim-page-title">Delivery Records</h1>
          <p className="bim-page-description">Review operational stock-out records.</p>
        </div>
        {canCreateDelivery ? (
          <Button as="a" href={data.routes.createDelivery} variant="primary">
            <Plus className="h-4 w-4" />
            Create Delivery
          </Button>
        ) : null}
      </header>

      <KpiGrid items={deliveryKpis} />

      <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <SearchBar
            className="flex-1"
            inputClassName="placeholder:text-zinc-500"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search delivery number, client, receiver, product, or serial..."
          />
          <span className="text-xs text-zinc-500">{records.length} records</span>
        </div>
      </section>

      <DeliveryRecordsTable records={records} loading={loading} error={error} />
    </Shell>
  );
}

function DeliveryRecordsTable({ records, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Delivery</th>
              <th className="px-4 py-3 font-medium">Client</th>
              <th className="px-4 py-3 font-medium">Receiver</th>
              <th className="px-4 py-3 font-medium">Delivery Date</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading delivery records..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : records.length ? (
              records.map((record) => (
                <tr key={record.id} className="border-t border-nexus-line hover:bg-zinc-900/70">
                  <td className="px-4 py-4">
                    <a href={`/operations/deliveries/${record.id}/`} className="font-mono text-xs font-bold text-nexus-orange hover:text-orange-300">
                      {record.delivery_number}
                    </a>
                    <p className="mt-1 text-xs text-zinc-500">Created by {record.created_by_name || "-"}</p>
                  </td>
                  <td className="px-4 py-4">
                    <p className="font-semibold text-white">{record.client_name || record.customer_name || "-"}</p>
                    <p className="mt-1 text-xs text-zinc-500">Stock exit</p>
                  </td>
                  <td className="px-4 py-4 text-zinc-300">{record.receiver_name || "-"}</td>
                  <td className="px-4 py-4 text-zinc-300">{formatDate(record.delivery_date)}</td>
                  <td className="px-4 py-4">
                    <p className="font-bold text-white">{formatCount(record.total_units || 0)}</p>
                    <p className="mt-1 text-xs text-zinc-500">{formatCount(record.items?.length || 0)} lines</p>
                  </td>
                  <td className="px-4 py-4">
                    <Status status={deliveryStatusLabel(record)} statusClass={deliveryStatusClass(record)} />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No delivery records yet."
                    description="Create Delivery will create the first operational stock-out record."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DeliveryRecordDetailPage({ data }) {
  const deliveryId = (data.currentPath || window.location.pathname).match(/\/operations\/deliveries\/(\d+)\//)?.[1];
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [editing, setEditing] = useState(false);
  const [savingCorrection, setSavingCorrection] = useState(false);
  const [correctionError, setCorrectionError] = useState("");
  const [correctionMessage, setCorrectionMessage] = useState("");
  const [correctionForm, setCorrectionForm] = useState({
    customerName: "",
    receiverName: "",
    deliveryDate: "",
    notes: "",
    items: []
  });
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState("");

  const isCancelled = record?.status === "cancelled" || record?.isactive === false;
  const canEditDelivery = Boolean(data.permissions?.canEditDelivery);
  const canCancelDelivery = Boolean(data.permissions?.canCancelDelivery);
  const canCreateClientReturn = Boolean(data.permissions?.canCreateClientReturn);

  useEffect(() => {
    const controller = new AbortController();

    async function loadDeliveryRecord() {
      setLoading(true);
      setError("");
      setNotFound(false);
      try {
        const endpoint = data.api.deliveryDetail.replace("{id}", deliveryId);
        const response = await fetch(endpoint, { signal: controller.signal });

        if (response.status === 404) {
          setNotFound(true);
          setRecord(null);
          return;
        }
        if (!response.ok) {
          throw new Error("Could not load delivery record.");
        }

        setRecord(await response.json());
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadDeliveryRecord();
    return () => controller.abort();
  }, [data.api.deliveryDetail, deliveryId, reloadKey]);

  useEffect(() => {
    if (!record) return;
    setCorrectionForm({
      customerName: record.customer_name || "",
      receiverName: record.receiver_name || "",
      deliveryDate: record.delivery_date || "",
      notes: record.notes || "",
      items: (record.items || []).map((item) => ({
        id: item.id,
        notes: item.notes || ""
      }))
    });
  }, [record]);

  function updateCorrectionField(field, value) {
    setCorrectionForm((current) => ({ ...current, [field]: value }));
  }

  function updateCorrectionItem(itemId, value) {
    setCorrectionForm((current) => ({
      ...current,
      items: current.items.map((item) =>
        item.id === itemId ? { ...item, notes: value } : item
      )
    }));
  }

  async function saveDeliveryCorrection() {
    if (!canEditDelivery) return;
    setSavingCorrection(true);
    setCorrectionError("");
    setCorrectionMessage("");
    try {
      const endpoint = data.api.deliveryDetail.replace("{id}", deliveryId);
      const response = await fetch(endpoint, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          customer_name: correctionForm.customerName,
          receiver_name: correctionForm.receiverName,
          delivery_date: correctionForm.deliveryDate,
          notes: correctionForm.notes,
          items: correctionForm.items.map((item) => ({
            id: item.id,
            notes: item.notes || ""
          }))
        })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not update delivery record.");
      }
      setEditing(false);
      setCorrectionMessage("Delivery details updated.");
      setReloadKey((current) => current + 1);
    } catch (saveError) {
      setCorrectionError(saveError.message);
    } finally {
      setSavingCorrection(false);
    }
  }

  async function cancelDeliveryRecord() {
    if (!canCancelDelivery) return;
    setCancelling(true);
    setCancelError("");
    setCorrectionMessage("");
    try {
      if (!cancelReason.trim()) {
        throw new Error("Enter a cancellation reason.");
      }
      const endpoint = data.api.deliveryDetail.replace("{id}", deliveryId).replace(/\/$/, "/cancel/");
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({ cancel_reason: cancelReason })
      });
      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not cancel delivery record.");
      }
      setCancelOpen(false);
      setCancelReason("");
      setCorrectionMessage("Delivery record cancelled. Linked untouched sold units were moved back to available stock.");
      setReloadKey((current) => current + 1);
    } catch (cancelSaveError) {
      setCancelError(cancelSaveError.message);
    } finally {
      setCancelling(false);
    }
  }

  return (
    <Shell data={data}>
      <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <a href={data.routes.deliveryRecords} className="inline-flex items-center gap-2 text-sm font-semibold text-nexus-orange hover:text-orange-300">
            <ChevronRight className="h-4 w-4 rotate-180" />
            Back to Delivery Records
          </a>
          <h1 className="mt-3 bim-page-title">Delivery Record</h1>
          <p className="bim-page-description">Operational stock-out detail.</p>
        </div>
        {record ? (
          <div className="flex flex-wrap items-center gap-3">
            <Status status={deliveryStatusLabel(record)} statusClass={deliveryStatusClass(record)} />
            {!isCancelled && (canCreateClientReturn || canEditDelivery || canCancelDelivery) ? (
              <>
                {canCreateClientReturn ? (
                  <Button as="a" href={`/operations/client-returns/new/?delivery=${record.id}`} variant="outline">
                    <Icon name="reset" className="h-4 w-4" />
                    Create Client Return
                  </Button>
                ) : null}
                {canEditDelivery ? (
                  <Button type="button" variant="outline" onClick={() => setEditing((current) => !current)}>
                    <Edit3 className="h-4 w-4" />
                    Edit Details
                  </Button>
                ) : null}
                {canCancelDelivery ? (
                  <Button type="button" variant="secondary" onClick={() => setCancelOpen((current) => !current)}>
                    <RotateCcw className="h-4 w-4" />
                    Cancel Record
                  </Button>
                ) : null}
              </>
            ) : null}
          </div>
        ) : null}
      </header>

      {correctionMessage ? (
        <section className="mb-4 rounded-lg border border-nexus-green/50 bg-green-500/10 px-4 py-3 text-sm font-semibold text-green-200">
          {correctionMessage}
        </section>
      ) : null}

      {loading ? (
        <section className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-sm text-zinc-500">
          Loading delivery record...
        </section>
      ) : error ? (
        <section className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-sm font-semibold text-red-200">
          {error}
        </section>
      ) : notFound ? (
        <EmptyState
          className="rounded-lg border border-nexus-line bg-nexus-panel"
          title="Delivery record not found."
          description="The record may have been removed or you may not have access."
        />
      ) : record ? (
        <>
        {editing && canEditDelivery ? (
          <DeliveryCorrectionPanel
            form={correctionForm}
            items={record.items || []}
            saving={savingCorrection}
            error={correctionError}
            onFieldChange={updateCorrectionField}
            onItemChange={updateCorrectionItem}
            onCancel={() => {
              setEditing(false);
              setCorrectionError("");
            }}
            onSave={saveDeliveryCorrection}
          />
        ) : null}

        {cancelOpen && canCancelDelivery ? (
          <section className="mb-5 rounded-lg border border-nexus-red/60 bg-red-500/10 p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <h2 className="text-sm font-bold text-red-100">Cancel delivery record</h2>
                <p className="mt-1 text-sm text-red-200/80">
                  Cancellation is only allowed while linked units are still active, sold, and untouched. Wrong unit, product, or serial entries should be cancelled and recreated when safe.
                </p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setCancelOpen(false)}>
                <X className="h-4 w-4" />
                Close
              </Button>
            </div>
            <div className="mt-4">
              <Field label="Cancellation reason" required>
                <TextInput value={cancelReason} onChange={setCancelReason} placeholder="Explain the delivery mistake" />
              </Field>
            </div>
            {cancelError ? <p className="mt-3 text-sm font-semibold text-red-200">{cancelError}</p> : null}
            <div className="mt-4 flex flex-wrap gap-3">
              <Button type="button" variant="danger" loading={cancelling} onClick={cancelDeliveryRecord}>
                <RotateCcw className="h-4 w-4" />
                Confirm Cancel
              </Button>
              <Button type="button" variant="secondary" onClick={() => setCancelOpen(false)}>
                Keep Record
              </Button>
            </div>
          </section>
        ) : null}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
          <div className="min-w-0 space-y-5">
            <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="bim-section-title">Delivery Number</p>
                  <h2 className="mt-2 font-mono text-2xl font-bold text-nexus-orange">{record.delivery_number}</h2>
                </div>
                <div className="grid gap-3 text-sm md:min-w-48 md:text-right">
                  <div>
                    <p className="bim-helper-text">Delivery Date</p>
                    <p className="mt-1 text-zinc-300">{formatDate(record.delivery_date)}</p>
                  </div>
                  <div>
                    <p className="bim-helper-text">Status</p>
                    <p className="mt-1 text-zinc-300">{deliveryStatusLabel(record)}</p>
                  </div>
                </div>
              </div>

              <dl className="mt-5 grid gap-4 md:grid-cols-2">
                <DetailRow label="Client" value={record.client_name || record.customer_name || "-"} strong />
                <DetailRow label="Receiver" value={record.receiver_name || "-"} />
                <DetailRow label="Delivery Date" value={formatDate(record.delivery_date)} />
                <DetailRow label="Created By" value={record.created_by_name || "-"} />
                <DetailRow label="Total Units" value={formatCount(record.total_units || 0)} highlight />
                <DetailRow label="Status" value={deliveryStatusLabel(record)} />
              </dl>

              {record.notes ? (
                <div className="mt-5 rounded-lg border border-nexus-line bg-nexus-panel2 p-4">
                  <p className="bim-helper-text">Notes</p>
                  <p className="mt-2 text-sm text-zinc-300">{record.notes}</p>
                </div>
              ) : null}
            </section>

            <DeliveryItemsTable items={record.items || []} />
          </div>

          <aside className="rounded-lg border border-nexus-line bg-nexus-panel p-4 xl:sticky xl:top-5 xl:self-start">
            <h2 className="bim-section-title">Activity</h2>
            <div className="mt-4 space-y-3 text-sm">
              <DetailRow label="Record Status" value={deliveryStatusLabel(record)} highlight />
              <DetailRow label="Created" value={formatDate(record.crdate)} />
              <DetailRow label="Item Lines" value={formatCount(record.items?.length || 0)} />
              <DetailRow label="Delivery Type" value="Operational stock exit" />
              {isCancelled ? (
                <>
                  <DetailRow label="Cancelled" value={formatDate(record.cancelled_at)} />
                  <DetailRow label="Reason" value={record.cancel_reason || "-"} />
                </>
              ) : null}
            </div>
          </aside>
        </div>
        </>
      ) : null}
    </Shell>
  );
}

function DeliveryCorrectionPanel({
  form,
  items,
  saving,
  error,
  onFieldChange,
  onItemChange,
  onCancel,
  onSave
}) {
  return (
    <section className="mb-5 rounded-lg border border-nexus-line bg-nexus-panel p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-sm font-bold text-white">Edit delivery details</h2>
          <p className="bim-page-description">
            Safe edits are limited to client, receiver, delivery date, notes, and item notes.
          </p>
        </div>
        <Button type="button" variant="ghost" onClick={onCancel}>
          <X className="h-4 w-4" />
          Close
        </Button>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <Field label="Client" required>
          <TextInput value={form.customerName} onChange={(value) => onFieldChange("customerName", value)} />
        </Field>
        <Field label="Receiver">
          <TextInput value={form.receiverName} onChange={(value) => onFieldChange("receiverName", value)} />
        </Field>
        <Field label="Delivery Date" required>
          <TextInput type="date" value={form.deliveryDate} onChange={(value) => onFieldChange("deliveryDate", value)} />
        </Field>
        <Field label="Notes">
          <TextInput value={form.notes} onChange={(value) => onFieldChange("notes", value)} />
        </Field>
      </div>

      <div className="mt-5 rounded-lg border border-nexus-line bg-nexus-panel2">
        <PanelHeader title="Item Notes" badge={formatCount(items.length)} />
        <div className="divide-y divide-nexus-line">
          {items.length ? (
            items.map((item) => {
              const formItem = form.items.find((entry) => entry.id === item.id);
              return (
                <div key={item.id} className="grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_minmax(220px,0.8fr)]">
                  <div>
                    <p className="font-semibold text-white">{item.product_name}</p>
                    <p className="mt-1 font-mono text-xs text-zinc-500">{item.serial_number || "-"}</p>
                  </div>
                  <Field label="Line Notes">
                    <TextInput value={formItem?.notes || ""} onChange={(value) => onItemChange(item.id, value)} />
                  </Field>
                </div>
              );
            })
          ) : (
            <EmptyState
              className="border-t border-nexus-line"
              title="No item lines on this record."
              description="There are no item notes to edit."
            />
          )}
        </div>
      </div>

      {error ? <p className="mt-3 text-sm font-semibold text-red-200">{error}</p> : null}
      <div className="mt-5 flex flex-wrap gap-3">
        <Button type="button" variant="primary" loading={saving} onClick={onSave}>
          <Save className="h-4 w-4" />
          Save Details
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </section>
  );
}

function DeliveryItemsTable({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Delivered Items" badge={formatCount(items.length)} />
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Product</th>
              <th className="px-4 py-3 font-medium">Unit</th>
              <th className="px-4 py-3 font-medium">Serial Number</th>
              <th className="px-4 py-3 font-medium">Unit Status</th>
              <th className="px-4 py-3 font-medium">Notes</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map((item) => (
                <tr key={item.id} className="border-t border-nexus-line">
                  <td className="px-4 py-4">
                    <p className="font-semibold text-white">{item.product_name}</p>
                    <p className="mt-1 font-mono text-xs text-zinc-500">{item.product_sku || "-"}</p>
                  </td>
                  <td className="px-4 py-4">
                    <p className="font-mono text-xs text-zinc-300">{item.product_unit ? `Unit #${item.product_unit}` : "-"}</p>
                    <p className="mt-1 text-xs text-zinc-500">Product #{item.product || "-"}</p>
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-zinc-300">{item.serial_number || "-"}</td>
                  <td className="px-4 py-4">
                    <Status status={item.product_unit_status_label || item.product_unit_status || "-"} statusClass={item.product_unit_status || "inactive"} />
                  </td>
                  <td className="px-4 py-4 text-zinc-400">{item.notes || "-"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">
                  <EmptyState
                    className="border-t border-nexus-line"
                    title="No item lines on this record."
                    description="This delivery record has no active delivered item rows."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function deliveryStatusLabel(record) {
  if (record.status === "cancelled" || record.isactive === false) return "Cancelled";
  if (record.status === "draft") return "Draft";
  return "Delivered";
}

function deliveryStatusClass(record) {
  if (record.status === "cancelled" || record.isactive === false) return "inactive";
  if (record.status === "draft") return "reserved";
  return "delivered";
}

function Header({ data }) {
  const [greeting, setGreeting] = useState(() => browserGreeting(data.hero.greetingName));

  useEffect(() => {
    function updateGreeting() {
      setGreeting(browserGreeting(data.hero.greetingName));
    }

    updateGreeting();
    const intervalId = window.setInterval(updateGreeting, 60000);
    return () => window.clearInterval(intervalId);
  }, [data.hero.greetingName]);

  return (
    <header className="pb-5">
      <div className="min-w-0">
        <p className="flex items-center gap-2 text-sm font-semibold text-zinc-300">
          <span className="h-2 w-2 rounded-full bg-nexus-blue/80" />
          {greeting}
        </p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">{data.hero.title}</h1>
        <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-zinc-400">
          <span>{data.hero.subtitle}</span>
          <span className="text-zinc-600">-</span>
          <span>
            Built for <strong className="font-bold text-zinc-300">BIMPOS</strong>
          </span>
        </p>
        <SearchBar
          className="mt-4 max-w-xl cursor-not-allowed rounded-lg bg-nexus-panel opacity-60"
          inputClassName="cursor-not-allowed placeholder:text-zinc-500"
          type="search"
          disabled
          title="Global search coming later"
          placeholder="Global search coming later..."
        />
      </div>
    </header>
  );
}

function InventoryPage({ data }) {
  const initialInventoryParams = new URLSearchParams(window.location.search);
  const [products, setProducts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [refs, setRefs] = useState({ categories: [], brands: [] });
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [status, setStatus] = useState(() => initialInventoryParams.get("status") || "");
  const [stockFilter, setStockFilter] = useState(() => initialInventoryParams.get("stock") || "");
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (category) params.set("category", category);
    if (brand) params.set("brand", brand);
    if (status) params.set("status", status);

    async function loadInventory() {
      setLoading(true);
      setError("");
      try {
        const [productsResponse, summaryResponse, categoriesResponse, brandsResponse] =
          await Promise.all([
            fetch(`${data.api.products}?${params.toString()}`, { signal: controller.signal }),
            fetch(data.api.summary, { signal: controller.signal }),
            fetch(data.api.categories, { signal: controller.signal }),
            fetch(data.api.brands, { signal: controller.signal })
          ]);

        if (!productsResponse.ok || !summaryResponse.ok) {
          throw new Error("BIM Stock API request failed.");
        }

        const productData = await productsResponse.json();
        const summaryData = await summaryResponse.json();
        const categoryData = categoriesResponse.ok ? await categoriesResponse.json() : [];
        const brandData = brandsResponse.ok ? await brandsResponse.json() : [];

        setProducts(productData);
        setSummary(summaryData);
        setRefs({ categories: categoryData, brands: brandData });
        setSelectedId((current) => current || productData[0]?.id || null);
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadInventory();
    return () => controller.abort();
  }, [brand, category, data.api.brands, data.api.categories, data.api.products, data.api.summary, query, status]);

  const visibleProducts = useMemo(() => {
    if (stockFilter === "out") {
      return products.filter((product) => product.available_units === 0);
    }
    if (stockFilter === "low") {
      return products.filter((product) => product.available_units > 0 && product.is_low_stock);
    }
    return products;
  }, [products, stockFilter]);

  const selectedProduct = useMemo(
    () => visibleProducts.find((product) => product.id === selectedId) || visibleProducts[0] || null,
    [visibleProducts, selectedId]
  );
  const lowStockCount = visibleProducts.filter((product) => product.is_low_stock).length;
  const outOfStockCount = visibleProducts.filter((product) => product.available_units === 0).length;
  const inactiveCount = visibleProducts.filter((product) => !product.isactive || product.available_units === 0).length;
  const inventoryKpis = [
    {
      label: "Total Products",
      value: formatCount(summary?.total_products ?? 0),
      detail: "catalogue items",
      icon: "database",
      tone: "blue",
      href: data.routes.inventory
    },
    {
      label: "Available Stock",
      value: formatCount(summary?.available_units ?? 0),
      detail: "units ready to use",
      icon: "layers",
      tone: "green",
      href: data.routes.availableStock
    },
    {
      label: "Reserved Stock",
      value: formatCount(summary?.reserved_units ?? 0),
      detail: "pending allocation",
      icon: "box",
      tone: "neutral",
      href: `${data.routes.inventory}?status=reserved`
    },
    {
      label: "Low Stock Alerts",
      value: formatCount(summary?.low_stock_products ?? 0),
      detail: "products at or below threshold",
      icon: "triangle-alert",
      tone: (summary?.low_stock_products ?? 0) > 0 ? "warning" : "neutral",
      href: data.routes.lowStock
    },
    {
      label: "Out of Stock Products",
      value: formatCount(summary?.out_of_stock_products ?? outOfStockCount),
      detail: "products with no available units",
      icon: "package-x",
      tone: (summary?.out_of_stock_products ?? outOfStockCount) > 0 ? "danger" : "neutral",
      href: data.routes.outOfStock
    }
  ];

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0">
          <InventoryHeader actions={data.quickActions} />
          <KpiGrid items={inventoryKpis} />

          <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center">
              <SearchBar
                className="flex-1"
                inputClassName="placeholder:text-zinc-500"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by product name, SKU, barcode, or serial..."
              />
              <span className="inline-flex items-center gap-2 text-sm text-zinc-400">
                <Filter className="h-4 w-4" />
                Filter
              </span>
              <Select value={category} onChange={setCategory} options={refs.categories.map((item) => [item.id, item.name])} label="Category" />
              <Select value={brand} onChange={setBrand} options={refs.brands.map((item) => [item.id, item.brandname])} label="Brand" />
              <Select
                value={status}
                onChange={(value) => {
                  setStatus(value);
                  setStockFilter("");
                }}
                options={[
                  ["available", "Available"],
                  ["reserved", "Reserved"],
                  ["issued", "Issued"],
                  ["sold", "Sold"],
                  ["repair", "Repair"],
                  ["inactive", "Inactive"]
                ]}
                label="Status"
              />
              <Select
                value={stockFilter}
                onChange={(value) => {
                  setStockFilter(value);
                  if (value) setStatus("");
                }}
                options={[
                  ["low", "Low Stock"],
                  ["out", "Out of Stock"]
                ]}
                label="Stock"
              />
              <span className="text-right text-xs text-zinc-500 xl:ml-auto">
                {visibleProducts.length} products
              </span>
            </div>
          </section>

          <InventoryTable
            products={visibleProducts}
            selectedId={selectedProduct?.id}
            onSelect={setSelectedId}
            loading={loading}
            error={error}
          />
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500">
            <span>Showing {visibleProducts.length} products</span>
            <span>{lowStockCount} low stock - {inactiveCount} inactive</span>
          </div>
        </div>

        <ProductDetail product={selectedProduct} canAccessAdmin={data.user?.canAccessAdmin} />
      </div>
    </Shell>
  );
}

function InventoryHeader({ actions }) {
  const addProduct = actions.find((action) => action.label === "Add Product");
  return (
    <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 className="bim-page-title">BIM Stock</h1>
        <p className="bim-page-description">Manage products and stock availability.</p>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <button
          type="button"
          disabled
          title="Export coming later"
          className="inline-flex h-9 cursor-not-allowed items-center gap-2 rounded-md px-3 font-semibold text-zinc-500"
        >
          <Icon name="upload" className="h-4 w-4" />
          Export
        </button>
        {addProduct?.enabled && addProduct.href ? (
          <a className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black" href={addProduct.href}>
            <Plus className="h-4 w-4" />
            Add Product
          </a>
        ) : null}
      </div>
    </header>
  );
}

function Select({ value, onChange, options, label }) {
  return (
    <select
      aria-label={label}
      className="h-10 rounded-md border border-nexus-line bg-nexus-panel2 px-3 text-sm text-zinc-300 outline-none"
      value={value}
      onChange={(event) => onChange(event.target.value)}
    >
      <option value="">{label}</option>
      {options.map(([optionValue, optionLabel]) => (
        <option key={optionValue} value={optionValue}>
          {optionLabel}
        </option>
      ))}
    </select>
  );
}

function InventoryTable({ products, selectedId, onSelect, loading, error }) {
  return (
    <section className="mt-4 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Product</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">Brand / Model</th>
              <th className="px-4 py-3 font-medium">SKU</th>
              <th className="px-4 py-3 font-medium">Stock</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <TableMessage message="Loading BIM Stock..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : products.length ? (
              products.map((product) => (
                <tr
                  key={product.id}
                  className={`cursor-pointer border-t border-nexus-line hover:bg-zinc-900/70 ${
                    selectedId === product.id ? "bg-amber-950/20 outline outline-1 outline-nexus-orange/50" : ""
                  }`}
                  onClick={() => onSelect(product.id)}
                >
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <Avatar product={product} />
                      <div>
                        <p className="font-semibold text-white">{product.display_name}</p>
                        <p className="mt-1 font-mono text-xs text-zinc-500">{product.sku}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-zinc-400">{product.category_name}</td>
                  <td className="px-4 py-4">
                    <p className="text-zinc-200">{product.brand_name}</p>
                    <p className="mt-1 font-mono text-xs text-zinc-500">{product.model_name}</p>
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-nexus-orange">{product.sku}</td>
                  <td className="px-4 py-4">
                    <StockBar product={product} />
                  </td>
                  <td className="px-4 py-4">
                    <ProductStatus product={product} />
                  </td>
                </tr>
              ))
            ) : (
              <TableMessage message="No products found." />
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function TableMessage({ message }) {
  return (
    <tr>
      <td className="px-4 py-8 text-center text-zinc-500" colSpan="6">
        {message}
      </td>
    </tr>
  );
}

function Avatar({ product }) {
  const letters = (product.brand_name || product.display_name || "?").slice(0, 2).toUpperCase();
  return (
    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-blue-600 text-xs font-bold text-white">
      {letters}
    </span>
  );
}

function StockBar({ product }) {
  const total = Math.max(product.total_units, 1);
  const percent = Math.min(100, Math.round((product.available_units / total) * 100));
  const low = product.is_low_stock;
  const outOfStock = product.available_units === 0;
  return (
    <div className="w-28">
      <p className="text-xs font-semibold text-white">
        <span className={outOfStock ? "text-nexus-red" : low ? "text-nexus-orange" : "text-white"}>{product.available_units}</span>
        <span className="text-zinc-500"> / {product.total_units}</span>
      </p>
      <div className="mt-2 h-1 rounded-full bg-zinc-800">
        <div
          className={`h-1 rounded-full ${outOfStock ? "bg-nexus-red" : low ? "bg-nexus-orange" : "bg-nexus-green"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

function ProductStatus({ product }) {
  let label = "Active";
  let statusKey = "active";
  if (!product.isactive) {
    label = "Inactive";
    statusKey = "inactive";
  } else if (product.available_units === 0) {
    label = "Out of Stock";
    statusKey = "out_of_stock";
  } else if (product.is_low_stock) {
    label = "Low Stock";
    statusKey = "low_stock";
  }
  const meta = statusMeta[statusKey] || statusMeta.active;
  return (
    <span className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-bold ${meta.className}`}>
      <Icon name={meta.icon} className="h-3.5 w-3.5" />
      {label}
    </span>
  );
}

function ProductDetail({ product, canAccessAdmin = false }) {
  if (!product) {
    return (
      <aside className="rounded-lg border border-nexus-line bg-nexus-panel p-4 text-sm text-zinc-500">
        No product selected.
      </aside>
    );
  }

  const availability = product.total_units
    ? Math.round((product.available_units / product.total_units) * 100)
    : 0;
  const optionalFields = [];

  return (
    <aside className="rounded-lg border border-nexus-line bg-nexus-panel xl:sticky xl:top-5 xl:h-[calc(100vh-2.5rem)]">
      <div className="flex items-center justify-between border-b border-nexus-line px-4 py-4">
        <h2 className="bim-section-title">Product Detail</h2>
        <button
          aria-label="Close product detail panel coming later"
          className="cursor-not-allowed text-zinc-600"
          disabled
          title="Panel close coming later"
          type="button"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="space-y-5 p-4">
        <Avatar product={product} />
        <div>
          <h3 className="text-base font-bold text-white">{product.display_name}</h3>
          <p className="text-sm text-zinc-500">{product.brand_name} - {product.model_name}</p>
        </div>

        <dl className="space-y-3 text-sm">
          <DetailRow label="SKU" value={product.sku} />
          <DetailRow label="Barcode" value={product.barcode || "-"} />
          <DetailRow label="Category" value={product.category_name} />
          <DetailRow label="Brand" value={product.brand_name} />
          <DetailRow label="Model" value={product.model_name} />
        </dl>

        <div className="border-t border-nexus-line pt-5">
          <h3 className="bim-section-title">Stock Summary</h3>
          <div className="mt-4">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Stock Availability</span>
              <span className="font-bold text-nexus-orange">{availability}%</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-zinc-800">
              <div className="h-1.5 rounded-full bg-nexus-orange" style={{ width: `${availability}%` }} />
            </div>
          </div>
          <DetailRow label="Available Stock" value={product.available_units} highlight />
          <DetailRow label="Reserved Stock" value={product.reserved_units} />
          <DetailRow label="Total Stock" value={product.total_units} strong />
          <DetailRow label="Sold Stock" value={product.sold_units} />
          <DetailRow label="Low Stock Alert" value={product.reorder_stock_level} />
        </div>

        {canAccessAdmin ? (
          <a
            href={`/admin/bim_stock/productunit/?q=${encodeURIComponent(product.sku)}`}
            className="flex items-center justify-between rounded-lg border border-nexus-line bg-nexus-panel2 px-4 py-3 hover:border-nexus-orange/70"
          >
            <span className="inline-flex items-center gap-3 text-sm font-semibold text-white">
              <Package className="h-4 w-4 text-nexus-orange" />
              Stock Units
            </span>
            <ChevronRight className="h-4 w-4 text-zinc-500" />
          </a>
        ) : null}
      </div>
      <CardFooter className={`mt-auto grid gap-2 p-4 ${canAccessAdmin ? "grid-cols-2" : "grid-cols-1"}`}>
        {canAccessAdmin ? (
          <Button as="a" href={`/admin/bim_stock/product/${product.id}/change/`} variant="outline">
            <Edit3 className="h-4 w-4" />
            Edit
          </Button>
        ) : null}
        <Button as="a" href={`/inventory/products/${product.id}/`} variant="primary">
          <Eye className="h-4 w-4" />
          Full View
        </Button>
        <div className="hidden">
          <h3 className="bim-label">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "âœ“" : "â—‹"} {label}
            </p>
          ))}
        </div>

        <div className="hidden">
          <h3 className="bim-label">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "âœ“" : "â—‹"} {label}
            </p>
          ))}
        </div>
      </CardFooter>
    </aside>
  );
}

function ProductDetailsPage({ data }) {
  const productId = data.currentPath?.match(/\/inventory\/products\/(\d+)\//)?.[1];
  const [product, setProduct] = useState(null);
  const [units, setUnits] = useState([]);
  const [movements, setMovements] = useState([]);
  const [unitsAccessDenied, setUnitsAccessDenied] = useState(false);
  const [movementsAccessDenied, setMovementsAccessDenied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadProduct() {
      setLoading(true);
      setError("");
      try {
        const [productResponse, unitsResponse, movementsResponse] = await Promise.all([
          fetch(data.api.productDetail.replace("{id}", productId), {
            signal: controller.signal
          }),
          fetch(`${data.api.productUnits}?product=${productId}`, {
            signal: controller.signal
          }),
          fetch(data.api.productMovements.replace("{id}", productId), {
            signal: controller.signal
          })
        ]);

        if (!productResponse.ok) {
          throw new Error("Could not load product details.");
        }

        setProduct(await productResponse.json());
        setUnits(unitsResponse.ok ? await unitsResponse.json() : []);
        setMovements(movementsResponse.ok ? await movementsResponse.json() : []);
        setUnitsAccessDenied(unitsResponse.status === 401 || unitsResponse.status === 403);
        setMovementsAccessDenied(movementsResponse.status === 401 || movementsResponse.status === 403);
      } catch (loadError) {
        if (loadError.name !== "AbortError") {
          setError(loadError.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadProduct();
    return () => controller.abort();
  }, [data.api.productDetail, data.api.productMovements, data.api.productUnits, productId]);

  if (loading) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-line bg-nexus-panel p-6 text-zinc-400">
          Loading product details...
        </div>
      </Shell>
    );
  }

  if (error || !product) {
    return (
      <Shell data={data}>
        <div className="rounded-lg border border-nexus-red/60 bg-red-500/10 p-6 text-red-200">
          {error || "Product was not found."}
        </div>
      </Shell>
    );
  }

  const supplierUnit = units.find((unit) => unit.supplier_name);
  const lastCostUnit = [...units].filter((unit) => Number(unit.cost) > 0).pop();
  const stockPercent = product.total_units
    ? Math.round((product.available_units / product.total_units) * 100)
    : 0;
  const receiveStockAction = data.quickActions.find((action) => action.label === "Receive Stock");
  const addStockUnitAction = data.quickActions.find((action) => action.label === "Add Unit");
  const createDeliveryAction = data.quickActions.find((action) => action.label === "Create Delivery");
  const detailActions = [receiveStockAction, addStockUnitAction, createDeliveryAction].filter(
    (action) => action?.enabled && action.href
  );
  const recentActivity = movements.slice(0, 6);

  return (
    <Shell data={data}>
      <header className="mb-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="flex items-start gap-4">
            <Avatar product={product} />
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="bim-page-title">{product.display_name}</h1>
                <ProductStatus product={product} />
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                <span className="font-mono font-bold text-nexus-orange">{product.sku}</span>
                <span className="mx-2">â€¢</span>
                {product.category_name}
                <span className="mx-2">â€¢</span>
                {product.brand_name} {product.model_name}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm">
            {data.user?.canAccessAdmin ? (
              <a href={`/admin/bim_stock/product/${product.id}/change/`} className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <Edit3 className="h-4 w-4" />
                Edit Product
              </a>
            ) : null}
            {detailActions.map((action) => (
              <ProductDetailActionLink
                key={action.label}
                action={action}
                primary={action.label === "Receive Stock" || action.label === "Add Unit"}
              />
            ))}
          </div>
        </div>
      </header>

      <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-6">
        <ProductDetailMetric label="Total Stock" value={product.total_units} detail="registered units" />
        <ProductDetailMetric
          label="Available"
          value={product.available_units}
          detail={`${stockPercent}% in stock`}
          warning={product.is_low_stock}
          danger={product.available_units === 0}
        />
        <ProductDetailMetric label="Reserved" value={product.reserved_units} detail="pending allocation" />
        <ProductDetailMetric label="Low Stock Alert" value={product.reorder_stock_level} detail="alert threshold" info />
      </section>

      <nav className="mt-5 flex gap-1 overflow-x-auto border-b border-nexus-line text-sm font-semibold">
        {[
          ["Overview", ""],
          ["Stock Units", product.total_units],
          ["Movements", movements.length],
          ["Receiving", 0],
          ["Deliveries", 0],
          ["Documents", 0]
        ].map(([label, count], index) => (
          <button
            key={label}
            className={`border-b-2 px-4 py-3 ${index === 0 ? "border-nexus-orange text-nexus-orange" : "border-transparent text-zinc-400"}`}
          >
            {label} {count !== "" ? <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">{count}</span> : null}
          </button>
        ))}
      </nav>

      <div className="mt-4 grid gap-5 xl:grid-cols-[minmax(0,1fr)_280px]">
        <div className="space-y-5">
          <div className="grid gap-5 xl:grid-cols-2">
            <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
                <SectionTitle title="Product Information" />
                <dl className="mt-4 divide-y divide-nexus-line">
                  <DetailRow label="Product Name" value={product.descript} />
                  <DetailRow label="SKU" value={product.sku} />
                <DetailRow label="Barcode" value={product.barcode || "-"} />
                <DetailRow label="Category" value={product.category_name} />
                <DetailRow label="Brand" value={product.brand_name} />
                <DetailRow label="Model" value={product.model_name} />
                <DetailRow label="Unit of Measure" value="Each" />
              </dl>
            </section>

            <div className="space-y-5">
              <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
                <SectionTitle title="Supplier Information" />
                <dl className="mt-4 divide-y divide-nexus-line">
                  <DetailRow label="Default Supplier" value={supplierUnit?.supplier_name || "-"} />
                  <DetailRow label="Last Purchase" value={formatDate(supplierUnit?.purchase_date || supplierUnit?.crdate)} />
                  <DetailRow label="Last Cost" value={formatCurrency(lastCostUnit?.cost)} />
                </dl>
              </section>

              <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
                <SectionTitle title="Stock Availability" />
                <div className="mt-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-400">In-stock rate</span>
                    <span className="font-bold text-nexus-orange">{stockPercent}%</span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-zinc-800">
                    <div className="h-1.5 rounded-full bg-nexus-orange" style={{ width: `${stockPercent}%` }} />
                  </div>
                </div>
                <dl className="mt-4 divide-y divide-nexus-line">
                  <DetailRow label="Available" value={product.available_units} highlight />
                  <DetailRow label="Reserved" value={product.reserved_units} />
                  <DetailRow label="Total" value={product.total_units} strong />
                  <DetailRow label="Low Stock Alert" value={product.reorder_stock_level} />
                </dl>
              </section>
            </div>
          </div>

          <ProductUnitRegister
            product={product}
            units={units}
            accessDenied={unitsAccessDenied}
            canAccessAdmin={data.user?.canAccessAdmin}
          />
          <ProductMovementHistory
            movements={movements}
            accessDenied={movementsAccessDenied}
          />
        </div>

        <aside className="rounded-lg border border-nexus-line bg-nexus-panel">
          <PanelHeader title="Recent Activity" />
          {recentActivity.length ? (
            recentActivity.map((movement) => (
              <div key={movement.id} className="border-t border-nexus-line px-4 py-4">
                <p className="text-sm font-bold text-white">{movement.movement_type_label || movement.movement_type}</p>
                <p className="mt-1 text-xs text-zinc-500">{movement.reference || movement.serial_number || "-"}</p>
                <p className="mt-1 text-xs text-zinc-600">{formatDate(movement.movement_date || movement.crdate)}</p>
              </div>
            ))
          ) : movementsAccessDenied ? (
            <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
              Movement history requires stock movement access.
            </p>
          ) : (
            <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
              No stock movements recorded yet.
            </p>
          )}
          <a href={`/inventory/products/${product.id}/`} className="block border-t border-nexus-line px-4 py-4 text-center text-sm font-semibold text-nexus-orange hover:bg-nexus-panel2">
            View product detail
          </a>
        </aside>
      </div>
    </Shell>
  );
}

function ProductMovementHistory({ movements, accessDenied }) {
  const visibleMovements = movements.slice(0, 10);

  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel" aria-label="Movement History">
      <PanelHeader title="Movement History" badge={`${formatCount(movements.length)} events`} />
      {accessDenied ? (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          Movement history requires stock movement access.
        </p>
      ) : visibleMovements.length ? (
        <>
          <div className="overflow-x-auto border-t border-nexus-line">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-zinc-800/80 text-zinc-400">
                <tr>
                  <th className="px-4 py-3 font-medium">Date</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Serial</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Reference</th>
                  <th className="px-4 py-3 font-medium">User</th>
                  <th className="px-4 py-3 font-medium">Notes</th>
                </tr>
              </thead>
              <tbody>
                {visibleMovements.map((movement) => (
                  <tr key={movement.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                    <td className="px-4 py-3 text-zinc-400">{formatDate(movement.movement_date || movement.crdate)}</td>
                    <td className="px-4 py-3 font-semibold text-white">{movement.movement_type_label || movement.movement_type}</td>
                    <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{movement.serial_number || "-"}</td>
                    <td className="px-4 py-3 text-zinc-400">
                      {movement.from_status || "-"} {movement.to_status ? "->" : ""} {movement.to_status || ""}
                    </td>
                    <td className="px-4 py-3 text-zinc-400">{movement.reference || movement.receiving_number || movement.delivery_number || "-"}</td>
                    <td className="px-4 py-3 text-zinc-400">{movement.performed_by_name || "-"}</td>
                    <td className="px-4 py-3 text-zinc-400">{movement.notes || movement.reason || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {movements.length > visibleMovements.length ? (
            <p className="border-t border-nexus-line px-4 py-3 text-xs text-zinc-500">
              Showing {visibleMovements.length} of {movements.length} movement events.
            </p>
          ) : null}
        </>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No stock movements are recorded for this product yet.
        </p>
      )}
    </section>
  );
}

function ProductDetailActionLink({ action, primary = false }) {
  return (
    <Button as="a" href={action.href} variant={primary ? "primary" : "secondary"}>
      <Icon name={action.icon} className="h-4 w-4" />
      {action.label}
    </Button>
  );
}

function ProductUnitRegister({ product, units, accessDenied, canAccessAdmin = false }) {
  const visibleUnits = units.slice(0, 10);
  const unitLabel = product.total_units === 1 ? "unit" : "units";

  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel" aria-label="Stock unit register">
      <PanelHeader title="Stock Unit Register" badge={`${formatCount(product.total_units)} ${unitLabel}`} />
      {accessDenied ? (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          Stock-unit details require stock-unit access.
        </p>
      ) : visibleUnits.length ? (
        <>
          <div className="overflow-x-auto border-t border-nexus-line">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-zinc-800/80 text-zinc-400">
                <tr>
                  <th className="px-4 py-3 font-medium">Serial Number</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Supplier</th>
                  <th className="px-4 py-3 font-medium">Cost</th>
                  <th className="px-4 py-3 font-medium">Purchased</th>
                  <th className="px-4 py-3 font-medium">Sold</th>
                  {canAccessAdmin ? <th className="px-4 py-3 font-medium">Admin</th> : null}
                </tr>
              </thead>
              <tbody>
                {visibleUnits.map((unit) => (
                  <tr key={unit.id} className="border-t border-nexus-line hover:bg-nexus-panel2/60">
                    <td className="px-4 py-3 font-mono text-xs text-nexus-orange">{unit.serial_number}</td>
                    <td className="px-4 py-3">
                      <Status status={unit.status_label || unit.status} statusClass={unit.status} />
                    </td>
                    <td className="px-4 py-3 text-zinc-400">{unit.supplier_name || "-"}</td>
                    <td className="px-4 py-3 text-zinc-400">{formatCurrency(unit.cost)}</td>
                    <td className="px-4 py-3 text-zinc-400">{formatDate(unit.purchase_date)}</td>
                    <td className="px-4 py-3 text-zinc-400">{formatDate(unit.sold_date)}</td>
                    {canAccessAdmin ? (
                      <td className="px-4 py-3">
                        <a href={`/admin/bim_stock/productunit/${unit.id}/change/`} className="text-xs font-semibold text-nexus-orange hover:text-white">
                          Edit Unit
                        </a>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {units.length > visibleUnits.length ? (
            <p className="border-t border-nexus-line px-4 py-3 text-xs text-zinc-500">
              Showing {visibleUnits.length} of {units.length} active stock units.
            </p>
          ) : null}
        </>
      ) : (
        <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
          No stock units are registered for this product yet.
        </p>
      )}
    </section>
  );
}

function ProductDetailMetric({ label, value, detail, warning = false, danger = false, info = false }) {
  const color = danger ? "text-nexus-red" : warning ? "text-nexus-orange" : info ? "text-nexus-blue" : "text-white";
  return (
    <article className={`rounded-lg border bg-nexus-panel p-4 ${danger ? "border-nexus-red/70" : warning ? "border-nexus-orange/70" : "border-nexus-line"}`}>
      <p className="text-sm text-zinc-400">{label}</p>
      <p className={`mt-4 text-2xl font-bold ${color}`}>{formatCount(value)}</p>
      <p className="mt-1 text-sm text-zinc-500">{detail}</p>
    </article>
  );
}

function AddProductPage({ data }) {
  const emptyForm = {
    descript: "",
    category: "",
    brand: "",
    modelName: "",
    barcode: "",
    reorderStockLevel: "0",
    notes: "",
    imageFile: null,
    isactive: true
  };
  const [form, setForm] = useState(emptyForm);
  const [refs, setRefs] = useState({ categories: [], brands: [] });
  const [refsLoading, setRefsLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const imageInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadRefs() {
      setRefsLoading(true);
      const [categoriesResponse, brandsResponse] = await Promise.all([
        fetch(data.api.categories, { signal: controller.signal }),
        fetch(data.api.brands, { signal: controller.signal })
      ]);

      setRefs({
        categories: categoriesResponse.ok ? await categoriesResponse.json() : [],
        brands: brandsResponse.ok ? await brandsResponse.json() : []
      });
      setRefsLoading(false);
    }

    loadRefs().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load product form data.");
        setRefsLoading(false);
      }
    });

    return () => controller.abort();
  }, [data.api.brands, data.api.categories]);

  const selectedCategory = refs.categories.find((category) => String(category.id) === String(form.category));
  const selectedBrand = refs.brands.find((brand) => String(brand.id) === String(form.brand));
  const requiredDone = [form.descript, form.category, form.brand, form.modelName].filter(Boolean).length;
  const requiredTotal = 4;
  const requiredProgress = Math.round((requiredDone / requiredTotal) * 100);
  const skuPreview =
    selectedCategory && selectedBrand && form.modelName
      ? `${selectedCategory.name.slice(0, 3).toUpperCase()}-${selectedBrand.brandname.slice(0, 3).toUpperCase()}-${form.modelName.replace(/\s+/g, "").toUpperCase()}`
      : "auto-generate";

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function resetForm() {
    setForm(emptyForm);
    if (imageInputRef.current) {
      imageInputRef.current.value = "";
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = "";
    }
  }

  function selectImageFile(file) {
    if (!file) return;
    if (!["image/png", "image/jpeg"].includes(file.type)) {
      setError("Select a PNG or JPG product image.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Product image must be 5MB or smaller.");
      return;
    }

    setForm((current) => ({ ...current, imageFile: file }));
    setError("");
  }

  function handleImageInputChange(event) {
    selectImageFile(event.target.files?.[0]);
  }

  function handleImageDrop(event) {
    event.preventDefault();
    selectImageFile(event.dataTransfer.files?.[0]);
  }

  function handleImageDragOver(event) {
    event.preventDefault();
  }

  function clearImageFile() {
    setForm((current) => ({ ...current, imageFile: null }));
    if (imageInputRef.current) {
      imageInputRef.current.value = "";
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = "";
    }
  }

  function addLookupItem(listName, item, labelField) {
    setRefs((current) => ({
      ...current,
      [listName]: [...current[listName], item].sort((left, right) =>
        String(left[labelField] || "").localeCompare(String(right[labelField] || ""))
      )
    }));
  }

  async function createLookupOption(kind, name) {
    const lookupConfig = {
      category: {
        endpoint: data.api.categories,
        listName: "categories",
        labelField: "name",
        formField: "category",
        body: (name) => ({ name })
      },
      brand: {
        endpoint: data.api.brands,
        listName: "brands",
        labelField: "brandname",
        formField: "brand",
        body: (name) => ({ brandname: name })
      }
    };
    const config = lookupConfig[kind];
    const trimmedName = name.trim();

    if (!trimmedName) {
      throw new Error("Enter a name before creating a catalogue value.");
    }

    setError("");
    const response = await fetch(config.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": data.csrfToken
      },
      body: JSON.stringify(config.body(trimmedName))
    });

    if (!response.ok) {
      const details = await response.json().catch(() => ({}));
      throw new Error(firstApiError(details) || "Could not create catalogue value.");
    }

    const created = await response.json();
    addLookupItem(config.listName, created, config.labelField);
    updateField(config.formField, String(created.id));
    return created;
  }

  async function saveProduct(addAnother = false) {
    setSaving(true);
    setError("");
    try {
      const payload = new FormData();
      payload.append("descript", form.descript);
      payload.append("category", form.category);
      payload.append("brand", form.brand);
      payload.append("model_name_input", form.modelName);
      payload.append("barcode", form.barcode);
      payload.append("reorder_stock_level", form.reorderStockLevel);
      payload.append("isactive", form.isactive ? "true" : "false");
      if (form.imageFile) {
        payload.append("image", form.imageFile);
      }

      const response = await fetch(data.api.products, {
        method: "POST",
        headers: {
          "X-CSRFToken": data.csrfToken
        },
        body: payload
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not save product.");
      }

      if (addAnother) {
        resetForm();
      } else {
        window.location.assign(data.routes.inventory);
      }
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <AddProductHeader
            saving={saving}
            onReset={resetForm}
            onSave={() => saveProduct(false)}
            onSaveAnother={() => saveProduct(true)}
          />
          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <p className="mb-5 text-sm text-zinc-300">
            Create a new product definition. Stock is added separately after creation.
          </p>

          <FormSection icon="box" title="Product Information" subtitle="Core catalogue fields that define this product.">
            <div className="grid gap-5">
              <Field label="Product Name" required>
                <TextInput value={form.descript} onChange={(value) => updateField("descript", value)} placeholder="Enter product name" />
              </Field>
            </div>

            <div className="mt-5 grid gap-5 md:grid-cols-2">
              <SearchableCreatableSelect
                label="Category"
                required
                value={form.category}
                onChange={(value) => updateField("category", value)}
                options={refs.categories}
                getOptionLabel={(item) => item.name}
                onCreate={(name) => createLookupOption("category", name)}
                placeholder="Search or create category..."
                loading={refsLoading}
              />
              <SearchableCreatableSelect
                label="Brand"
                required
                value={form.brand}
                onChange={(value) => updateField("brand", value)}
                options={refs.brands}
                getOptionLabel={(item) => item.brandname}
                onCreate={(name) => createLookupOption("brand", name)}
                placeholder="Search or create brand..."
                loading={refsLoading}
              />
              <Field label="Model" required>
                <TextInput value={form.modelName} onChange={(value) => updateField("modelName", value)} placeholder="Enter model" />
                <p className="mt-2 text-xs text-zinc-500">Used to generate SKU.</p>
              </Field>
            </div>

            <div className="mt-5 grid gap-5">
              <Field label="SKU Preview">
                <TextInput value={skuPreview === "auto-generate" ? "Full Category, Brand & Model to generate" : skuPreview} disabled />
                <p className="mt-2 text-xs text-zinc-500">Generated from Category + Brand + Model. Read-only.</p>
              </Field>
              <Field label="Barcode">
                <TextInput value={form.barcode} onChange={(value) => updateField("barcode", value)} placeholder="Enter barcode" />
                <p className="mt-2 text-xs text-zinc-500">EAN-13 or UPC barcode (optional).</p>
              </Field>
              <Field label="Low Stock Alert">
                <TextInput value={form.reorderStockLevel} onChange={(value) => updateField("reorderStockLevel", value)} placeholder="Enter alert threshold" />
                <p className="mt-2 text-xs text-zinc-500">When available stock is at or below this number, BIM Nexus shows low stock alerts.</p>
              </Field>
              <Field label="Internal Notes">
                <textarea
                  value={form.notes}
                  onChange={(event) => updateField("notes", event.target.value)}
                  className="min-h-20 w-full rounded-md border border-nexus-line bg-black px-3 py-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
                  placeholder="Add internal notes"
                />
                <p className="mt-2 text-xs text-zinc-500">Optional notes about usage, compatibility, or product details.</p>
              </Field>
            </div>
          </FormSection>

          <FormSection icon="package" title="Product Image" subtitle="Optional photo or icon for this product.">
            <div className="grid gap-5 md:grid-cols-[120px_minmax(0,1fr)]">
              <input
                ref={imageInputRef}
                type="file"
                accept="image/png,image/jpeg"
                className="hidden"
                onChange={handleImageInputChange}
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={handleImageInputChange}
              />
              <button
                type="button"
                onClick={() => imageInputRef.current?.click()}
                onDrop={handleImageDrop}
                onDragOver={handleImageDragOver}
                className="grid aspect-square place-items-center rounded-lg border border-dashed border-nexus-line bg-black text-center text-xs text-zinc-500 hover:border-nexus-orange hover:text-zinc-300"
              >
                <span className="max-w-full break-words px-2">
                  <Package className="mx-auto mb-2 h-6 w-6 text-zinc-500" />
                  {form.imageFile ? (
                    <>
                      Selected
                      <br />
                      {form.imageFile.name}
                    </>
                  ) : (
                    <>
                      Drop image
                      <br />
                      or click to upload
                    </>
                  )}
                </span>
              </button>
              <div>
                <p className="text-sm font-bold text-white">Product Image</p>
                <p className="mt-2 text-sm text-zinc-400">
                  Upload a photo or icon for this product. Used in listings, detail views, and reports.
                </p>
                <p className="mt-4 text-xs text-zinc-500">PNG, JPG - max 5MB</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => imageInputRef.current?.click()}
                    className="inline-flex h-9 items-center gap-2 rounded-md border border-nexus-line px-3 text-xs font-semibold text-zinc-200 hover:bg-nexus-panel"
                  >
                    <Package className="h-4 w-4" />
                    Upload Image
                  </button>
                  <button
                    type="button"
                    onClick={() => cameraInputRef.current?.click()}
                    className="inline-flex h-9 items-center gap-2 rounded-md border border-nexus-line px-3 text-xs font-semibold text-zinc-200 hover:bg-nexus-panel"
                  >
                    <Camera className="h-4 w-4" />
                    Take Photo
                  </button>
                </div>
                {form.imageFile ? (
                  <button type="button" onClick={clearImageFile} className="mt-3 text-xs font-semibold text-nexus-orange hover:text-white">
                    Remove image
                  </button>
                ) : null}
              </div>
            </div>
          </FormSection>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button type="button" onClick={resetForm} className="text-left text-sm font-semibold text-zinc-300 hover:text-white">
              Discard all changes
            </button>
            <div className="flex flex-wrap gap-3">
              <button disabled type="button" className="inline-flex h-10 items-center gap-2 rounded-md bg-zinc-700 px-4 text-sm font-semibold text-zinc-500">
                <Icon name={workflowMeta.receive_stock.icon} className="h-4 w-4" />
                Save & Receive Stock
              </button>
              <button disabled={saving} onClick={() => saveProduct(true)} type="button" className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-semibold text-white hover:bg-nexus-panel">
                <Plus className="h-4 w-4" />
                Save & Add Another
              </button>
              <button disabled={saving} onClick={() => saveProduct(false)} type="button" className="inline-flex h-10 items-center gap-2 rounded-md bg-nexus-orange px-4 text-sm font-semibold text-black">
                <Save className="h-4 w-4" />
                Save Product
              </button>
            </div>
          </div>
        </div>

        <AddProductPreview
          form={form}
          selectedCategory={selectedCategory}
          selectedBrand={selectedBrand}
          skuPreview={skuPreview}
          requiredDone={requiredDone}
          requiredTotal={requiredTotal}
          requiredProgress={requiredProgress}
        />
      </div>
    </Shell>
  );
}

function StockEntryPage({ data, mode = "add-unit" }) {
  const isReceiving = mode === "receive";
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    supplier: "",
    entryDate: today,
    deliveryNote: "",
    referenceNumber: "",
    notes: ""
  });
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [refsLoading, setRefsLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [lines, setLines] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const serialBatch = useMemo(() => String(Date.now()).slice(-6), []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadData() {
      setRefsLoading(true);
      const requests = [fetch(data.api.products, { signal: controller.signal })];
      if (isReceiving) {
        requests.push(fetch(data.api.suppliers, { signal: controller.signal }));
      }
      const [productsResponse, suppliersResponse] = await Promise.all(requests);
      setProducts(productsResponse.ok ? await productsResponse.json() : []);
      setSuppliers(suppliersResponse?.ok ? await suppliersResponse.json() : []);
      setRefsLoading(false);
    }

    loadData().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError(`Could not load ${isReceiving ? "receiving" : "stock unit"} data.`);
        setRefsLoading(false);
      }
    });

    return () => controller.abort();
  }, [data.api.products, data.api.suppliers, isReceiving]);

  const filteredProducts = products
    .filter((product) => {
      const text = `${product.display_name} ${product.sku} ${product.barcode || ""}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 6);
  const selectedSupplier = suppliers.find((supplier) => String(supplier.id) === String(form.supplier));
  const handledByName = data.user?.displayName || data.user?.username || "-";
  const totalUnits = lines.reduce((total, line) => total + Math.max(Number(line.quantity) || 0, 0), 0);
  const totalCost = lines.reduce(
    (total, line) => total + (Number(line.quantity) || 0) * (Number(line.cost) || 0),
    0
  );

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addSupplierItem(item) {
    setSuppliers((current) =>
      [...current, item].sort((left, right) =>
        String(left.name || "").localeCompare(String(right.name || ""))
      )
    );
  }

  async function createSupplierOption(name) {
    const trimmedName = name.trim();

    if (!trimmedName) {
      throw new Error("Enter a supplier name before creating it.");
    }

    setError("");
    const response = await fetch(data.api.suppliers, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": data.csrfToken
      },
      body: JSON.stringify({ name: trimmedName })
    });

    if (!response.ok) {
      const details = await response.json().catch(() => ({}));
      throw new Error(firstApiError(details) || "Could not create supplier.");
    }

    const created = await response.json();
    addSupplierItem(created);
    updateField("supplier", String(created.id));
    return created;
  }

  function addProductLine(product) {
    setLines((current) => [
      ...current,
      {
        key: `${product.id}-${Date.now()}`,
        product,
        quantity: 1,
        serials: "",
        cost: "0.00"
      }
    ]);
    setQuery("");
  }

  function updateLine(key, field, value) {
    setLines((current) =>
      current.map((line) => (line.key === key ? { ...line, [field]: value } : line))
    );
  }

  function removeLine(key) {
    setLines((current) => current.filter((line) => line.key !== key));
  }

  function parseSerials(value) {
    return value
      .split(/\r?\n|,/)
      .map((serial) => serial.trim())
      .filter(Boolean);
  }

  function buildGeneratedSerial(line, lineIndex, serialIndex) {
    const lineToken = String(lineIndex + 1).padStart(2, "0");
    const serialToken = String(serialIndex + 1).padStart(3, "0");
    return `${line.product.sku}-${serialBatch}-${lineToken}-${serialToken}`;
  }

  function buildReceivingSerialNumbers(line, lineIndex) {
    const quantity = Number(line.quantity) || 0;
    const serialNumbers = parseSerials(line.serials);

    if (serialNumbers.length > quantity) {
      throw new Error(`Serial number count cannot exceed quantity for ${line.product.display_name}.`);
    }

    for (let index = serialNumbers.length; index < quantity; index += 1) {
      serialNumbers.push(buildGeneratedSerial(line, lineIndex, index));
    }

    return serialNumbers;
  }

  function buildReceivingNotes() {
    return [
      form.deliveryNote ? `Delivery note: ${form.deliveryNote}` : "",
      form.notes
    ]
      .filter(Boolean)
      .join(" | ");
  }

  async function createReceivingRecord() {
    const itemInputs = lines.map((line, lineIndex) => {
      const quantity = Number(line.quantity) || 0;

      if (quantity < 1) {
        throw new Error(`Quantity must be at least 1 for ${line.product.display_name}.`);
      }

      return {
        product: line.product.id,
        quantity,
        serial_numbers: buildReceivingSerialNumbers(line, lineIndex),
        cost: line.cost || "0.00"
      };
    });

    const response = await fetch(data.api.receivingRecords, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": data.csrfToken
      },
      body: JSON.stringify({
        supplier: form.supplier,
        received_date: form.entryDate,
        reference_number: form.referenceNumber || form.deliveryNote,
        notes: buildReceivingNotes(),
        item_inputs: itemInputs
      })
    });

    if (!response.ok) {
      const details = await response.json().catch(() => ({}));
      throw new Error(firstApiError(details) || "Could not create receiving record.");
    }

    const created = await response.json();
    window.location.assign(created.id ? `/operations/receiving/${created.id}/` : data.routes.receivingRecords);
  }

  async function createProductUnits() {
    for (const line of lines) {
      const quantity = Number(line.quantity) || 0;
      const serials = parseSerials(line.serials);

      for (let index = 0; index < quantity; index += 1) {
        const serialNumber =
          serials[index] || `${line.product.sku}-${serialBatch}-${String(index + 1).padStart(3, "0")}`;
        const response = await fetch(data.api.productUnits, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": data.csrfToken
          },
          body: JSON.stringify({
            product: line.product.id,
            serial_number: serialNumber,
            status: "available",
            supplier: null,
            cost: line.cost || "0.00",
            purchase_date: form.entryDate,
            notes: form.notes
          })
        });

        if (!response.ok) {
          const details = await response.json().catch(() => ({}));
          throw new Error(firstApiError(details) || "Could not create stock unit.");
        }
      }
    }

    window.location.assign(data.routes.inventory);
  }

  async function saveStockUnits() {
    setSaving(true);
    setError("");
    try {
      if (!form.entryDate || !lines.length) {
        throw new Error("Entry date and at least one product are required.");
      }
      if (isReceiving && !form.supplier) {
        throw new Error("Supplier is required when receiving stock.");
      }

      if (isReceiving) {
        await createReceivingRecord();
      } else {
        await createProductUnits();
      }
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">{isReceiving ? "Receive Stock" : "Add Unit"}</h1>
              <p className="bim-page-description">
                {isReceiving
                  ? "Record supplier stock received with reference details."
                  : "Add physical inventory units without supplier or receipt details."}
              </p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/inventory/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled type="button" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-500">
                <Save className="h-4 w-4" />
                Save Draft
              </button>
              <button disabled={saving} onClick={saveStockUnits} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Save className="h-4 w-4" />
                {isReceiving ? "Receive Stock" : "Add Units"}
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection
            icon="clipboard"
            title={isReceiving ? "Receiving Information" : "Unit Entry"}
            subtitle={isReceiving ? "Supplier and reference details for this stock receipt." : "Minimal details for manual stock-unit entry."}
          >
            <div className="mb-5 flex items-center justify-between rounded-lg border border-nexus-line bg-nexus-panel2 p-4">
              <div>
                <p className="text-xs text-zinc-500">{isReceiving ? "Receiving Reference" : "Entry Reference"} (auto-generated)</p>
                <p className="mt-1 text-sm font-semibold text-zinc-500">Not created yet</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              {isReceiving ? (
                <SearchableCreatableSelect
                  label="Supplier"
                  required
                  value={form.supplier}
                  onChange={(value) => updateField("supplier", value)}
                  options={suppliers}
                  getOptionLabel={(item) => item.name}
                  onCreate={createSupplierOption}
                  placeholder="Search or create supplier..."
                  loading={refsLoading}
                />
              ) : null}
              <Field label={isReceiving ? "Receiving Date" : "Entry Date"} required>
                <TextInput type="date" value={form.entryDate} onChange={(value) => updateField("entryDate", value)} />
              </Field>
              {isReceiving ? (
                <>
                  <Field label="Delivery Note Number">
                    <TextInput value={form.deliveryNote} onChange={(value) => updateField("deliveryNote", value)} placeholder="Enter delivery note number" />
                  </Field>
                  <Field label="Reference Number">
                    <TextInput value={form.referenceNumber} onChange={(value) => updateField("referenceNumber", value)} placeholder="Enter supplier reference" />
                  </Field>
                </>
              ) : null}
            </div>
            <div className="mt-5">
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Condition notes, discrepancies, special instructions..." />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Products" subtitle="Search or scan a product, then add physical units.">
            <div className="relative">
              <div className="flex gap-3">
                <SearchBar
                  className="flex-1"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search product by name, SKU, or barcode..."
                />
                <button
                  type="button"
                  disabled
                  title="Barcode scanning coming later"
                  className="inline-flex h-10 cursor-not-allowed items-center gap-2 rounded-md px-3 text-sm font-semibold text-zinc-500"
                >
                  <RefreshCw className="h-4 w-4" />
                  Scan
                </button>
              </div>
              {filteredProducts.length ? (
                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
                  {filteredProducts.map((product) => (
                    <button
                      key={product.id}
                      onClick={() => addProductLine(product)}
                      type="button"
                      className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                    >
                      <span>
                        <span className="block text-sm font-bold text-white">{product.display_name}</span>
                        <span className="font-mono text-xs text-nexus-orange">{product.sku}</span>
                      </span>
                      <Plus className="h-4 w-4 text-zinc-500" />
                    </button>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="mt-4 rounded-lg border border-dashed border-nexus-line bg-black/30">
              {lines.length ? (
                lines.map((line) => (
                  <div key={line.key} className="grid gap-3 border-b border-nexus-line p-4 last:border-b-0 lg:grid-cols-[minmax(0,1fr)_110px_130px_minmax(0,1fr)_40px]">
                    <div>
                      <p className="font-bold text-white">{line.product.display_name}</p>
                      <p className="mt-1 font-mono text-xs text-nexus-orange">{line.product.sku}</p>
                    </div>
                    <CompactField label="Quantity">
                      <TextInput value={line.quantity} onChange={(value) => updateLine(line.key, "quantity", value)} />
                    </CompactField>
                    <CompactField label="Unit Cost">
                      <TextInput value={line.cost} onChange={(value) => updateLine(line.key, "cost", value)} />
                    </CompactField>
                    <CompactField label="Serial Numbers">
                      <textarea
                        value={line.serials}
                        onChange={(event) => updateLine(line.key, "serials", event.target.value)}
                        className="min-h-10 rounded-md border border-nexus-line bg-black px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
                        placeholder="One per line. Blank = auto-generated"
                      />
                    </CompactField>
                    <button onClick={() => removeLine(line.key)} type="button" className="mt-5 text-zinc-500 hover:text-nexus-red" aria-label={`Remove ${line.product.display_name}`}>
                      <X className="h-4 w-4" aria-hidden="true" />
                    </button>
                  </div>
                ))
              ) : (
                <div className="grid min-h-36 place-items-center text-center text-sm text-zinc-600">
                  <span>
                    <Package className="mx-auto mb-3 h-8 w-8" />
                    No products added yet
                    <br />
                    Search above or scan a barcode to add items
                  </span>
                </div>
              )}
            </div>
          </FormSection>

          {isReceiving ? (
            <FormSection icon="clipboard" title="Attachments" subtitle="Upload delivery notes or supporting documents.">
              <div className="grid min-h-28 place-items-center rounded-lg border border-dashed border-nexus-line bg-black/30 text-center text-sm text-zinc-600">
                Drop files here or click to upload
                <br />
                PDF, PNG, JPG, XLSX - max 20MB
              </div>
            </FormSection>
          ) : null}
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <div className="flex items-center justify-between border-b border-nexus-line px-4 py-4">
              <h2 className="bim-section-title">{isReceiving ? "Receiving Summary" : "Unit Summary"}</h2>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value="Not created yet" />
              {isReceiving ? <DetailRow label="Supplier" value={selectedSupplier?.name || "-"} /> : null}
              <DetailRow label="Date" value={form.entryDate || "-"} />
              <DetailRow label={isReceiving ? "Received By" : "Added By"} value={handledByName} />
              <DetailRow label="Products" value={lines.length} strong />
              <DetailRow label="Total Units" value={totalUnits} strong />
              {isReceiving ? <DetailRow label="Attachments" value="0" /> : null}
              <DetailRow label="Total Cost" value={totalCost ? `$${totalCost.toFixed(2)}` : "-"} />
            </dl>
          </section>

          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Quick Actions" />
            <div className="space-y-2 p-3">
              {["Save Draft", "Upload Attachment", "Scan Barcode"].map((label) => (
                <button key={label} disabled className="flex w-full items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-semibold text-zinc-500">
                  <Save className="h-4 w-4" />
                  {label}
                </button>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function CreateDeliveryPage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    client: "",
    customerName: "",
    receiverName: "",
    deliveryDate: today,
    notes: ""
  });
  const [units, setUnits] = useState([]);
  const [clients, setClients] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadUnits() {
      const [response, clientsResponse] = await Promise.all([
        fetch(`${data.api.productUnits}?status=available`, { signal: controller.signal }),
        fetch(data.api.clients, { signal: controller.signal })
      ]);
      setUnits(response.ok ? await response.json() : []);
      setClients(clientsResponse.ok ? await clientsResponse.json() : []);
    }

    loadUnits().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load available stock units.");
      }
    });

    return () => controller.abort();
  }, [data.api.clients, data.api.productUnits]);

  const selectedIds = new Set(selectedUnits.map((unit) => unit.id));
  const filteredUnits = units
    .filter((unit) => !selectedIds.has(unit.id))
    .filter((unit) => {
      const text = `${unit.product_name} ${unit.product_sku} ${unit.product_barcode || ""} ${unit.serial_number}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 8);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function addClientItem(item) {
    setClients((current) =>
      current.some((client) => client.id === item.id)
        ? current
        : [...current, item].sort((a, b) => a.name.localeCompare(b.name))
    );
  }

  async function createClientOption(name) {
    if (!name.trim()) {
      throw new Error("Enter a client name before creating it.");
    }
    const response = await fetch(data.api.clients, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": data.csrfToken
      },
      body: JSON.stringify({ name: name.trim() })
    });
    if (!response.ok) {
      const details = await response.json().catch(() => ({}));
      throw new Error(firstApiError(details) || "Could not create client.");
    }
    const created = await response.json();
    addClientItem(created);
    updateField("client", String(created.id));
    updateField("customerName", created.name);
    return created;
  }

  function addUnit(unit) {
    setSelectedUnits((current) => [...current, unit]);
    setQuery("");
  }

  function removeUnit(unitId) {
    setSelectedUnits((current) => current.filter((unit) => unit.id !== unitId));
  }

  async function completeDelivery() {
    setSaving(true);
    setError("");
    try {
      const selectedClient = clients.find((client) => String(client.id) === String(form.client));
      if (!selectedClient || !selectedUnits.length) {
        throw new Error("Client and at least one stock unit are required.");
      }

      const response = await fetch(data.api.deliveries, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          client: selectedClient.id,
          customer_name: selectedClient.name,
          receiver_name: form.receiverName,
          delivery_date: form.deliveryDate,
          notes: form.notes,
          unit_ids: selectedUnits.map((unit) => unit.id)
        })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not complete delivery.");
      }

      const created = await response.json();
      window.location.assign(created.id ? `/operations/deliveries/${created.id}/` : data.routes.deliveryRecords);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="bim-page-title">Create Delivery</h1>
              <p className="bim-page-description">Record outgoing stock and update unit status.</p>
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              <a href="/inventory/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
                <X className="h-4 w-4" />
                Cancel
              </a>
              <button disabled type="button" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-500">
                <Save className="h-4 w-4" />
                Save Draft
              </button>
              <button disabled={saving} onClick={completeDelivery} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Icon name={workflowMeta.create_delivery.icon} className="h-4 w-4" />
                Complete Delivery
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="delivery" title="Delivery Information" subtitle="Internal stock exit details for this dispatch.">
            <div className="mb-5 flex items-center justify-between rounded-lg border border-nexus-line bg-nexus-panel2 p-4">
              <div>
                <p className="text-xs text-zinc-500">Delivery Reference (auto-generated)</p>
                <p className="mt-1 text-sm font-semibold text-zinc-500">Not created yet</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <SearchableCreatableSelect
                label="Client"
                required
                value={form.client}
                onChange={(value) => {
                  const selected = clients.find((client) => String(client.id) === String(value));
                  updateField("client", value);
                  updateField("customerName", selected?.name || "");
                }}
                options={clients}
                onCreate={createClientOption}
                placeholder="Search or create client..."
                helperText="Delivery links to Client master data; no invoice or accounting record is created."
              />
              <Field label="Delivery Date" required>
                <TextInput value={form.deliveryDate} onChange={(value) => updateField("deliveryDate", value)} />
              </Field>
              <Field label="Receiver Name">
                <TextInput value={form.receiverName} onChange={(value) => updateField("receiverName", value)} placeholder="Enter receiver name" />
              </Field>
            </div>
            <div className="mt-5">
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Delivery notes or handover instructions..." />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Stock Units" subtitle="Search available stock units and add them to this delivery.">
            <div className="relative">
              <SearchBar
                className="flex-1"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search available unit by product, SKU, barcode, or serial..."
              />
              {filteredUnits.length ? (
                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
                  {filteredUnits.map((unit) => (
                    <button
                      key={unit.id}
                      onClick={() => addUnit(unit)}
                      type="button"
                      className="flex w-full items-center justify-between border-b border-nexus-line px-4 py-3 text-left last:border-b-0 hover:bg-nexus-panel2"
                    >
                      <span>
                        <span className="block text-sm font-bold text-white">{unit.product_name}</span>
                        <span className="font-mono text-xs text-nexus-orange">{unit.product_sku} / {unit.serial_number}</span>
                      </span>
                      <Plus className="h-4 w-4 text-zinc-500" />
                    </button>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="mt-4 rounded-lg border border-dashed border-nexus-line bg-black/30">
              {selectedUnits.length ? (
                selectedUnits.map((unit) => (
                  <div key={unit.id} className="grid gap-3 border-b border-nexus-line p-4 last:border-b-0 md:grid-cols-[minmax(0,1fr)_180px_40px]">
                    <div>
                      <p className="font-bold text-white">{unit.product_name}</p>
                      <p className="mt-1 font-mono text-xs text-nexus-orange">{unit.product_sku}</p>
                    </div>
                    <p className="font-mono text-sm text-zinc-300">{unit.serial_number}</p>
                    <button onClick={() => removeUnit(unit.id)} type="button" className="text-zinc-500 hover:text-nexus-red">
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))
              ) : (
                <div className="grid min-h-36 place-items-center text-center text-sm text-zinc-600">
                  <span>
                    <Package className="mx-auto mb-3 h-8 w-8" />
                    No stock units selected yet
                    <br />
                    Search above to add available units
                  </span>
                </div>
              )}
            </div>
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <div className="flex items-center justify-between border-b border-nexus-line px-4 py-4">
              <h2 className="bim-section-title">Delivery Summary</h2>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value="Not created yet" />
              <DetailRow label="Client" value={clients.find((client) => String(client.id) === String(form.client))?.name || "-"} />
              <DetailRow label="Receiver" value={form.receiverName || "-"} />
              <DetailRow label="Date" value={form.deliveryDate || "-"} />
              <DetailRow label="Units" value={selectedUnits.length} strong />
            </dl>
          </section>

          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <PanelHeader title="Quick Actions" />
            <div className="space-y-2 p-3">
              {["Save Draft", "Scan Barcode"].map((label) => (
                <button key={label} disabled className="flex w-full items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-semibold text-zinc-500">
                  <Save className="h-4 w-4" />
                  {label}
                </button>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </Shell>
  );
}

function AddProductHeader({ saving, onReset, onSave, onSaveAnother }) {
  return (
    <header className="mb-5 border-b border-nexus-line pb-4">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 className="bim-page-title">Add Product</h1>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <Button onClick={onReset} type="button" variant="secondary">
          <RotateCcw className="h-4 w-4" />
          Reset
        </Button>
        <Button disabled={saving} onClick={onSaveAnother} type="button" variant="secondary">
          <Plus className="h-4 w-4" />
          Save & Add Another
        </Button>
        <Button disabled={saving} onClick={onSave} type="button" variant="primary">
          <Save className="h-4 w-4" />
          Save Product
        </Button>
      </div>
      </div>
    </header>
  );
}

function FormSection({ icon, title, subtitle, children }) {
  return (
    <Card className="mb-5 p-5">
      <CardHeader className="flex items-start gap-3 px-0 py-0 pb-5">
        <span className="rounded-lg bg-nexus-orange/10 p-2 text-nexus-orange">
          <Icon name={icon} className="h-5 w-5" />
        </span>
        <div>
          <CardTitle className="normal-case tracking-normal text-white">{title}</CardTitle>
          <CardDescription>{subtitle}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="pt-5">{children}</CardContent>
    </Card>
  );
}

function Field({ label, required = false, children }) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-white">
        {label}
        {required ? <span className="text-nexus-orange">*</span> : null}
      </span>
      <span className="mt-2 block">{children}</span>
    </label>
  );
}

function TextInput({ value, onChange, placeholder, disabled = false, type = "text" }) {
  return (
    <Input
      type={type}
      disabled={disabled}
      value={value}
      onChange={(event) => onChange?.(event.target.value)}
      placeholder={placeholder}
      className=""
    />
  );
}

function CompactField({ label, children }) {
  return (
    <label className="grid gap-1.5 text-xs font-semibold text-zinc-500">
      <span>{label}</span>
      {children}
    </label>
  );
}

function SelectInput({ value, onChange, options, placeholder, disabled = false }) {
  return (
    <select
      disabled={disabled}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="h-10 w-full rounded-md border border-nexus-line bg-black px-3 text-sm text-zinc-200 outline-none disabled:bg-zinc-800/80 disabled:text-zinc-500"
    >
      <option value="">{placeholder}</option>
      {options.map(([optionValue, optionLabel]) => (
        <option key={optionValue} value={optionValue}>
          {optionLabel}
        </option>
      ))}
    </select>
  );
}

function SearchableCreatableSelect({
  label,
  required = false,
  value,
  onChange,
  options,
  getOptionLabel = (option) => option.name,
  getOptionValue = (option) => option.id,
  onCreate,
  placeholder,
  helperText,
  loading = false,
  disabled = false
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const selected = options.find((option) => String(getOptionValue(option)) === String(value));
  const trimmedQuery = query.trim();
  const normalizedQuery = trimmedQuery.toLowerCase();
  const filteredOptions = normalizedQuery
    ? options.filter((option) => getOptionLabel(option).toLowerCase().includes(normalizedQuery))
    : options;
  const visibleOptions = filteredOptions.slice(0, 8);
  const hasExactMatch = options.some((option) => getOptionLabel(option).trim().toLowerCase() === normalizedQuery);
  const canCreate = Boolean(onCreate && trimmedQuery && !hasExactMatch && !creating && !disabled);

  function selectOption(option) {
    onChange(String(getOptionValue(option)));
    setQuery("");
    setOpen(false);
    setCreateError("");
  }

  async function createOption() {
    if (!canCreate) return;

    setCreating(true);
    setCreateError("");
    try {
      const created = await onCreate(trimmedQuery);
      selectOption(created);
    } catch (error) {
      setCreateError(error.message || "Could not create lookup value.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="relative">
      <label className="block">
        <span className="text-sm font-semibold text-white">
          {label}
          {required ? <span className="text-nexus-orange">*</span> : null}
        </span>
        <span className="relative mt-2 block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-600" />
          <input
            disabled={disabled}
            value={open ? query : selected ? getOptionLabel(selected) : ""}
            onFocus={() => {
              if (disabled) return;
              setOpen(true);
              setQuery("");
            }}
            onChange={(event) => {
              setQuery(event.target.value);
              setOpen(true);
              setCreateError("");
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && canCreate) {
                event.preventDefault();
                createOption();
              }
              if (event.key === "Escape") {
                setOpen(false);
                setQuery("");
              }
            }}
            onBlur={() => window.setTimeout(() => setOpen(false), 150)}
            placeholder={loading ? "Loading..." : placeholder}
            className="h-10 w-full rounded-md border border-nexus-line bg-black py-2 pl-9 pr-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 disabled:bg-zinc-800/80 disabled:text-zinc-500"
          />
        </span>
      </label>
      {helperText ? <p className="mt-2 text-xs text-zinc-500">{helperText}</p> : null}
      {createError ? <p className="mt-2 text-xs font-semibold text-red-300">{createError}</p> : null}
      {open && !disabled ? (
        <div className="absolute z-30 mt-2 max-h-72 w-full overflow-auto rounded-md border border-nexus-line bg-zinc-950 p-1 shadow-2xl shadow-black/50">
          {loading ? <div className="px-3 py-2 text-sm text-zinc-500">Loading...</div> : null}
          {!loading && visibleOptions.length ? (
            visibleOptions.map((option) => (
              <button
                key={getOptionValue(option)}
                type="button"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => selectOption(option)}
                className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-sm text-zinc-200 hover:bg-nexus-panel"
              >
                <span className="min-w-0 truncate">{getOptionLabel(option)}</span>
                {String(getOptionValue(option)) === String(value) ? <span className="text-xs text-nexus-orange">Selected</span> : null}
              </button>
            ))
          ) : null}
          {!loading && !visibleOptions.length ? (
            <div className="px-3 py-2 text-sm text-zinc-500">No matches found.</div>
          ) : null}
          {!loading && canCreate ? (
            <button
              type="button"
              disabled={creating}
              onMouseDown={(event) => event.preventDefault()}
              onClick={createOption}
              className="mt-1 flex w-full items-center gap-2 rounded border border-dashed border-nexus-line px-3 py-2 text-left text-sm font-semibold text-nexus-orange hover:border-nexus-orange hover:bg-nexus-panel disabled:text-zinc-600"
            >
              <Plus className="h-4 w-4" />
              {creating ? "Creating..." : `Create "${trimmedQuery}"`}
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function AddProductPreview({
  form,
  selectedCategory,
  selectedBrand,
  skuPreview,
  requiredDone,
  requiredTotal,
  requiredProgress
}) {
  const missing = [
    ["Product Name", form.descript],
    ["Category", selectedCategory?.name],
    ["Brand", selectedBrand?.brandname],
    ["Model", form.modelName]
  ];
  const optionalFields = [
    ["Barcode", form.barcode],
    ["Low Stock Alert", form.reorderStockLevel],
    ["Internal Notes", form.notes],
    ["Product Image", form.imageFile]
  ];

  return (
    <aside className="space-y-4 xl:sticky xl:top-5 xl:h-fit">
      <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="border-b border-nexus-line px-4 py-4">
        <h2 className="bim-section-title">Live Preview</h2>
      </div>
      <div className="space-y-5 p-4">
        <div className="flex gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-zinc-800 text-zinc-500">
            <Package className="h-5 w-5" />
          </span>
          <div>
            <h3 className="font-bold italic text-zinc-400">{form.descript || "Product Name"}</h3>
            <p className="text-sm text-zinc-500">-</p>
          </div>
        </div>

        <div className="rounded-lg border border-nexus-line bg-nexus-panel2 p-3">
          <p className="text-xs font-semibold text-zinc-400">SKU</p>
          <p className="mt-2 text-sm italic text-zinc-500">
            {skuPreview === "auto-generate" ? "Full Category, Brand & Model" : skuPreview}
          </p>
        </div>

        <dl className="space-y-3 text-sm">
          <DetailRow label="Category" value={selectedCategory?.name || "-"} />
          <DetailRow label="Brand" value={selectedBrand?.brandname || "-"} />
          <DetailRow label="Model" value={form.modelName || "-"} />
          <DetailRow label="Tracking Method" value="Serial Number Tracking" strong />
          <DetailRow label="Status" value={form.isactive ? "Active" : "Inactive"} highlight={form.isactive} />
        </dl>

        <div className="border-t border-nexus-line pt-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-400">Required fields</span>
            <span className="font-bold text-nexus-orange">{requiredProgress}%</span>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-zinc-800">
            <div className="h-1.5 rounded-full bg-nexus-orange" style={{ width: `${requiredProgress}%` }} />
          </div>
          <p className="mt-2 text-xs text-zinc-500">{requiredTotal - requiredDone} required fields remaining</p>
        </div>

        <div className="space-y-2 border-t border-nexus-line pt-4">
          <h3 className="bim-label">Required</h3>
          {missing.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "âœ“" : "â—‹"} {label}
            </p>
          ))}
        </div>
        <div className="space-y-2 border-t border-nexus-line pt-4">
          <h3 className="bim-label">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "âœ“" : "â—‹"} {label}
            </p>
          ))}
        </div>
      </div>
      </section>

      <section className="rounded-lg border border-nexus-line bg-nexus-panel p-4">
        <h2 className="bim-section-title">Product Lifecycle</h2>
        <div className="mt-4 space-y-4 text-sm">
          <LifecycleStep number="1" title="Product Created" detail="You are here" active />
          <LifecycleStep number="2" title="Stock Received or Added" detail="Via receiving record or adjustment" />
          <LifecycleStep number="3" title="Stock Units Available" detail="Units become searchable inventory" />
        </div>
      </section>
    </aside>
  );
}

function LifecycleStep({ number, title, detail, active = false }) {
  return (
    <div className="flex gap-3">
      <span
        className={`grid h-6 w-6 shrink-0 place-items-center rounded-full text-xs font-bold ${
          active ? "bg-nexus-orange text-black" : "bg-zinc-800 text-zinc-400"
        }`}
      >
        {number}
      </span>
      <span>
        <span className={`block font-bold ${active ? "text-nexus-orange" : "text-white"}`}>{title}</span>
        <span className="mt-1 block text-xs text-zinc-500">{detail}</span>
      </span>
    </div>
  );
}

function firstApiError(details) {
  if (typeof details === "string") {
    return details;
  }
  if (Array.isArray(details)) {
    return details[0] || "";
  }
  if (!details || typeof details !== "object") {
    return "";
  }
  const firstValue = Object.values(details)[0];
  if (Array.isArray(firstValue)) {
    return firstValue[0];
  }
  if (typeof firstValue === "string") {
    return firstValue;
  }
  return "";
}

function DetailRow({ label, value, highlight = false, strong = false }) {
  return (
    <div className="mt-3 flex items-center justify-between gap-3 text-sm">
      <dt className="text-zinc-500">{label}</dt>
      <dd className={`${highlight ? "text-nexus-green" : strong ? "text-white" : "text-zinc-300"} font-semibold`}>
        {value}
      </dd>
    </div>
  );
}

function QuickAddMenu({ actions }) {
  const quickActionLabels = new Set(["Add Product", "Add Unit", "Receive Stock", "Create Delivery"]);
  const visibleActions = actions.filter(
    (action) => quickActionLabels.has(action.label) && action.enabled && action.href
  );

  if (!visibleActions.length) return null;

  return (
    <details className="relative">
      <summary className="inline-flex h-9 cursor-pointer list-none items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black marker:hidden">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Quick Add
      </summary>
      <div className="absolute right-0 z-20 mt-2 w-64 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
        {visibleActions.map((action) => (
          <a key={action.label} href={action.href} className="flex items-start gap-3 border-b border-nexus-line px-3 py-3 last:border-b-0 hover:bg-nexus-panel2">
            <ActionIcon name={action.icon} tone={action.tone} />
            <span>
              <span className="block text-sm font-semibold text-white">{action.label}</span>
              <span className="block text-xs text-zinc-500">{action.description}</span>
            </span>
          </a>
        ))}
      </div>
    </details>
  );
}

function KpiGrid({ items }) {
  return (
    <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4" aria-label="Key metrics">
      {items.map((item) => {
        const isWarning = item.tone === "warning";
        const isDanger = item.tone === "danger";
        const className = `group block min-h-32 rounded-lg border bg-nexus-panel p-4 shadow-panel ${
            isDanger
              ? "border-nexus-red/70"
              : isWarning
                ? "border-nexus-orange/70"
                : "border-nexus-line"
          } ${item.href ? "cursor-pointer hover:border-nexus-orange/70 hover:bg-nexus-orange/5 focus:outline-none focus:ring-2 focus:ring-nexus-orange/40" : ""}`;
        const content = (
          <>
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm font-medium text-zinc-400">{item.label}</p>
              <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
                <Icon name={item.icon} />
              </span>
            </div>
            <p
              className={`mt-6 text-3xl font-semibold tracking-tight ${
                isDanger
                  ? "text-nexus-red"
                  : isWarning
                    ? "text-nexus-orange"
                    : "text-white group-hover:text-nexus-orange"
              }`}
            >
              {item.value}
            </p>
            <div className="mt-1 flex items-center justify-between gap-3 text-sm text-zinc-400">
              <span>{item.detail}</span>
              {item.href ? <ChevronRight className="h-4 w-4 shrink-0 text-zinc-600 group-hover:text-nexus-orange" /> : null}
            </div>
            {item.trend ? (
              <p className={`mt-2 text-xs font-semibold ${item.tone === "stock" ? "text-nexus-red" : "text-nexus-green"}`}>
                {item.trend}
              </p>
            ) : null}
          </>
        );

        return item.href ? (
          <a key={item.label} href={item.href} className={className} title={item.todo || undefined}>
            {content}
          </a>
        ) : (
          <article key={item.label} className={className}>
            {content}
          </article>
        );
      })}
    </section>
  );
}

function Overview({ items }) {
  return (
    <section className="mt-5" aria-label="System overview">
      <SectionTitle title="System Overview" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        {items.map((item) => {
          const isEnabled = item.enabled !== false && item.href;
          const className = `group flex items-center gap-3 rounded-lg border border-nexus-line bg-nexus-panel p-4 ${
            isEnabled ? "cursor-pointer hover:border-nexus-orange/70 hover:bg-nexus-orange/5 focus:outline-none focus:ring-2 focus:ring-nexus-orange/40" : "cursor-not-allowed opacity-45 grayscale"
          }`;
          const content = (
            <>
              <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
                <Icon name={item.icon} />
              </span>
              <div className="min-w-0 flex-1">
                <p className={`text-sm font-bold ${isEnabled ? "text-white group-hover:text-nexus-orange" : "text-zinc-500"}`}>{item.value}</p>
                <p className={`text-xs ${isEnabled ? "text-zinc-400" : "text-zinc-500"}`}>{item.label}</p>
                <p className="text-xs text-zinc-500">{item.detail}</p>
              </div>
              {isEnabled ? <ChevronRight className="h-4 w-4 shrink-0 text-zinc-600 group-hover:text-nexus-orange" /> : null}
            </>
          );
          return isEnabled ? (
            <a key={item.label} href={item.href} className={className}>
              {content}
            </a>
          ) : (
            <article key={item.label} aria-disabled="true" className={className} title={item.detail || undefined}>
              {content}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function RecentActivity({ items }) {
  return (
    <section className="overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Activity" />
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-zinc-800/80 text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">Reference</th>
              <th className="px-4 py-3 font-medium">Activity</th>
              <th className="px-4 py-3 font-medium">Product / Record</th>
              <th className="px-4 py-3 font-medium">Performed by</th>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map((item) => {
                const rowClass = `border-t border-nexus-line ${item.href ? "cursor-pointer hover:bg-nexus-panel2" : "hover:bg-nexus-panel2/60"}`;
                const content = (
                  <>
                    <td className="px-4 py-4 font-mono text-xs text-nexus-orange">{item.reference || "-"}</td>
                    <td className="px-4 py-4 font-semibold text-white">{item.type || "-"}</td>
                    <td className="px-4 py-4 text-zinc-400">{item.related || "-"}</td>
                    <td className="px-4 py-4 text-zinc-400">{item.user || "-"}</td>
                    <td className="px-4 py-4 text-zinc-400">{item.date ? String(item.date) : "-"}</td>
                    <td className="px-4 py-4">
                      <span className="inline-flex items-center gap-2">
                        <Status status={item.status || "-"} statusClass={item.status_class} />
                        {item.href ? <ChevronRight className="h-4 w-4 text-zinc-600" /> : null}
                      </span>
                    </td>
                  </>
                );

                return (
                  <tr
                    key={`${item.reference}-${item.type}`}
                    className={rowClass}
                    onClick={() => {
                      if (item.href) window.location.assign(item.href);
                    }}
                    tabIndex={item.href ? 0 : undefined}
                    onKeyDown={(event) => {
                      if (item.href && (event.key === "Enter" || event.key === " ")) {
                        event.preventDefault();
                        window.location.assign(item.href);
                      }
                    }}
                  >
                    {content}
                  </tr>
                );
              })
            ) : (
              <tr className="border-t border-nexus-line">
                <td className="px-4 py-8 text-center text-sm text-zinc-500" colSpan="6">
                  No activity recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function RecentDeliveries({ items = [] }) {
  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Deliveries" action="View all" actionHref="/operations/deliveries/" />
      <RecordPanel
        items={items}
        emptyTitle="No delivery records yet."
        emptyDetail="Create your first delivery once stock is available."
      />
    </section>
  );
}

function RecentReceiving({ items = [] }) {
  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Receiving" action="View all" actionHref="/operations/receiving/" />
      <RecordPanel
        items={items}
        emptyTitle="No receiving records yet."
        emptyDetail="Receive stock to begin tracking inventory."
      />
    </section>
  );
}

function RecordPanel({ items = [], emptyTitle, emptyDetail }) {
  if (!items.length) {
    return <EmptyPanel title={emptyTitle} detail={emptyDetail} />;
  }

  return (
    <div className="border-t border-nexus-line">
      {items.map((item) => {
        const className = `flex items-start gap-3 border-b border-nexus-line px-4 py-3 last:border-b-0 ${
          item.href ? "hover:bg-nexus-panel2" : ""
        }`;
        const content = (
          <>
          <StatusIcon statusClass={item.status_class} />
          <span className="min-w-0 flex-1">
            <span className="block font-mono text-xs text-nexus-orange">{item.reference}</span>
            <span className="mt-1 block truncate text-sm font-semibold text-white">{item.title || "-"}</span>
            <span className="block truncate text-xs text-zinc-500">{item.detail || "-"}</span>
          </span>
          <span className="shrink-0 text-right text-xs text-zinc-500">{item.date ? String(item.date) : "-"}</span>
          </>
        );

        return item.href ? (
          <a key={item.reference} href={item.href} className={className}>
            {content}
          </a>
        ) : (
          <div key={item.reference} className={className} data-future-href={item.futureHref || undefined}>
            {content}
          </div>
        );
      })}
    </div>
  );
}

function EmptyPanel({ title, detail }) {
  return <EmptyState className="border-t border-nexus-line" title={title} description={detail} />;
}

function StatusIcon({ statusClass }) {
  const meta = statusMeta[statusClass] || statusMeta.available;

  return (
    <span className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-md ${meta.className}`}>
      <Icon name={meta.icon} className="h-4 w-4" />
    </span>
  );
}

function Status({ status, statusClass }) {
  return <Badge status={statusClass}>{status}</Badge>;
}

function PanelHeader({ title, action, actionHref, badge }) {
  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3">
      <h2 className="bim-section-title">{title}</h2>
      {badge ? <Badge className="rounded-full bg-nexus-orange px-2 py-1 font-bold text-white">{badge}</Badge> : null}
      {action && actionHref ? (
        <a className="inline-flex items-center gap-1 text-xs font-semibold text-nexus-orange hover:text-orange-300" href={actionHref}>
          {action}
          <ChevronRight className="h-4 w-4" />
        </a>
      ) : action ? (
        <button className="text-xs font-semibold text-nexus-orange">{action}</button>
      ) : null}
    </div>
  );
}

function SectionTitle({ title }) {
  return <h2 className="mb-3 bim-section-title">{title}</h2>;
}

function ActionIcon({ name, tone = "neutral" }) {
  return (
    <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${toneClasses[tone] || toneClasses.neutral}`}>
      <Icon name={name} className="h-5 w-5" />
    </span>
  );
}

function LogoutForm({ data }) {
  return (
    <form method="post" action={data.logoutHref}>
      <input type="hidden" name="csrfmiddlewaretoken" value={data.csrfToken} />
      <Button className="text-zinc-300" type="submit" variant="outline">
        Log out
      </Button>
    </form>
  );
}

const appRoutes = [
  {
    match: (path) => path.startsWith("/settings"),
    render: (data) => <SettingsPage data={data} />
  },
  {
    match: (path) => /^\/suppliers\/\d+\//.test(path),
    render: (data) => <MasterDataDetailPage data={data} type="suppliers" />
  },
  {
    match: (path) => path.startsWith("/suppliers/new"),
    render: (data) => <MasterDataDetailPage data={data} type="suppliers" isNew />
  },
  {
    match: (path) => path === "/suppliers/",
    render: (data) => <MasterDataListPage data={data} type="suppliers" />
  },
  {
    match: (path) => /^\/clients\/\d+\//.test(path),
    render: (data) => <MasterDataDetailPage data={data} type="clients" />
  },
  {
    match: (path) => path.startsWith("/clients/new"),
    render: (data) => <MasterDataDetailPage data={data} type="clients" isNew />
  },
  {
    match: (path) => path === "/clients/",
    render: (data) => <MasterDataListPage data={data} type="clients" />
  },
  {
    match: (path) => path.startsWith("/assets"),
    render: (data) => <PlaceholderPage data={data} title="Assets" />
  },
  {
    match: (path) => path.startsWith("/knowledge-base"),
    render: (data) => <PlaceholderPage data={data} title="Knowledge Base" />
  },
  {
    match: (path) => /^\/operations\/receiving\/\d+\//.test(path),
    render: (data) => <ReceivingRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/receiving/new"),
    render: (data) => <StockEntryPage data={data} mode="receive" />
  },
  {
    match: (path) => path === "/operations/receiving/",
    render: (data) => <ReceivingRecordsPage data={data} />
  },
  {
    match: (path) => /^\/operations\/deliveries\/\d+\//.test(path),
    render: (data) => <DeliveryRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/deliveries/new"),
    render: (data) => <CreateDeliveryPage data={data} />
  },
  {
    match: (path) => path === "/operations/deliveries/",
    render: (data) => <DeliveryRecordsPage data={data} />
  },
  {
    match: (path) => /^\/operations\/reservations\/\d+\//.test(path),
    render: (data) => <ReservationRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/reservations/new"),
    render: (data) => <CreateReservationPage data={data} />
  },
  {
    match: (path) => path === "/operations/reservations/",
    render: (data) => <ReservationRecordsPage data={data} />
  },
  {
    match: (path) => /^\/operations\/issues\/\d+\//.test(path),
    render: (data) => <IssueRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/issues/new"),
    render: (data) => <CreateIssuePage data={data} />
  },
  {
    match: (path) => path === "/operations/issues/",
    render: (data) => <IssueRecordsPage data={data} />
  },
  {
    match: (path) => /^\/operations\/repairs\/\d+\//.test(path),
    render: (data) => <RepairRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/repairs/new"),
    render: (data) => <CreateRepairPage data={data} />
  },
  {
    match: (path) => path === "/operations/repairs/",
    render: (data) => <RepairRecordsPage data={data} />
  },
  {
    match: (path) => /^\/operations\/client-returns\/\d+\//.test(path),
    render: (data) => <ClientReturnRecordDetailPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations/client-returns/new"),
    render: (data) => <CreateClientReturnPage data={data} />
  },
  {
    match: (path) => path === "/operations/client-returns/",
    render: (data) => <ClientReturnRecordsPage data={data} />
  },
  {
    match: (path) => path.startsWith("/operations"),
    render: (data) => <OperationsPage data={data} />
  },
  {
    match: (path) => path.startsWith("/inventory/products/new"),
    render: (data) => <AddProductPage data={data} />
  },
  {
    match: (path) => /^\/inventory\/products\/\d+\//.test(path),
    render: (data) => <ProductDetailsPage data={data} />
  },
  {
    match: (path) => path.startsWith("/inventory/stock-units/new"),
    render: (data) => <StockEntryPage data={data} mode="add-unit" />
  },
  {
    match: (path) => path.startsWith("/inventory"),
    render: (data) => <InventoryPage data={data} />
  }
];

export default function AppRouter({ initialData }) {
  if (!initialData) {
    return (
      <div className="grid min-h-screen place-items-center bg-nexus-page text-white">
        BIM Nexus could not load dashboard data.
      </div>
    );
  }

  if (initialData.page?.type === "login") {
    return <LoginPage data={initialData.page} />;
  }

  if (initialData.page?.type === "password_setup") {
    return <PasswordSetupPage data={initialData.page} />;
  }

  const currentPath = initialData.currentPath || window.location.pathname;
  const route = appRoutes.find((candidate) => candidate.match(currentPath));

  if (route) {
    return route.render(initialData);
  }

  return <CommandCenter data={initialData} />;
}
