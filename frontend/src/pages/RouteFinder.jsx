import { useState } from "react";
import { routeApi } from "../services/api";
import SignalStrip from "../components/SignalStrip";

export default function RouteFinder() {
  const [origin, setOrigin] = useState("A");
  const [destination, setDestination] = useState("E");
  const [algorithm, setAlgorithm] = useState("dijkstra");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function findRoute() {
    setError("");
    setResult(null);
    try {
      const { data } = await routeApi.recommend({ origin_node: origin, destination_node: destination, algorithm });
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't find a route between those nodes.");
    }
  }

  return (
    <div>
      <SignalStrip pattern={["low", "low", "medium", "low", "low", "high", "low", "low"]} />
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>Route finder</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24 }}>
        Recommends the fastest path using live congestion-weighted edges (demo network: nodes A–E).
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <div className="form-row">
            <label>Origin</label>
            <input value={origin} onChange={(e) => setOrigin(e.target.value.toUpperCase())} style={{ width: 80 }} />
          </div>
          <div className="form-row">
            <label>Destination</label>
            <input value={destination} onChange={(e) => setDestination(e.target.value.toUpperCase())} style={{ width: 80 }} />
          </div>
          <div className="form-row">
            <label>Algorithm</label>
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
              <option value="dijkstra">Dijkstra</option>
              <option value="astar">A*</option>
            </select>
          </div>
        </div>
        <button className="btn" onClick={findRoute}>Find route</button>
        {error && <p className="error-text">{error}</p>}
      </div>

      {result && (
        <div className="card">
          <div className="stat-label">Recommended path</div>
          <div className="stat-value" style={{ marginBottom: 16 }}>{result.path.join(" → ")}</div>
          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div>
              <div className="stat-label">Distance</div>
              <div className="mono">{result.total_distance_km} km</div>
            </div>
            <div>
              <div className="stat-label">Est. travel time</div>
              <div className="mono">{result.estimated_time_minutes} min</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
