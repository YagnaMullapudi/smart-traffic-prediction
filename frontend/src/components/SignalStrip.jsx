/**
 * Recurring visual signature: a thin strip of colored segments echoing a
 * traffic-light sequence. Opens every page as a quiet "status readout"
 * rather than a decorative divider — segment colors are semantic (low/
 * medium/high load), not arbitrary.
 */
export default function SignalStrip({ pattern = ["low", "low", "medium", "low", "high", "low", "medium", "low"] }) {
  const colorFor = {
    low: "var(--risk-low)",
    medium: "var(--risk-medium)",
    high: "var(--risk-high)",
  };
  return (
    <div className="signal-strip">
      {pattern.map((level, i) => (
        <span key={i} style={{ background: colorFor[level], opacity: 0.85 }} />
      ))}
    </div>
  );
}
