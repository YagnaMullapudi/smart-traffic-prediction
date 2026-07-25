import { useEffect, useState } from "react";
import { datasetApi } from "../services/api";
import SignalStrip from "../components/SignalStrip";

export default function Datasets() {
  const [datasets, setDatasets] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  function refresh() {
    datasetApi.list().then((res) => setDatasets(res.data)).catch(() => {});
  }

  useEffect(refresh, []);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await datasetApi.upload(file);
      refresh();
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div>
      <SignalStrip pattern={["low", "low", "low", "medium", "low", "low", "low", "low"]} />
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>Datasets</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24 }}>
        Upload traffic, weather, road, or accident CSVs. Row/column counts are detected automatically.
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <label className="btn" style={{ display: "inline-block" }}>
          {uploading ? "Uploading…" : "Upload dataset (.csv)"}
          <input type="file" accept=".csv,.parquet" onChange={handleUpload} disabled={uploading} hidden />
        </label>
        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Filename</th><th>Rows</th><th>Columns</th><th>Uploaded</th></tr>
          </thead>
          <tbody>
            {datasets.length === 0 && (
              <tr><td colSpan={4} style={{ color: "var(--text-secondary)", fontFamily: "var(--font-body)" }}>
                No datasets yet. Upload one above to get started.
              </td></tr>
            )}
            {datasets.map((d) => (
              <tr key={d.id}>
                <td>{d.filename}</td>
                <td>{d.rows ?? "—"}</td>
                <td>{d.columns ?? "—"}</td>
                <td>{new Date(d.uploaded_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
