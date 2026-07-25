import { useState } from "react";
import { mlApi, dlApi } from "../services/api";
import SignalStrip from "../components/SignalStrip";

export default function Predict() {
  const [featuresJson, setFeaturesJson] = useState('{\n  "hour": 8,\n  "day_of_week": 1,\n  "is_peak_hour": 1,\n  "speed": 22\n}');
  const [accidentResult, setAccidentResult] = useState(null);
  const [accidentError, setAccidentError] = useState("");

  const [sequence, setSequence] = useState(Array.from({ length: 24 }, () => 50).join(", "));
  const [congestionResult, setCongestionResult] = useState(null);
  const [congestionError, setCongestionError] = useState("");

  async function predictAccident() {
    setAccidentError("");
    setAccidentResult(null);
    try {
      const features = JSON.parse(featuresJson);
      const { data } = await mlApi.predict(features);
      setAccidentResult(data);
    } catch (err) {
      setAccidentError(err?.response?.data?.detail || "Invalid input or no trained model yet.");
    }
  }

  async function predictCongestion() {
    setCongestionError("");
    setCongestionResult(null);
    try {
      const values = sequence.split(",").map((v) => parseFloat(v.trim()));
      const { data } = await dlApi.predict(values);
      setCongestionResult(data);
    } catch (err) {
      setCongestionError(err?.response?.data?.detail || "Invalid input or no trained model yet.");
    }
  }

  const badgeClass = (level) => `badge badge-${level}`;

  return (
    <div>
      <SignalStrip pattern={["low", "medium", "high", "high", "medium", "low", "low", "medium"]} />
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>Live prediction</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: 24 }}>
        Score accident risk from road conditions, or forecast the next congestion reading.
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 12 }}>Accident risk</h3>
        <div className="form-row">
          <label>Feature values (JSON — must match your training columns)</label>
          <textarea
            className="mono"
            rows={6}
            style={{ background: "var(--surface-raised)", border: "1px solid var(--border)", color: "var(--text-primary)", borderRadius: 6, padding: 10 }}
            value={featuresJson}
            onChange={(e) => setFeaturesJson(e.target.value)}
          />
        </div>
        <button className="btn" onClick={predictAccident}>Predict risk</button>
        {accidentError && <p className="error-text">{accidentError}</p>}
        {accidentResult && (
          <div style={{ marginTop: 16 }}>
            <span className={badgeClass(accidentResult.risk_level)}>{accidentResult.risk_level.toUpperCase()} RISK</span>
            <p className="mono" style={{ marginTop: 8 }}>
              probability: {accidentResult.accident_probability.toFixed(3)} · model: {accidentResult.model_used}
            </p>
          </div>
        )}
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Congestion forecast</h3>
        <div className="form-row">
          <label>Recent sequence (comma-separated, must match trained sequence length)</label>
          <input value={sequence} onChange={(e) => setSequence(e.target.value)} className="mono" />
        </div>
        <button className="btn" onClick={predictCongestion}>Forecast next value</button>
        {congestionError && <p className="error-text">{congestionError}</p>}
        {congestionResult && (
          <div style={{ marginTop: 16 }}>
            <span className={badgeClass(congestionResult.congestion_level === "moderate" ? "medium" : congestionResult.congestion_level)}>
              {congestionResult.congestion_level.toUpperCase()} CONGESTION
            </span>
            <p className="mono" style={{ marginTop: 8 }}>
              predicted: {congestionResult.predicted_next_values[0].toFixed(2)} · model: {congestionResult.model_used}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
