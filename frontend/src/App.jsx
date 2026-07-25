import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import TrainModels from "./pages/TrainModels";
import Predict from "./pages/Predict";
import RouteFinder from "./pages/RouteFinder";

function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}

function ProtectedLayout({ children }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/datasets" element={<ProtectedLayout><Datasets /></ProtectedLayout>} />
      <Route path="/models" element={<ProtectedLayout><TrainModels /></ProtectedLayout>} />
      <Route path="/predict" element={<ProtectedLayout><Predict /></ProtectedLayout>} />
      <Route path="/routes" element={<ProtectedLayout><RouteFinder /></ProtectedLayout>} />
    </Routes>
  );
}
