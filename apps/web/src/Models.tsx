import { ShieldCheck } from "lucide-react";
import { names } from "./components";
import { Model } from "./types";
export function Models({ model }: { model: Model }) {
  return (
    <>
      <div className="status-strip">
        <span>
          <ShieldCheck size={16} /> {model.selection_policy}
        </span>
      </div>
      <section className="card">
        <div className="card-title">
          <div>
            <h2>Model comparison</h2>
            <p>Held-out test results · choice frozen using validation data</p>
          </div>
          <span className="tag">SEED 42</span>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>MODEL FAMILY</th>
                <th>ROC-AUC</th>
                <th>PR-AUC¹</th>
                <th>PRECISION</th>
                <th>RECALL</th>
                <th>F1</th>
                <th>TRAINING</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(model.comparison).map(([name, r]) => (
                <tr key={name}>
                  <td>
                    <b>{names[name]}</b>{" "}
                    {name === model.selected && (
                      <span className="badge low">SERVING</span>
                    )}
                  </td>
                  {["roc_auc", "pr_auc", "precision", "recall", "f1"].map(
                    (k) => (
                      <td key={k}>{r.test[k].toFixed(3)}</td>
                    ),
                  )}
                  <td>{r.training_seconds.toFixed(1)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="muted">
          ¹ Average precision. Training duration includes model search and
          calibration; machine-dependent.
        </p>
      </section>
      <div className="detail-grid">
        <section className="card">
          <h2>Evaluation protocol</h2>
          <ol className="steps">
            <li>Group identical predictor profiles before splitting</li>
            <li>Three-fold CV and two configurations per family</li>
            <li>Fit sigmoid calibration on separate records</li>
            <li>Select family and F1 threshold on validation data</li>
            <li>Report untouched test performance</li>
          </ol>
          <p>
            {Object.entries(model.dataset.splits)
              .map(([k, v]) => `${k}: ${v.rows}`)
              .join(" · ")}
          </p>
        </section>
        <section className="card">
          <h2>Value-index regression</h2>
          <p>
            Auxiliary random forest predicts the observed calculated
            customer-value index. This is not a forecast of future revenue.
          </p>
          <div className="model-metrics">
            <div>
              <b>{model.regression.mae.toFixed(2)}</b>
              <small>MAE</small>
            </div>
            <div>
              <b>{model.regression.r2.toFixed(3)}</b>
              <small>R²</small>
            </div>
          </div>
          <p className="muted">
            Exposure = churn probability × predicted value index. No currency or
            causal interpretation.
          </p>
        </section>
      </div>
    </>
  );
}
