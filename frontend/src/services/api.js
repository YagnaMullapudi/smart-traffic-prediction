import axios from "axios";

// In local dev, VITE_API_URL is unset and Vite's proxy (see vite.config.js)
// forwards /api to localhost:8000. In production, set VITE_API_URL to your
// deployed backend's URL (e.g. https://smart-traffic-backend.onrender.com/api).
const baseURL = import.meta.env.VITE_API_URL || "/api";
const api = axios.create({ baseURL });

// Attach the JWT to every outgoing request, if present.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authApi = {
  login: (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  register: (email, username, password) => api.post("/auth/register", { email, username, password }),
  profile: () => api.get("/auth/profile"),
};

export const datasetApi = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/datasets/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
  },
  list: () => api.get("/datasets/"),
};

export const mlApi = {
  train: (payload) => api.post("/ml/train", payload),
  predict: (features) => api.post("/ml/predict", { features }),
};

export const dlApi = {
  train: (payload) => api.post("/dl/train", payload),
  predict: (recent_sequence) => api.post("/dl/predict", { recent_sequence }),
};

export const routeApi = {
  recommend: (payload) => api.post("/routes/recommend", payload),
};

export const dashboardApi = {
  stats: () => api.get("/dashboard/stats"),
};

export default api;
