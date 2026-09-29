import { Zap } from "lucide-react";
import { Customer, percent } from "./lib";
import { Explanation, Model } from "./types";
export function CustomerDetail({
  selected,
  setSelected,
  model,
  rows,
  explaining,
  explanation,
}: {
  selected: Customer;
  setSelected: (c: Customer | undefined) => void;
  model: Model;
  rows: Customer[];
  explaining: boolean;
  explanation: Explanation | undefined;
}) {
  return (
    <>
      <button className="text-button" onClick={() => setSelected(undefined)}>
        ← Back to customers
      </button>
      <div className="detail-grid">
        <section className="card">
          <div className="section-label">CHURN PROBABILITY</div>
          <div className="big-risk">{percent(selected.probability)}</div>
          <span className={"badge " + selected.risk.toLowerCase()}>
            {selected.risk} RISK
          </span>
          <p>Decision threshold: {percent(model.threshold)}</p>
          <p>
            Value at risk: <b>{selected.value_at_risk.toFixed(1)}</b> index
            units
          </p>
          <h3>Observed profile</h3>
          {Object.entries(selected.features)
            .filter(([k]) => k !== "customer_id")
            .map(([k, v]) => (
              <div className="profile-row" key={k}>
                <span>{k.replaceAll("_", " ")}</span>
                <b>{String(v ?? "Missing")}</b>
              </div>
            ))}
        </section>
        <section className="card">
          <div className="card-title">
            <h2>What drives this prediction?</h2>
            <span className="tag">SHAP</span>
          </div>
          <p className="muted">Contributions to calibrated churn probability</p>
          {explaining ? (
            <div className="empty">Computing model explanations…</div>
          ) : (
            explanation && (
              <>
                <div className="contributions">
                  {explanation.explanation.map((e) => (
                    <div className="contribution" key={e.feature}>
                      <span>{e.feature.replaceAll("_", " ")}</span>
                      <div>
                        <i
                          style={{
                            width: `${Math.min(100, Math.abs(e.contribution) * 300)}%`,
                            background:
                              e.contribution > 0 ? "#ed8a68" : "#30aa94",
                          }}
                        />
                      </div>
                      <b>
                        {e.contribution > 0 ? "+" : ""}
                        {(e.contribution * 100).toFixed(1)} pp
                      </b>
                    </div>
                  ))}
                </div>
                <div className="insight">
                  <Zap size={18} />
                  <div>
                    <b>Model-derived investigation signals</b>
                    <p>
                      Inspect{" "}
                      {explanation.explanation
                        .filter((e) => e.contribution > 0)
                        .slice(0, 2)
                        .map((e) => e.feature.replaceAll("_", " "))
                        .join(" and ")}
                      . These associations do not establish causes or prove that
                      an intervention will work.
                    </p>
                  </div>
                </div>
                <p className="muted">
                  Baseline: {percent(explanation.base_probability)}.{" "}
                  {explanation.explanation_note}
                </p>
              </>
            )
          )}
          <h3>Prediction history</h3>
          {rows
            .filter((r) => r.customer_id === selected.customer_id)
            .map((r) => (
              <div className="profile-row" key={r.id}>
                <span>{new Date(r.timestamp).toLocaleString()}</span>
                <b>{percent(r.probability)}</b>
              </div>
            ))}
        </section>
      </div>
    </>
  );
}
