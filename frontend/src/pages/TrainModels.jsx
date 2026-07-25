import { useEffect, useState } from "react";
import { datasetApi, mlApi, dlApi } from "../services/api";
import SignalStrip from "../components/SignalStrip";

export default function TrainModels() {
  const [datasets, setDatasets] = useState([]);
  const [datasetId, setDatasetId] = useState("");
  const [mlResults, setMlResults] = useState(null);
  const [dlResults, setDlResults] = useState(null);
  const [mlTarget, setMlTarget] = useState("accident");
  const [dlTarget, setDlTarget] = useState("traffic_volume");
  const [loadingMl, setLoadingMl] = useState(false);
  const [loadingDl, setLoadingDl] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    datasetApi.list().then((res) => setDatasets(res.data)).catch(() => {});
  }, []);

  async function trainMl() {
    setLoadingMl(true);
    setError("");
    try {
      const { data } = await mlApi.train({
        dataset_id: Number(datasetId),
        target_column: mlTarget,
        models: ["random_forest", "xgboost", "lightgbm", "decision_tree"],
      });
      setMlResults(data.sort((a, b) => b.roc_auc - a.roc_auc));
    } catch (err) {
      setError(err?.response?.data?.detail || "ML training failed");
    } finally {
      setLoadingMl(false);
    }
  }

  async function trainDl() {
    setLoadingDl(true);
    setError("");
    try {
      const { data } = await dlApi.train({
        dataset_id: Number(datasetId),
        target_column: dlTarget,
        sequence_length: 24,
        epochs: 20,
        models: ["lstm", "gru"],
      });
      setDlResults(data.sort((a, b) => a.rmse - b.rmse));
    } catch (err) {
      setError(err?.response?.data?.detail || "DL training failed");
    } finally {
      setLoadingDl(false);
    }
  }

  return (
    <div>
      <SignalStrip pattern={["medium", "low", "high", "medium", "low", "low", "medium", "low"]} />
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>Train models</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24 }}>
        Trains all candidate models and automatically flags the best performer.
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="form-row">
          <label>Dataset</label>
          <select value={datasetId} onChange={(e) => setDatasetId(e.target.value)}>
            <option value="">Select a dataset…</option>
            {datasets.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
          </select>
        </div>
        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 12 }}>Accident risk (ML) — XGBoost, Random Forest, LightGBM, Decision Tree</h3>
        <div className="form-row" style={{ maxWidth: 280 }}>
          <label>Target column</label>
          <input value={mlTarget} onChange={(e) => setMlTarget(e.target.value)} />
        </div>
        <button className="btn" onClick={trainMl} disabled={!datasetId || loadingMl}>
          {loadingMl ? "Training…" : "Train & compare"}
        </button>

        {mlResults && (
          <table style={{ marginTop: 16 }}>
            <thead><tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC-AUC</th></tr></thead>
            <tbody>
              {mlResults.map((r, i) => (
                <tr key={r.model_name} style={i === 0 ? { color: "var(--accent)" } : {}}>
                  <td>{r.model_name}{i === 0 ? " ★" : ""}</td>
                  <td>{r.accuracy.toFixed(3)}</td>
                  <td>{r.precision.toFixed(3)}</td>
                  <td>{r.recall.toFixed(3)}</td>
                  <td>{r.f1_score.toFixed(3)}</td>
                  <td>{r.roc_auc.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Congestion forecast (DL) — LSTM vs GRU</h3>
        <div className="form-row" style={{ maxWidth: 280 }}>
          <label>Target column</label>
          <input value={dlTarget} onChange={(e) => setDlTarget(e.target.value)} />
        </div>
        <button className="btn" onClick={trainDl} disabled={!datasetId || loadingDl}>
          {loadingDl ? "Training…" : "Train & compare"}
        </button>

        {dlResults && (
          <table style={{ marginTop: 16 }}>
            <thead><tr><th>Model</th><th>RMSE</th><th>MAE</th><th>MAPE</th></tr></thead>
            <tbody>
              {dlResults.map((r, i) => (
                <tr key={r.model_name} style={i === 0 ? { color: "var(--accent)" } : {}}>
                  <td>{r.model_name.toUpperCase()}{i === 0 ? " ★" : ""}</td>
                  <td>{r.rmse.toFixed(3)}</td>
                  <td>{r.mae.toFixed(3)}</td>
                  <td>{r.mape.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
