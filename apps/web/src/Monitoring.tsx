import {
  Activity,
  BarChart3,
  Download,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Stat } from "./components";
import { api, percent } from "./lib";
import { Monitor } from "./types";
export function Monitoring({
  monitor,
  setToast,
  setError,
}: {
  monitor: Monitor;
  setToast: (t: string) => void;
  setError: (e: string) => void;
}) {
  return (
    <>
      <div className="stats-grid">
        <Stat
          label="REFERENCE COMPARISON"
          value={monitor.status}
          note="PSI threshold: 0.20"
          icon={<Activity />}
        />
        <Stat
          label="OBSERVED WINDOW"
          value={String(monitor.rows)}
          note="Current model · latest 500"
          icon={<Users />}
        />
        <Stat
          label="DRIFTED FEATURES"
          value={String(
            Object.values(monitor.features).filter((f) => f.drift).length,
          )}
          note="Heuristic alerts require investigation"
          icon={<BarChart3 />}
        />
        <Stat
          label="LABELED OUTCOMES"
          value={String(monitor.performance.rows)}
          note={monitor.performance.status}
          icon={<ShieldCheck />}
        />
      </div>
      <section className="card">
        <div className="card-title">
          <div>
            <h2>Feature distribution health</h2>
            <p>
              Compared with the training reference; drift does not prove
              performance loss.
            </p>
          </div>
          <button
            className="text-button"
            onClick={async () => {
              try {
                await api("/monitoring/run", {});
                setToast("Monitoring snapshot saved.");
              } catch (e) {
                setError(String(e));
              }
            }}
          >
            Save snapshot <Download size={14} />
          </button>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>FEATURE</th>
                <th>PSI</th>
                <th>MISSING</th>
                <th>OUTSIDE TRAIN RANGE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(monitor.features).map(([name, f]) => (
                <tr key={name}>
                  <td>{name.replaceAll("_", " ")}</td>
                  <td>{f.psi.toFixed(3)}</td>
                  <td>{percent(f.missing_rate)}</td>
                  <td>{percent(f.out_of_range_rate)}</td>
                  <td>
                    <span className={"badge " + (f.drift ? "high" : "low")}>
                      {f.drift ? "INVESTIGATE" : "STABLE"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {monitor.rows === 0 && (
          <div className="empty">Score customers to begin monitoring.</div>
        )}
      </section>
      <div className="insight">
        <ShieldCheck />
        <div>
          <b>Promotion is gated by evidence</b>
          <p>
            Drift can trigger candidate training. Promotion requires independent
            labels, improved average precision, and calibration and recall
            guardrails. Missing labels never become invented performance scores.
          </p>
        </div>
      </div>
    </>
  );
}
