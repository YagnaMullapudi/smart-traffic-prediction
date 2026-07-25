import { NavLink, useNavigate } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/datasets", label: "Datasets" },
  { to: "/models", label: "Train Models" },
  { to: "/predict", label: "Predict" },
  { to: "/routes", label: "Route Finder" },
];

export default function Sidebar() {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="signal-dot" />
        Traffic Predict
      </div>
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.to === "/"}
          className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
        >
          {l.label}
        </NavLink>
      ))}
      <div style={{ marginTop: "auto", paddingTop: 24 }}>
        <button className="btn-secondary" style={{ width: "100%" }} onClick={logout}>
          Sign out
        </button>
      </div>
    </aside>
  );
}
