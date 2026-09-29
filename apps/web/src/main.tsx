import {
  Activity,
  ArrowUpRight,
  Bell,
  Boxes,
  ChevronRight,
  CircleHelp,
  FileUp,
  LayoutDashboard,
  RefreshCw,
  ShieldCheck,
  Users,
  Zap,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { CustomerDetail } from "./CustomerDetail";
import { Customers } from "./Customers";
import { api, Customer } from "./lib";
import { Models } from "./Models";
import { Monitoring } from "./Monitoring";
import { Overview } from "./Overview";
import "./style.css";
import { Dashboard, Explanation, Model, Monitor } from "./types";

const nav = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "Customers", icon: Users },
  { name: "Models", icon: Boxes },
  { name: "Monitoring", icon: Activity },
];

function App() {
  const [page, setPage] = useState("Overview");
  const [data, setData] = useState<Dashboard>();
  const [model, setModel] = useState<Model>();
  const [monitor, setMonitor] = useState<Monitor>();
  const [rows, setRows] = useState<Customer[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [risk, setRisk] = useState("");
  const [selected, setSelected] = useState<Customer>();
  const [explanation, setExplanation] = useState<Explanation>();
  const [explaining, setExplaining] = useState(false);
  const [toast, setToast] = useState("");
  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [d, m, c, o] = await Promise.all([
        api<Dashboard>("/dashboard"),
        api<Model>("/model/info"),
        api<Customer[]>("/customers?limit=500"),
        api<Monitor>("/monitoring"),
      ]);
      setData(d);
      setModel(m);
      setRows(c);
      setMonitor(o);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void refresh();
  }, []);
  useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(""), 5000);
      return () => clearTimeout(id);
    }
  }, [toast]);
  async function inspect(row: Customer) {
    setSelected(row);
    setExplanation(undefined);
    setExplaining(true);
    try {
      setExplanation(await api<Explanation>("/explain", row.features));
    } catch (e) {
      setError(String(e));
    } finally {
      setExplaining(false);
    }
  }
  async function upload(file?: File) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch("/api/predict/csv", {
        method: "POST",
        body,
        headers: sessionStorage.getItem("apiKey")
          ? { "X-API-Key": sessionStorage.getItem("apiKey")! }
          : {},
      });
      if (!response.ok) throw new Error(await response.text());
      const url = URL.createObjectURL(await response.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = "signalforge-predictions.csv";
      a.click();
      URL.revokeObjectURL(url);
      setToast("Batch scored. Results downloaded.");
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  }
  const filtered = rows.filter(
    (r) =>
      r.customer_id.toLowerCase().includes(query.toLowerCase()) &&
      (!risk || r.risk === risk),
  );
  return (
    <div className="shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={() => setPage("Overview")}>
          <span className="brand-mark">
            <Zap size={21} />
          </span>
          SignalForge<span className="ai">AI</span>
        </a>
        <div className="workspace">
          <span className="workspace-avatar">S</span>
          <div>
            Customer intelligence<small>Portfolio workspace</small>
          </div>
          <ChevronRight size={14} />
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav>
          {nav.map(({ name, icon: Icon }) => (
            <button
              key={name}
              onClick={() => {
                setPage(name);
                setSelected(undefined);
              }}
              className={page === name ? "active" : ""}
            >
              <Icon size={18} />
              {name}
              {name === "Monitoring" && monitor?.status === "ALERT" && (
                <span className="nav-dot" />
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="lifecycle">
            <div>
              <span className="pulse" /> ML lifecycle active
            </div>
            <p>
              From customer signals
              <br />
              to explainable decisions.
            </p>
            <div className="tiny-flow">
              INGEST <ChevronRight size={10} /> TRAIN <ChevronRight size={10} />{" "}
              SERVE
            </div>
          </div>
          <a href="/api/docs" target="_blank">
            <CircleHelp size={16} /> API documentation{" "}
            <ArrowUpRight size={14} />
          </a>
          <div className="profile">
            <span>SF</span>
            <div>
              SignalForge demo<small>UCI research dataset</small>
            </div>
          </div>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            Workspace <ChevronRight size={13} /> <b>{page}</b>
          </div>
          <div className="top-actions">
            <span className="demo-badge">RESEARCH DEMO</span>
            <button aria-label="Refresh data" onClick={() => void refresh()}>
              <RefreshCw size={17} className={loading ? "spin" : ""} />
            </button>
            <button
              aria-label="Set API key"
              onClick={() => {
                const key = prompt(
                  "API key for this session (leave blank for local demo)",
                );
                if (key !== null) {
                  sessionStorage.setItem("apiKey", key);
                  void refresh();
                }
              }}
            >
              <ShieldCheck size={17} />
            </button>
            <Bell size={17} />
          </div>
        </header>
        <div className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                CUSTOMER INTELLIGENCE / {page.toUpperCase()}
              </div>
              <h1>
                {selected
                  ? selected.customer_id
                  : page === "Overview"
                    ? "See the signals. Act with clarity."
                    : page === "Customers"
                      ? "Every customer has a signal."
                      : page === "Models"
                        ? "Evidence before complexity."
                        : "Confidence, continuously checked."}
              </h1>
              <p>
                {page === "Overview"
                  ? "An explainable view of churn risk, customer value, and model health."
                  : page === "Customers"
                    ? "Explore scored customers and the factors behind each prediction."
                    : page === "Models"
                      ? "Four model families. One reproducible evaluation protocol."
                      : "Track distribution shifts, data quality, and delayed outcomes."}
              </p>
            </div>
            <label className="primary-button">
              <FileUp size={16} /> Score a CSV
              <input
                type="file"
                accept=".csv"
                onChange={(e) => void upload(e.target.files?.[0])}
              />
            </label>
          </div>
          {error && (
            <div role="alert" className="error">
              {error}
              <button onClick={() => void refresh()}>Retry</button>
            </div>
          )}
          {loading && !data ? (
            <div className="empty">Loading live model and prediction data…</div>
          ) : !data || !model ? (
            <div className="empty">
              Start the API and train a model to connect this workspace.
            </div>
          ) : (
            <>
              {selected ? (
                <CustomerDetail
                  selected={selected}
                  setSelected={setSelected}
                  model={model}
                  rows={rows}
                  explaining={explaining}
                  explanation={explanation}
                />
              ) : (
                <>
                  {page === "Overview" && (
                    <Overview
                      data={data}
                      model={model}
                      setPage={setPage}
                      inspect={inspect}
                    />
                  )}
                  {page === "Customers" && (
                    <Customers
                      filtered={filtered}
                      query={query}
                      setQuery={setQuery}
                      risk={risk}
                      setRisk={setRisk}
                      inspect={inspect}
                    />
                  )}
                  {page === "Models" && <Models model={model} />}
                  {page === "Monitoring" && monitor && (
                    <Monitoring
                      monitor={monitor}
                      setToast={setToast}
                      setError={setError}
                    />
                  )}
                </>
              )}
            </>
          )}
          <footer>
            <span>
              SignalForge AI{" "}
              <span className="muted">/ Explainable customer intelligence</span>
            </span>
            <span>UCI Iranian Churn · CC BY 4.0 · Research demo</span>
          </footer>
        </div>
      </main>
      {toast && (
        <div role="status" className="toast">
          {toast}
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
