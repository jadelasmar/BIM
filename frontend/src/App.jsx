import { useEffect, useMemo, useState } from "react";
import {
  ChevronRight,
  Download,
  Edit3,
  Eye,
  Filter,
  LayoutDashboard,
  MoreHorizontal,
  Package,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Settings,
  Truck,
  X
} from "lucide-react";

import logoPrimary from "./assets/brand/logo-primary.png";
import logoWhite from "./assets/brand/logo-white.png";
import { iconComponents, statusStyles, toneClasses } from "./uiRegistry";

function Icon({ name, className = "h-4 w-4" }) {
  const Component = iconComponents[name] || LayoutDashboard;
  return <Component className={className} aria-hidden="true" />;
}

function formatCount(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return typeof value === "number" ? value.toLocaleString() : value;
}

function Shell({ data, children }) {
  return (
    <div className="min-h-screen bg-nexus-page text-zinc-100 lg:grid lg:grid-cols-[248px_minmax(0,1fr)]">
      <aside className="border-b border-nexus-line bg-black/95 px-4 py-5 lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="px-2">
          <a href="/" className="inline-flex" aria-label="BIM Nexus Command Center">
            <img src={logoWhite} alt="BIM Nexus" className="bim-sidebar-logo bim-sidebar-logo-dark h-8 w-auto max-w-[196px]" />
            <img src={logoPrimary} alt="BIM Nexus" className="bim-sidebar-logo bim-sidebar-logo-light h-8 w-auto max-w-[196px]" />
          </a>
          <p className="mt-2 text-xs text-zinc-500">Internal IT Operations</p>
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
                className={`flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-semibold ${
                  item.active
                    ? "border border-nexus-line bg-nexus-panel text-white"
                    : "text-zinc-400 hover:bg-nexus-panel hover:text-white"
                }`}
              >
                <Icon
                  name={item.icon}
                  className={`h-4 w-4 ${item.active ? "text-nexus-orange" : "text-zinc-500"}`}
                />
                {item.name}
              </a>
            )
          )}
        </nav>

        <div className="my-5 h-px bg-nexus-line" />

        <nav className="space-y-2" aria-label="Settings navigation">
          {data.navigation.secondary.map((item) =>
            item.enabled && item.href ? (
              <a
                key={item.name}
                href={item.href}
                className={`flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-semibold ${
                  item.active
                    ? "border border-nexus-line bg-nexus-panel text-white"
                    : "text-zinc-300 hover:bg-nexus-panel"
                }`}
              >
                <Icon
                  name={item.icon}
                  className={`h-4 w-4 ${item.active ? "text-nexus-orange" : "text-zinc-500"}`}
                />
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

      <main className="min-w-0 px-4 py-5 sm:px-6 lg:px-7">{children}</main>
    </div>
  );
}

function CommandCenter({ data }) {
  return (
    <Shell data={data}>
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
    </Shell>
  );
}

function SettingsPage({ data }) {
  const storageKey = data.theme?.storageKey || "bim-nexus-theme";
  const [theme, setThemeState] = useState(() =>
    document.documentElement.dataset.theme === "light" ? "light" : "dark"
  );

  function setTheme(nextTheme) {
    const normalizedTheme = nextTheme === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = normalizedTheme;
    window.localStorage.setItem(storageKey, normalizedTheme);
    setThemeState(normalizedTheme);
  }

  return (
    <Shell data={data}>
      <header className="mb-5">
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="mt-1 text-sm text-zinc-400">Manage BIM Nexus display preferences.</p>
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

        {data.user?.isStaff ? (
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

function OperationsPage({ data }) {
  const workflows = [
    {
      title: "Receive Stock",
      detail: "Register incoming inventory units.",
      href: data.routes.receiveStock,
      enabled: data.quickActions.some((action) => action.label === "Receive Stock" && action.enabled),
      icon: "download",
      tone: "green"
    },
    {
      title: "Create Delivery",
      detail: "Dispatch available stock units.",
      href: data.routes.createDelivery,
      enabled: data.quickActions.some((action) => action.label === "Create Delivery" && action.enabled),
      icon: "delivery",
      tone: "orange"
    },
    {
      title: "Stock Movement",
      detail: "Manual adjustments and exceptions.",
      href: null,
      enabled: false,
      icon: "trending-up",
      tone: "neutral"
    }
  ];

  return (
    <Shell data={data}>
      <header className="mb-5">
        <h1 className="text-2xl font-bold text-white">Operations</h1>
        <p className="mt-1 text-sm text-zinc-400">Run stock entry and stock exit workflows.</p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {workflows.map((workflow) => {
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

function Header({ data }) {
  return (
    <header className="flex flex-col gap-4 pb-5 xl:flex-row xl:items-start xl:justify-between">
      <div className="min-w-0">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">
          <span className="h-2 w-2 rounded-full border border-nexus-blue" />
          {data.hero.greeting}
        </p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">{data.hero.title}</h1>
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
        <button className="inline-flex h-9 items-center gap-2 rounded-md px-2 font-semibold text-zinc-200 hover:bg-nexus-panel">
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </button>
        <QuickAddMenu actions={data.quickActions} />
        <LogoutForm data={data} />
      </div>
    </header>
  );
}

function InventoryPage({ data }) {
  const [products, setProducts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [refs, setRefs] = useState({ categories: [], brands: [] });
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [status, setStatus] = useState("");
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
          throw new Error("Inventory API request failed.");
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

  const selectedProduct = useMemo(
    () => products.find((product) => product.id === selectedId) || products[0] || null,
    [products, selectedId]
  );
  const lowStockCount = products.filter((product) => product.is_low_stock || product.is_critical_stock).length;
  const inactiveCount = products.filter((product) => !product.isactive || product.available_units === 0).length;

  return (
    <Shell data={data}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0">
          <InventoryHeader actions={data.quickActions} />
          <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4">
            <InventoryMetric label="Total Products" value={summary?.total_products ?? 0} detail="catalogue items" icon="database" />
            <InventoryMetric label="Available Stock" value={summary?.available_units ?? 0} detail="units ready to use" icon="layers" />
            <InventoryMetric label="Reserved Stock" value={summary?.reserved_units ?? 0} detail="pending allocation" icon="box" />
            <InventoryMetric
              label="Low Stock Alerts"
              value={summary?.low_stock_products ?? 0}
              detail="products below threshold"
              icon="triangle-alert"
              alert={(summary?.critical_stock_products ?? 0) > 0}
              warning={(summary?.low_stock_products ?? 0) > 0}
            />
          </section>

          <section className="mt-4 rounded-lg border border-nexus-line bg-nexus-panel p-3">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center">
              <label className="flex h-10 flex-1 items-center gap-3 rounded-md border border-nexus-line bg-black px-3 text-zinc-500">
                <Search className="h-4 w-4" />
                <input
                  className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-500"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search by product name, SKU, barcode, or serial..."
                />
              </label>
              <span className="inline-flex items-center gap-2 text-sm text-zinc-400">
                <Filter className="h-4 w-4" />
                Filter
              </span>
              <Select value={category} onChange={setCategory} options={refs.categories.map((item) => [item.id, item.name])} label="Category" />
              <Select value={brand} onChange={setBrand} options={refs.brands.map((item) => [item.id, item.brandname])} label="Brand" />
              <Select
                value={status}
                onChange={setStatus}
                options={[
                  ["available", "Available"],
                  ["reserved", "Reserved"],
                  ["sold", "Sold"],
                  ["returned", "Returned"],
                  ["inactive", "Inactive"]
                ]}
                label="Status"
              />
              <span className="text-right text-xs text-zinc-500 xl:ml-auto">
                {products.length} products
              </span>
            </div>
          </section>

          <InventoryTable
            products={products}
            selectedId={selectedProduct?.id}
            onSelect={setSelectedId}
            loading={loading}
            error={error}
          />
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500">
            <span>Showing {products.length} products</span>
            <span>{lowStockCount} low stock - {inactiveCount} inactive</span>
          </div>
        </div>

        <ProductDetail product={selectedProduct} />
      </div>
    </Shell>
  );
}

function InventoryHeader({ actions }) {
  const addProduct = actions.find((action) => action.label === "Add Product");
  return (
    <header className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-white">Inventory</h1>
        <p className="mt-1 text-sm text-zinc-400">Manage products and stock availability.</p>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <button className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
          <Download className="h-4 w-4" />
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

function InventoryMetric({ label, value, detail, icon, alert = false, warning = false }) {
  return (
    <article className={`min-h-28 rounded-lg border bg-nexus-panel p-4 ${alert ? "border-nexus-red/70" : warning ? "border-nexus-orange/70" : "border-nexus-line"}`}>
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm text-zinc-400">{label}</p>
        <span className={`rounded-md p-2 ${alert ? toneClasses.red : warning ? toneClasses.warning : toneClasses.neutral}`}>
          <Icon name={icon} />
        </span>
      </div>
      <p className={`mt-5 text-3xl font-bold ${alert ? "text-nexus-red" : warning ? "text-nexus-orange" : "text-zinc-100"}`}>{formatCount(value)}</p>
      <p className="mt-1 text-sm text-zinc-400">{detail}</p>
    </article>
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
              <TableMessage message="Loading inventory..." />
            ) : error ? (
              <TableMessage message={error} />
            ) : products.length ? (
              products.map((product) => (
                <tr
                  key={product.id}
                  className={`cursor-pointer border-t border-nexus-line hover:bg-zinc-900/70 ${
                    selectedId === product.id ? "bg-amber-950/20 outline outline-1 outline-nexus-orange/50" : ""
                  }`}
                  onClick={() => window.location.assign(`/inventory/products/${product.id}/`)}
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
  const critical = product.is_critical_stock;
  return (
    <div className="w-28">
      <p className="text-xs font-semibold text-white">
        <span className={critical ? "text-nexus-red" : low ? "text-nexus-orange" : "text-white"}>{product.available_units}</span>
        <span className="text-zinc-500"> / {product.total_units}</span>
      </p>
      <div className="mt-2 h-1 rounded-full bg-zinc-800">
        <div
          className={`h-1 rounded-full ${critical ? "bg-nexus-red" : low ? "bg-nexus-orange" : "bg-nexus-green"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

function ProductStatus({ product }) {
  let label = "Active";
  let className = statusStyles.available;
  if (!product.isactive || product.available_units === 0) {
    label = "Inactive";
    className = statusStyles.inactive;
  } else if (product.is_critical_stock) {
    label = "Critical Stock";
    className = statusStyles.inactive;
  } else if (product.is_low_stock) {
    label = "Low Stock";
    className = statusStyles.returned;
  }
  return <span className={`rounded-md px-2 py-1 text-xs font-bold ${className}`}>{label}</span>;
}

function ProductDetail({ product }) {
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
        <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Product Detail</h2>
        <button className="text-zinc-500 hover:text-zinc-200" type="button">
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
          <h3 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Stock Summary</h3>
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
          <DetailRow label="Minimum Level" value={product.minimum_stock_level} />
          <DetailRow label="Reorder Level" value={product.reorder_stock_level} />
        </div>

        <a
          href={`/admin/bim_stock/product/${product.id}/change/`}
          className="flex items-center justify-between rounded-lg border border-nexus-line bg-nexus-panel2 px-4 py-3 hover:border-nexus-orange/70"
        >
          <span className="inline-flex items-center gap-3 text-sm font-semibold text-white">
            <Package className="h-4 w-4 text-nexus-orange" />
            Stock Units
          </span>
          <ChevronRight className="h-4 w-4 text-zinc-500" />
        </a>
      </div>
      <div className="mt-auto grid grid-cols-2 gap-2 border-t border-nexus-line p-4">
        <a href={`/admin/bim_stock/product/${product.id}/change/`} className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-nexus-line text-sm font-semibold text-zinc-200">
          <Edit3 className="h-4 w-4" />
          Edit
        </a>
        <a href={`/inventory/products/${product.id}/`} className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-nexus-orange text-sm font-semibold text-black">
          <Eye className="h-4 w-4" />
          Full View
        </a>
        <div className="hidden">
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "✓" : "○"} {label}
            </p>
          ))}
        </div>

        <div className="hidden">
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "✓" : "○"} {label}
            </p>
          ))}
        </div>
      </div>
    </aside>
  );
}

function ProductDetailsPage({ data }) {
  const productId = data.currentPath?.match(/\/inventory\/products\/(\d+)\//)?.[1];
  const [product, setProduct] = useState(null);
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadProduct() {
      setLoading(true);
      setError("");
      try {
        const [productResponse, unitsResponse] = await Promise.all([
          fetch(data.api.productDetail.replace("{id}", productId), {
            signal: controller.signal
          }),
          fetch(`${data.api.productUnits}?product=${productId}`, {
            signal: controller.signal
          })
        ]);

        if (!productResponse.ok) {
          throw new Error("Could not load product details.");
        }

        setProduct(await productResponse.json());
        setUnits(unitsResponse.ok ? await unitsResponse.json() : []);
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
  }, [data.api.productDetail, data.api.productUnits, productId]);

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
  const recentActivity = units.slice(0, 6).map((unit) => ({
    title: activityTitle(unit),
    detail: activityDetail(unit),
    date: formatDate(unit.purchase_date || unit.sold_date || unit.crdate),
    tone: unit.status
  }));

  return (
    <Shell data={data}>
      <header className="mb-5">
        <div className="text-sm text-zinc-500">
          <a className="hover:text-zinc-200" href="/inventory/">Inventory</a>
          <span className="mx-2">›</span>
          <span>Products</span>
          <span className="mx-2">›</span>
          <span className="font-semibold text-white">{product.display_name}</span>
        </div>
        <div className="mt-5 flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="flex items-start gap-4">
            <Avatar product={product} />
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl font-bold text-white">{product.display_name}</h1>
                <ProductStatus product={product} />
              </div>
              <p className="mt-2 text-sm text-zinc-400">
                <span className="font-mono font-bold text-nexus-orange">{product.sku}</span>
                <span className="mx-2">•</span>
                {product.category_name}
                <span className="mx-2">•</span>
                {product.brand_name} {product.model_name}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm">
            <a href={`/admin/bim_stock/product/${product.id}/change/`} className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
              <Edit3 className="h-4 w-4" />
              Edit Product
            </a>
            <a href="/inventory/receiving/new/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
              <Download className="h-4 w-4" />
              Receive Stock
            </a>
            <a href="/inventory/deliveries/new/" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
              <Truck className="h-4 w-4" />
              Create Delivery
            </a>
            <a href="/inventory/receiving/new/" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
              <Plus className="h-4 w-4" />
              Add Unit
            </a>
            <button className="inline-flex h-9 items-center rounded-md px-2 text-zinc-400 hover:bg-nexus-panel">
              <MoreHorizontal className="h-5 w-5" />
            </button>
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
          danger={product.is_critical_stock}
        />
        <ProductDetailMetric label="Reserved" value={product.reserved_units} detail="pending allocation" />
        <ProductDetailMetric label="Minimum Level" value={product.minimum_stock_level} detail="critical threshold" />
        <ProductDetailMetric label="Reorder Level" value={product.reorder_stock_level} detail="low-stock threshold" info />
      </section>

      <nav className="mt-5 flex gap-1 overflow-x-auto border-b border-nexus-line text-sm font-semibold">
        {[
          ["Overview", ""],
          ["Stock Units", product.total_units],
          ["Movements", 0],
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
        <div className="grid gap-5 xl:grid-cols-2">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel p-5">
            <SectionTitle title="Product Information" />
            <dl className="mt-4 divide-y divide-nexus-line">
              <DetailRow label="Product Name" value={product.descript} />
              <DetailRow label="Printed Name" value={product.printed || "-"} />
              <DetailRow label="SKU" value={product.sku} />
              <DetailRow label="Barcode" value={product.barcode || "-"} />
              <DetailRow label="Type" value={product.type_name} />
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
                <DetailRow label="Supplier Code" value={supplierUnit ? `${product.model_name}-OEM` : "-"} />
                <DetailRow label="Last Purchase" value={formatDate(supplierUnit?.purchase_date || supplierUnit?.crdate)} />
                <DetailRow label="Last Cost" value={lastCostUnit ? `$${Number(lastCostUnit.cost).toFixed(2)}` : "-"} />
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
                <DetailRow label="Minimum Level" value={product.minimum_stock_level} />
                <DetailRow label="Reorder Level" value={product.reorder_stock_level} />
              </dl>
            </section>
          </div>
        </div>

        <aside className="rounded-lg border border-nexus-line bg-nexus-panel">
          <PanelHeader title="Recent Activity" />
          {recentActivity.length ? (
            recentActivity.map((item) => (
              <div key={`${item.title}-${item.detail}`} className="border-t border-nexus-line px-4 py-4">
                <p className="text-sm font-bold text-white">{item.title}</p>
                <p className="mt-1 text-xs text-zinc-500">{item.detail}</p>
                <p className="mt-1 text-xs text-zinc-600">{item.date}</p>
              </div>
            ))
          ) : (
            <p className="border-t border-nexus-line px-4 py-5 text-sm text-zinc-500">
              No stock-unit activity yet.
            </p>
          )}
          <a href={`/stock/products/${product.id}/`} className="block border-t border-nexus-line px-4 py-4 text-center text-sm font-semibold text-nexus-orange hover:bg-nexus-panel2">
            View legacy stock page
          </a>
        </aside>
      </div>
    </Shell>
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

function activityTitle(unit) {
  if (unit.status === "sold") return "Stock Delivered";
  if (unit.status === "reserved") return "Unit Reserved";
  if (unit.status === "returned") return "Unit Returned";
  return "Stock Received";
}

function activityDetail(unit) {
  if (unit.status === "sold") return `${unit.serial_number} delivered`;
  if (unit.status === "reserved") return `${unit.serial_number} reserved`;
  if (unit.status === "returned") return `${unit.serial_number} returned`;
  return `${unit.serial_number}${unit.supplier_name ? ` - ${unit.supplier_name}` : ""}`;
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(date);
}

function AddProductPage({ data }) {
  const emptyForm = {
    descript: "",
    type: "",
    category: "",
    brand: "",
    modelName: "",
    barcode: "",
    notes: "",
    isactive: true
  };
  const [form, setForm] = useState(emptyForm);
  const [refs, setRefs] = useState({ types: [], categories: [], brands: [] });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadRefs() {
      const [typesResponse, categoriesResponse, brandsResponse] =
        await Promise.all([
          fetch(data.api.types, { signal: controller.signal }),
          fetch(data.api.categories, { signal: controller.signal }),
          fetch(data.api.brands, { signal: controller.signal })
        ]);

      setRefs({
        types: typesResponse.ok ? await typesResponse.json() : [],
        categories: categoriesResponse.ok ? await categoriesResponse.json() : [],
        brands: brandsResponse.ok ? await brandsResponse.json() : []
      });
    }

    loadRefs().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load product form data.");
      }
    });

    return () => controller.abort();
  }, [data.api.brands, data.api.categories, data.api.types]);

  const filteredCategories = form.type
    ? refs.categories.filter((category) => String(category.type) === String(form.type))
    : refs.categories;
  const selectedCategory = refs.categories.find((category) => String(category.id) === String(form.category));
  const selectedType = refs.types.find((type) => String(type.id) === String(form.type)) || {
    name: selectedCategory?.type_name || ""
  };
  const selectedBrand = refs.brands.find((brand) => String(brand.id) === String(form.brand));
  const requiredDone = [form.descript, form.type, form.category, form.brand, form.modelName].filter(Boolean).length;
  const requiredTotal = 5;
  const requiredProgress = Math.round((requiredDone / requiredTotal) * 100);
  const skuPreview =
    selectedCategory && selectedBrand && form.modelName
      ? `${selectedCategory.name.slice(0, 3).toUpperCase()}-${selectedBrand.brandname.slice(0, 3).toUpperCase()}-${form.modelName.replace(/\s+/g, "").toUpperCase()}`
      : "auto-generate";

  function updateField(name, value) {
    setForm((current) => {
      const next = { ...current, [name]: value };
      if (name === "type") {
        next.category = "";
      }
      return next;
    });
  }

  async function saveProduct(addAnother = false) {
    setSaving(true);
    setError("");
    try {
      const response = await fetch(data.api.products, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          descript: form.descript,
          printed: "",
          category: form.category,
          brand: form.brand,
          model_name_input: form.modelName,
          barcode: form.barcode,
          isactive: form.isactive
        })
      });

      if (!response.ok) {
        const details = await response.json().catch(() => ({}));
        throw new Error(firstApiError(details) || "Could not save product.");
      }

      if (addAnother) {
        setForm(emptyForm);
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
            onReset={() => setForm(emptyForm)}
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
              <Field label="Type" required>
                <SelectInput value={form.type} onChange={(value) => updateField("type", value)} options={refs.types.map((item) => [item.id, item.name])} placeholder="Select type..." />
              </Field>
              <Field label="Category" required>
                <SelectInput value={form.category} onChange={(value) => updateField("category", value)} options={filteredCategories.map((item) => [item.id, item.name])} placeholder="Select category..." />
              </Field>
              <Field label="Brand" required>
                <SelectInput value={form.brand} onChange={(value) => updateField("brand", value)} options={refs.brands.map((item) => [item.id, item.brandname])} placeholder="Select brand..." />
              </Field>
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
              <div className="grid aspect-square place-items-center rounded-lg border border-dashed border-nexus-line bg-black text-center text-xs text-zinc-500">
                <span>
                  <Package className="mx-auto mb-2 h-6 w-6 text-zinc-500" />
                  Drop image
                  <br />
                  or click to upload
                </span>
              </div>
              <div>
                <p className="text-sm font-bold text-white">Product Image</p>
                <p className="mt-2 text-sm text-zinc-400">
                  Upload a photo or icon for this product. Used in listings, detail views, and reports.
                </p>
                <p className="mt-4 text-xs text-zinc-500">PNG, JPG - max 5MB</p>
              </div>
            </div>
          </FormSection>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <button type="button" onClick={() => setForm(emptyForm)} className="text-left text-sm font-semibold text-zinc-300 hover:text-white">
              Discard all changes
            </button>
            <div className="flex flex-wrap gap-3">
              <button disabled type="button" className="inline-flex h-10 items-center gap-2 rounded-md bg-zinc-700 px-4 text-sm font-semibold text-zinc-500">
                <Download className="h-4 w-4" />
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
          selectedType={selectedType}
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

function ReceiveStockPage({ data }) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    supplier: "",
    receivingDate: today,
    deliveryNote: "",
    invoiceReference: "",
    receivedBy: data.user?.displayName || "",
    notes: ""
  });
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [query, setQuery] = useState("");
  const [lines, setLines] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const serialBatch = useMemo(() => String(Date.now()).slice(-6), []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadData() {
      const [productsResponse, suppliersResponse] = await Promise.all([
        fetch(data.api.products, { signal: controller.signal }),
        fetch(data.api.suppliers, { signal: controller.signal })
      ]);
      setProducts(productsResponse.ok ? await productsResponse.json() : []);
      setSuppliers(suppliersResponse.ok ? await suppliersResponse.json() : []);
    }

    loadData().catch((loadError) => {
      if (loadError.name !== "AbortError") {
        setError("Could not load receiving data.");
      }
    });

    return () => controller.abort();
  }, [data.api.products, data.api.suppliers]);

  const filteredProducts = products
    .filter((product) => {
      const text = `${product.display_name} ${product.sku} ${product.barcode || ""}`.toLowerCase();
      return query && text.includes(query.toLowerCase());
    })
    .slice(0, 6);
  const selectedSupplier = suppliers.find((supplier) => String(supplier.id) === String(form.supplier));
  const totalUnits = lines.reduce((total, line) => total + Math.max(Number(line.quantity) || 0, 0), 0);
  const totalCost = lines.reduce(
    (total, line) => total + (Number(line.quantity) || 0) * (Number(line.cost) || 0),
    0
  );

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
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

  async function completeReceiving() {
    setSaving(true);
    setError("");
    try {
      if (!form.supplier || !form.receivingDate || !lines.length) {
        throw new Error("Supplier, receiving date, and at least one product are required.");
      }

      for (const line of lines) {
        const quantity = Number(line.quantity) || 0;
        const serials = line.serials
          .split(/\r?\n|,/)
          .map((serial) => serial.trim())
          .filter(Boolean);

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
              supplier: form.supplier,
              cost: line.cost || "0.00",
              purchase_date: form.receivingDate,
              notes: [form.deliveryNote, form.invoiceReference, form.notes]
                .filter(Boolean)
                .join(" | ")
            })
          });

          if (!response.ok) {
            const details = await response.json().catch(() => ({}));
            throw new Error(firstApiError(details) || "Could not create received stock unit.");
          }
        }
      }

      window.location.assign(data.routes.inventory);
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
              <h1 className="text-2xl font-bold text-white">Receive Stock</h1>
              <p className="mt-1 text-sm text-zinc-400">Register incoming inventory items.</p>
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
              <button disabled={saving} onClick={completeReceiving} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
                <Save className="h-4 w-4" />
                Complete Receiving
              </button>
            </div>
          </header>

          {error ? (
            <div className="mb-4 rounded-lg border border-nexus-red/60 bg-red-500/10 px-4 py-3 text-sm font-semibold text-red-200">
              {error}
            </div>
          ) : null}

          <FormSection icon="clipboard" title="Receiving Information" subtitle="Reference and logistics details for this receipt.">
            <div className="mb-5 flex items-center justify-between rounded-lg border border-nexus-line bg-nexus-panel2 p-4">
              <div>
                <p className="text-xs text-zinc-500">Receiving Reference (auto-generated)</p>
                <p className="mt-1 font-mono text-sm font-bold text-zinc-500">Not created yet</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <Field label="Supplier" required>
                <SelectInput value={form.supplier} onChange={(value) => updateField("supplier", value)} options={suppliers.map((item) => [item.id, item.name])} placeholder="Select supplier" />
              </Field>
              <Field label="Receiving Date" required>
                <TextInput value={form.receivingDate} onChange={(value) => updateField("receivingDate", value)} />
              </Field>
              <Field label="Delivery Note Number">
                <TextInput value={form.deliveryNote} onChange={(value) => updateField("deliveryNote", value)} placeholder="Enter delivery note number" />
              </Field>
              <Field label="Invoice Reference">
                <TextInput value={form.invoiceReference} onChange={(value) => updateField("invoiceReference", value)} placeholder="Enter invoice reference" />
              </Field>
              <Field label="Received By">
                <TextInput value={form.receivedBy} onChange={(value) => updateField("receivedBy", value)} />
              </Field>
            </div>
            <div className="mt-5">
              <Field label="Notes">
                <TextInput value={form.notes} onChange={(value) => updateField("notes", value)} placeholder="Condition notes, discrepancies, special instructions..." />
              </Field>
            </div>
          </FormSection>

          <FormSection icon="box" title="Products" subtitle="Search and add products to this receiving record.">
            <div className="relative">
              <div className="flex gap-3">
                <label className="flex h-10 flex-1 items-center gap-3 rounded-md border border-nexus-line bg-black px-3 text-zinc-500">
                  <Search className="h-4 w-4" />
                  <input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
                    placeholder="Search product by name, SKU, or barcode..."
                  />
                </label>
                <button type="button" className="inline-flex h-10 items-center gap-2 rounded-md px-3 text-sm font-semibold text-zinc-300 hover:bg-nexus-panel2">
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
                  <div key={line.key} className="grid gap-3 border-b border-nexus-line p-4 last:border-b-0 lg:grid-cols-[minmax(0,1fr)_90px_120px_minmax(0,1fr)_40px]">
                    <div>
                      <p className="font-bold text-white">{line.product.display_name}</p>
                      <p className="mt-1 font-mono text-xs text-nexus-orange">{line.product.sku}</p>
                    </div>
                    <TextInput value={line.quantity} onChange={(value) => updateLine(line.key, "quantity", value)} />
                    <TextInput value={line.cost} onChange={(value) => updateLine(line.key, "cost", value)} />
                    <textarea
                      value={line.serials}
                      onChange={(event) => updateLine(line.key, "serials", event.target.value)}
                      className="min-h-10 rounded-md border border-nexus-line bg-black px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
                      placeholder="Serials, one per line. Blank = auto-generated"
                    />
                    <button onClick={() => removeLine(line.key)} type="button" className="text-zinc-500 hover:text-nexus-red">
                      <X className="h-4 w-4" />
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

          <FormSection icon="clipboard" title="Attachments" subtitle="Upload invoice, delivery note, or supporting documents.">
            <div className="grid min-h-28 place-items-center rounded-lg border border-dashed border-nexus-line bg-black/30 text-center text-sm text-zinc-600">
              Drop files here or click to upload
              <br />
              PDF, PNG, JPG, XLSX - max 20MB
            </div>
          </FormSection>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-nexus-line bg-nexus-panel">
            <div className="flex items-center justify-between border-b border-nexus-line px-4 py-4">
              <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Receiving Summary</h2>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value="Not created yet" />
              <DetailRow label="Supplier" value={selectedSupplier?.name || "-"} />
              <DetailRow label="Date" value={form.receivingDate || "-"} />
              <DetailRow label="Received By" value={form.receivedBy || "-"} />
              <DetailRow label="Products" value={lines.length} strong />
              <DetailRow label="Total Units" value={totalUnits} strong />
              <DetailRow label="Attachments" value="0" />
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
    customerName: "",
    receiverName: "",
    deliveryDate: today,
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

  async function completeDelivery() {
    setSaving(true);
    setError("");
    try {
      if (!form.customerName || !selectedUnits.length) {
        throw new Error("Customer and at least one stock unit are required.");
      }

      const response = await fetch(data.api.deliveries, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": data.csrfToken
        },
        body: JSON.stringify({
          customer_name: form.customerName,
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

      window.location.assign(data.routes.inventory);
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
              <h1 className="text-2xl font-bold text-white">Create Delivery</h1>
              <p className="mt-1 text-sm text-zinc-400">Record outgoing stock and update unit status.</p>
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
                <Truck className="h-4 w-4" />
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
                <p className="mt-1 font-mono text-sm font-bold text-zinc-500">Not created yet</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <Field label="Customer / Department" required>
                <TextInput value={form.customerName} onChange={(value) => updateField("customerName", value)} placeholder="Enter customer or department" />
              </Field>
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
              <label className="flex h-10 flex-1 items-center gap-3 rounded-md border border-nexus-line bg-black px-3 text-zinc-500">
                <Search className="h-4 w-4" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600"
                  placeholder="Search available unit by product, SKU, barcode, or serial..."
                />
              </label>
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
              <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Delivery Summary</h2>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-black">Draft</span>
            </div>
            <dl className="divide-y divide-nexus-line p-4">
              <DetailRow label="Reference" value="Not created yet" />
              <DetailRow label="Customer" value={form.customerName || "-"} />
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
      <div className="mb-4 text-sm text-zinc-400">
        <a className="hover:text-zinc-200" href="/">BIM Nexus</a>
        <span className="mx-2">/</span>
        <a className="hover:text-zinc-200" href="/inventory/">Application</a>
        <span className="mx-2">/</span>
        <span className="font-mono text-white">05</span>
        <span className="mx-1">-</span>
        <span className="font-semibold text-white">Add Product</span>
      </div>
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-white">Add Product</h1>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <button onClick={onReset} type="button" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
          <RotateCcw className="h-4 w-4" />
          Reset
        </button>
        <button disabled={saving} onClick={onSaveAnother} type="button" className="inline-flex h-9 items-center gap-2 rounded-md px-3 font-semibold text-zinc-200 hover:bg-nexus-panel">
          <Plus className="h-4 w-4" />
          Save & Add Another
        </button>
        <button disabled={saving} onClick={onSave} type="button" className="inline-flex h-9 items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black">
          <Save className="h-4 w-4" />
          Save Product
        </button>
      </div>
      </div>
    </header>
  );
}

function FormSection({ icon, title, subtitle, children }) {
  return (
    <section className="mb-5 rounded-lg border border-nexus-line bg-nexus-panel p-5">
      <div className="flex items-start gap-3 border-b border-nexus-line pb-5">
        <span className="rounded-lg bg-nexus-orange/10 p-2 text-nexus-orange">
          <Icon name={icon} className="h-5 w-5" />
        </span>
        <div>
          <h2 className="font-bold text-white">{title}</h2>
          <p className="mt-1 text-sm text-zinc-500">{subtitle}</p>
        </div>
      </div>
      <div className="pt-5">{children}</div>
    </section>
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

function TextInput({ value, onChange, placeholder, disabled = false }) {
  return (
    <input
      disabled={disabled}
      value={value}
      onChange={(event) => onChange?.(event.target.value)}
      placeholder={placeholder}
      className="h-10 w-full rounded-md border border-nexus-line bg-black px-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 disabled:bg-zinc-800/80 disabled:font-mono disabled:text-zinc-500"
    />
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

function AddProductPreview({
  form,
  selectedType,
  selectedCategory,
  selectedBrand,
  skuPreview,
  requiredDone,
  requiredTotal,
  requiredProgress
}) {
  const missing = [
    ["Product Name", form.descript],
    ["Type", selectedType?.name],
    ["Category", selectedCategory?.name],
    ["Brand", selectedBrand?.brandname],
    ["Model", form.modelName]
  ];
  const optionalFields = [
    ["Barcode", form.barcode],
    ["Internal Notes", form.notes],
    ["Default Supplier", false],
    ["Supplier Cost", false],
    ["Client Price", false],
    ["Product Image", false]
  ];

  return (
    <aside className="space-y-4 xl:sticky xl:top-5 xl:h-fit">
      <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <div className="border-b border-nexus-line px-4 py-4">
        <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Live Preview</h2>
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
          <DetailRow label="Type" value={selectedType?.name || "-"} />
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
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Required</h3>
          {missing.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "✓" : "○"} {label}
            </p>
          ))}
        </div>
        <div className="space-y-2 border-t border-nexus-line pt-4">
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-zinc-400">Optional</h3>
          {optionalFields.map(([label, done]) => (
            <p key={label} className={`text-sm ${done ? "text-zinc-300" : "text-zinc-600"}`}>
              {done ? "✓" : "○"} {label}
            </p>
          ))}
        </div>
      </div>
      </section>

      <section className="rounded-lg border border-nexus-line bg-nexus-panel p-4">
        <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">Product Lifecycle</h2>
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
  return (
    <details className="relative">
      <summary className="inline-flex h-9 cursor-pointer list-none items-center gap-2 rounded-md bg-nexus-orange px-4 font-semibold text-black marker:hidden">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Quick Add
      </summary>
      <div className="absolute right-0 z-20 mt-2 w-64 overflow-hidden rounded-lg border border-nexus-line bg-nexus-panel shadow-2xl">
        {actions.map((action) =>
          action.enabled && action.href ? (
            <a key={action.label} href={action.href} className="flex items-start gap-3 border-b border-nexus-line px-3 py-3 last:border-b-0 hover:bg-nexus-panel2">
              <ActionIcon name={action.icon} />
              <span>
                <span className="block text-sm font-semibold text-white">{action.label}</span>
                <span className="block text-xs text-zinc-500">{action.description}</span>
              </span>
            </a>
          ) : (
            <span key={action.label} className="flex items-start gap-3 border-b border-nexus-line px-3 py-3 opacity-50 last:border-b-0">
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
            item.tone === "danger"
              ? "border-nexus-red/70"
              : item.tone === "warning"
                ? "border-nexus-orange/70"
                : "border-nexus-line"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm text-zinc-400">{item.label}</p>
            <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
              <Icon name={item.icon} />
            </span>
          </div>
          <p
            className={`mt-6 text-3xl font-bold ${
              item.tone === "danger"
                ? "text-nexus-red"
                : item.tone === "warning"
                  ? "text-nexus-orange"
                  : "text-white"
            }`}
          >
            {item.value}
          </p>
          <p className="mt-1 text-sm text-zinc-400">{item.detail}</p>
          {item.trend ? (
            <p className={`mt-2 text-xs font-semibold ${item.tone === "stock" ? "text-nexus-red" : "text-nexus-green"}`}>
              {item.trend}
            </p>
          ) : null}
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
        {items.map((item) => {
          const isEnabled = item.enabled !== false;
          return (
            <article
              key={item.label}
              aria-disabled={!isEnabled}
              className={`flex items-center gap-3 rounded-lg border border-nexus-line bg-nexus-panel p-4 ${
                isEnabled ? "" : "cursor-not-allowed opacity-45 grayscale"
              }`}
            >
              <span className={`rounded-md p-2 ${toneClasses[item.tone] || toneClasses.neutral}`}>
                <Icon name={item.icon} />
              </span>
              <div>
                <p className={`text-sm font-bold ${isEnabled ? "text-white" : "text-zinc-500"}`}>{item.value}</p>
                <p className={`text-xs ${isEnabled ? "text-zinc-300" : "text-zinc-500"}`}>{item.label}</p>
                <p className="text-xs text-zinc-500">{item.detail}</p>
              </div>
            </article>
          );
        })}
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
          const isEnabled = module.enabled && module.href;
          const content = (
            <>
              <span className={`inline-flex rounded-lg p-3 ${toneClasses[module.tone] || toneClasses.neutral}`}>
                <Icon name={module.icon} className="h-5 w-5" />
              </span>
              <h2 className={`mt-4 text-sm font-bold ${isEnabled ? "text-white" : "text-zinc-500"}`}>
                {module.name}
              </h2>
              <p className={`mt-1 min-h-10 text-sm ${isEnabled ? "text-zinc-400" : "text-zinc-600"}`}>
                {module.description}
              </p>
              <div className="mt-4 flex items-center justify-between border-t border-nexus-line pt-3 text-xs">
                <span className="font-mono text-zinc-500">
                  {module.count !== null && module.count !== undefined ? `${formatCount(module.count)} ${module.meta}` : module.meta}
                </span>
                <span className={`inline-flex items-center gap-1 font-semibold ${isEnabled ? "text-nexus-orange" : "text-zinc-600"}`}>
                  {isEnabled ? "Open" : "Pending"} <ChevronRight className="h-4 w-4" />
                </span>
              </div>
            </>
          );

          return isEnabled ? (
            <a key={module.name} href={module.href} className="rounded-lg border border-nexus-line bg-nexus-panel p-4 hover:border-nexus-orange/80">
              {content}
            </a>
          ) : (
            <article key={module.name} aria-disabled="true" className="rounded-lg border border-nexus-line bg-nexus-panel p-4 opacity-55 grayscale">
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
          const isEnabled = action.enabled && action.href;
          const className = `flex w-full items-center gap-3 rounded-lg border px-3 py-3 text-left ${
            index === 0 && isEnabled ? "border-nexus-orange/60 bg-nexus-orange/10" : "border-transparent"
          } ${isEnabled ? "hover:bg-nexus-panel2" : "cursor-not-allowed opacity-45 grayscale"}`;
          const inner = (
            <>
              <ActionIcon name={action.icon} />
              <span className="min-w-0 flex-1">
                <span className={`block text-sm font-bold ${isEnabled ? "text-white" : "text-zinc-500"}`}>
                  {action.label}
                </span>
                <span className="block text-xs text-zinc-500">{action.description}</span>
              </span>
              <ChevronRight className={`h-4 w-4 ${isEnabled ? "text-zinc-600" : "text-zinc-700"}`} aria-hidden="true" />
            </>
          );

          return isEnabled ? (
            <a key={action.label} href={action.href} className={className}>
              {inner}
            </a>
          ) : (
            <button key={action.label} type="button" disabled aria-disabled="true" className={className}>
              {inner}
            </button>
          );
        })}
      </div>
    </aside>
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
              <th className="px-4 py-3 font-medium">Ref</th>
              <th className="px-4 py-3 font-medium">Activity</th>
              <th className="px-4 py-3 font-medium">Performed by</th>
              <th className="px-4 py-3 font-medium">When</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map((item) => (
                <tr key={`${item.reference}-${item.type}`} className="border-t border-nexus-line">
                  <td className="px-4 py-4 font-mono text-xs text-nexus-orange">{item.reference || "-"}</td>
                  <td className="px-4 py-4 font-semibold text-white">{item.type || "-"}</td>
                  <td className="px-4 py-4 text-zinc-400">{item.user || "-"}</td>
                  <td className="px-4 py-4 text-zinc-400">{item.date ? String(item.date) : "-"}</td>
                  <td className="px-4 py-4">
                    <Status status={item.status || "-"} statusClass={item.status_class} />
                  </td>
                </tr>
              ))
            ) : (
              <tr className="border-t border-nexus-line">
                <td className="px-4 py-8 text-center text-sm text-zinc-500" colSpan="5">
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

function LowStockPanel() {
  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Low Stock Alerts" />
      <EmptyPanel message="Low stock thresholds are not configured yet." />
    </section>
  );
}

function RecentDeliveries() {
  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Deliveries" />
      <EmptyPanel message="Delivery records are not configured yet." />
    </section>
  );
}

function RecentReceiving() {
  return (
    <section className="rounded-lg border border-nexus-line bg-nexus-panel">
      <PanelHeader title="Recent Receiving" />
      <EmptyPanel message="Receiving records are not configured yet." />
    </section>
  );
}

function EmptyPanel({ message }) {
  return (
    <div className="grid min-h-40 place-items-center border-t border-nexus-line px-4 py-8 text-center text-sm text-zinc-500">
      {message}
    </div>
  );
}

function Status({ status, statusClass }) {
  const className =
    statusClass === "reserved"
        ? "text-nexus-orange"
        : "text-nexus-green";

  return <span className={`text-xs font-semibold ${className}`}>{status}</span>;
}

function PanelHeader({ title, action, badge }) {
  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3">
      <h2 className="text-xs font-bold uppercase tracking-[0.24em] text-zinc-400">{title}</h2>
      {badge ? <span className="rounded-full bg-nexus-orange px-2 py-1 text-xs font-bold text-white">{badge}</span> : null}
      {action ? <button className="text-xs font-semibold text-nexus-orange">{action}</button> : null}
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

function LogoutForm({ data }) {
  return (
    <form method="post" action={data.logoutHref}>
      <input type="hidden" name="csrfmiddlewaretoken" value={data.csrfToken} />
      <button className="h-9 rounded-md border border-nexus-line px-3 font-semibold text-zinc-300 hover:bg-nexus-panel">
        Log out
      </button>
    </form>
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

  const currentPath = initialData.currentPath || window.location.pathname;

  if (currentPath.startsWith("/settings")) {
    return <SettingsPage data={initialData} />;
  }

  if (currentPath.startsWith("/operations")) {
    return <OperationsPage data={initialData} />;
  }

  if (currentPath.startsWith("/inventory/products/new")) {
    return <AddProductPage data={initialData} />;
  }

  if (/^\/inventory\/products\/\d+\//.test(currentPath)) {
    return <ProductDetailsPage data={initialData} />;
  }

  if (currentPath.startsWith("/inventory/receiving/new")) {
    return <ReceiveStockPage data={initialData} />;
  }

  if (currentPath.startsWith("/inventory/deliveries/new")) {
    return <CreateDeliveryPage data={initialData} />;
  }

  if (currentPath.startsWith("/inventory")) {
    return <InventoryPage data={initialData} />;
  }

  return <CommandCenter data={initialData} />;
}
