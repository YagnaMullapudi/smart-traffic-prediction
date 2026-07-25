import { useEffect, useState } from "react";
import { dashboardApi } from "../services/api";
import SignalStrip from "../components/SignalStrip";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboardApi.stats()
      .then((res) => setStats(res.data))
      .catch(() => setError("Couldn't load stats yet — train a model or upload a dataset to get started."));
  }, []);

  return (
    <div>
      <SignalStrip />
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>Operations overview</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: 28 }}>
        Live summary of your datasets, trained models, and prediction activity.
      </p>

      {error && <div className="card" style={{ color: "var(--text-secondary)" }}>{error}</div>}

      {stats && (
        <div className="card-grid">
          <div className="card">
            <div className="stat-label">Datasets uploaded</div>
            <div className="stat-value">{stats.total_datasets}</div>
          </div>
          <div className="card">
            <div className="stat-label">Predictions served</div>
            <div className="stat-value">{stats.total_predictions}</div>
          </div>
          <div className="card">
            <div className="stat-label">Best accident model</div>
            <div className="stat-value" style={{ fontSize: 18 }}>{stats.best_ml_model || "—"}</div>
          </div>
          <div className="card">
            <div className="stat-label">Best congestion model</div>
            <div className="stat-value" style={{ fontSize: 18 }}>{stats.best_dl_model || "—"}</div>
          </div>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Getting started</h3>
        <ol style={{ color: "var(--text-secondary)", lineHeight: 1.9, paddingLeft: 20 }}>
          <li>Upload a traffic dataset on the <strong style={{ color: "var(--text-primary)" }}>Datasets</strong> page.</li>
          <li>Train ML (accident risk) and DL (congestion forecast) models on <strong style={{ color: "var(--text-primary)" }}>Train Models</strong>.</li>
          <li>Run live predictions on the <strong style={{ color: "var(--text-primary)" }}>Predict</strong> page.</li>
          <li>Get a congestion-aware route on <strong style={{ color: "var(--text-primary)" }}>Route Finder</strong>.</li>
        </ol>
      </div>
    </div>
  );
}
