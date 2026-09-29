import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Boxes,
  Cpu,
  Users,
  Zap,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CustomerTable, names, Stat } from "./components";
import { Customer, percent } from "./lib";
import { Dashboard, Model } from "./types";
export function Overview({
  data,
  model,
  setPage,
  inspect,
}: {
  data: Dashboard;
  model: Model;
  setPage: (page: string) => void;
  inspect: (row: Customer) => void;
}) {
  return (
    <>
      <div className="status-strip">
        <span>
          <span className="pulse" /> Serving {names[model.selected]}
        </span>
        <span>
          Measured test PR-AUC{" "}
          <b>{model.comparison[model.selected].test.pr_auc.toFixed(3)}</b>
        </span>
        <span>Model {model.version}</span>
      </div>
      <div className="stats-grid">
        <Stat
          label="PREDICTIONS IN WINDOW"
          value={data.total_predictions.toLocaleString()}
          note="Latest 500 recorded predictions"
          icon={<Users size={18} />}
        />
        <Stat
          label="HIGH-RISK PREDICTIONS"
          value={String(data.high_risk)}
          note={`${data.total_predictions ? percent(data.high_risk / data.total_predictions) : "0%"} of the current window`}
          icon={<Activity size={18} />}
          tone="orange"
        />
        <Stat
          label="AVERAGE CHURN RISK"
          value={
            data.average_probability === null
              ? "—"
              : percent(data.average_probability)
          }
          note="Calibrated model probabilities"
          icon={<BarChart3 size={18} />}
        />
        <Stat
          label="VALUE AT RISK INDEX"
          value={Math.round(data.value_at_risk).toLocaleString()}
          note="Estimated exposure · not currency"
          icon={<Zap size={18} />}
        />
      </div>
      <div className="overview-grid">
        <section className="card">
          <div className="card-title">
            <div>
              <h2>Risk distribution</h2>
              <p>Where predictions fall across the probability spectrum</p>
            </div>
            <span className="tag">LIVE WINDOW</span>
          </div>
          <ResponsiveContainer width="100%" height={255}>
            <BarChart
              data={data.distribution}
              margin={{
                top: 15,
                right: 10,
                bottom: 10,
                left: -25,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e8edf1"
              />
              <XAxis
                dataKey="range"
                tick={{ fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip />
              <Bar
                isAnimationActive={false}
                dataKey="count"
                radius={[5, 5, 0, 0]}
              >
                {data.distribution.map((_, i) => (
                  <Cell
                    key={i}
                    fill={i / 10 >= model.threshold ? "#e5a07e" : "#269d89"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="chart-foot">
            <span>
              <i className="legend green" /> Lower risk
            </span>
            <span>
              <i className="legend orange" /> Above decision threshold
            </span>
          </div>
        </section>
        <section className="card model-card">
          <div className="card-title">
            <h2>Production model</h2>
            <Cpu size={20} />
          </div>
          <div className="model-symbol">
            <Boxes size={28} />
          </div>
          <h3>{names[model.selected]}</h3>
          <p>Selected by validation average precision</p>
          <div className="model-metrics">
            <div>
              <b>{model.comparison[model.selected].test.roc_auc.toFixed(3)}</b>
              <small>TEST ROC-AUC</small>
            </div>
            <div>
              <b>{model.comparison[model.selected].test.f1.toFixed(3)}</b>
              <small>TEST F1</small>
            </div>
          </div>
          <button className="text-button" onClick={() => setPage("Models")}>
            Explore evaluation <ArrowUpRight size={14} />
          </button>
        </section>
      </div>
      <section className="card">
        <div className="card-title">
          <div>
            <h2>Recent customer signals</h2>
            <p>Actual API predictions from the research demo</p>
          </div>
          <button className="text-button" onClick={() => setPage("Customers")}>
            View all customers <ArrowUpRight size={14} />
          </button>
        </div>
        <CustomerTable rows={data.recent} inspect={inspect} />
      </section>
    </>
  );
}
