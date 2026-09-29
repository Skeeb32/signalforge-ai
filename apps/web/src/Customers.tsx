import { Search } from "lucide-react";
import { CustomerTable } from "./components";
import { Customer } from "./lib";
export function Customers({
  filtered,
  query,
  setQuery,
  risk,
  setRisk,
  inspect,
}: {
  filtered: Customer[];
  query: string;
  setQuery: (q: string) => void;
  risk: string;
  setRisk: (r: string) => void;
  inspect: (row: Customer) => void;
}) {
  return (
    <section className="card">
      <div className="card-title">
        <h2>
          Customer explorer <span className="count">{filtered.length}</span>
        </h2>
        <div className="filters">
          <label className="search">
            <Search size={15} />
            <input
              aria-label="Search customer ID"
              placeholder="Search customer ID"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <select
            aria-label="Filter risk"
            value={risk}
            onChange={(e) => setRisk(e.target.value)}
          >
            <option value="">All risk levels</option>
            <option>HIGH</option>
            <option>LOW</option>
          </select>
        </div>
      </div>
      <CustomerTable rows={filtered} inspect={inspect} />
    </section>
  );
}
