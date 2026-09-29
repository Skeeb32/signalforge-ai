import { ArrowUpRight } from "lucide-react";
import React from "react";
import { Customer, percent } from "./lib";
export const names: Record<string, string> = {
  logistic: "Logistic regression",
  random_forest: "Random forest",
  xgboost: "XGBoost",
  pytorch: "PyTorch neural network",
};
export function Stat({
  label,
  value,
  note,
  icon,
  tone = "",
}: {
  label: string;
  value: string;
  note: string;
  icon: React.ReactNode;
  tone?: string;
}) {
  return (
    <section className={"stat " + tone}>
      <div className="stat-top">
        <span>{label}</span>
        {icon}
      </div>
      <strong>{value}</strong>
      <p>{note}</p>
    </section>
  );
}
export function CustomerTable({
  rows,
  inspect,
}: {
  rows: Customer[];
  inspect: (r: Customer) => void;
}) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>CUSTOMER</th>
            <th>CHURN PROBABILITY</th>
            <th>RISK LEVEL</th>
            <th>VALUE AT RISK</th>
            <th>SCORED</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>
                <button className="customer-link" onClick={() => inspect(r)}>
                  <span className="customer-avatar">
                    {r.customer_id.slice(-2)}
                  </span>
                  {r.customer_id}
                </button>
              </td>
              <td>
                <div className="risk-cell">
                  <span>{percent(r.probability)}</span>
                  <div className="mini-bar">
                    <i
                      style={{
                        width: percent(r.probability),
                        background: r.risk === "HIGH" ? "#df956d" : "#29a68d",
                      }}
                    />
                  </div>
                </div>
              </td>
              <td>
                <span className={"badge " + r.risk.toLowerCase()}>
                  <i />
                  {r.risk}
                </span>
              </td>
              <td>
                {r.value_at_risk.toFixed(1)} <small>index</small>
              </td>
              <td className="muted">
                {new Date(r.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </td>
              <td>
                <button
                  aria-label={`Inspect ${r.customer_id}`}
                  className="icon-button"
                  onClick={() => inspect(r)}
                >
                  <ArrowUpRight size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && (
        <div className="empty">
          No predictions match. Upload a customer CSV to get started.
        </div>
      )}
    </div>
  );
}
