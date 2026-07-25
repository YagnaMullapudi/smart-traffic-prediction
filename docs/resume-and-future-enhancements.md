# Resume / Portfolio Description

## Short version (one bullet)

> **Smart Traffic Prediction System** — Full-stack ML/DL platform predicting traffic congestion (LSTM/GRU) and accident risk (XGBoost/Random Forest/LightGBM) from historical traffic data, with congestion-aware route recommendation (Dijkstra/A*), a FastAPI + PostgreSQL backend, JWT auth, a React dashboard, and Docker-based deployment to AWS.

## Long version (project description section)

**Smart Traffic Prediction System** | *Python, FastAPI, PostgreSQL, React, TensorFlow/Keras, scikit-learn, XGBoost, LightGBM, Docker, AWS*

Designed and built an end-to-end traffic analytics platform that ingests historical traffic, weather, and accident data and serves two prediction tasks through a REST API and web dashboard:

- **Deep learning congestion forecasting**: engineered a sliding-window time-series pipeline and trained/compared LSTM and GRU networks (TensorFlow/Keras) to forecast near-term traffic volume, automatically selecting the best model by RMSE.
- **Machine learning accident-risk classification**: built a tabular preprocessing pipeline (missing-value imputation, IQR-based outlier capping, time-based feature engineering, categorical encoding) feeding four candidate classifiers (Random Forest, XGBoost, LightGBM, Decision Tree), evaluated on accuracy/precision/recall/F1/ROC-AUC with automatic best-model selection.
- **Route recommendation**: implemented Dijkstra and A* search over a congestion-weighted road-network graph (NetworkX) to recommend fastest routes under current predicted conditions.
- **Backend**: designed a modular FastAPI service (JWT auth, dataset upload, training endpoints, prediction endpoints, dashboard aggregation) backed by PostgreSQL via SQLAlchemy, with clear separation between API, ML/DL core, and data layers.
- **Frontend**: built a React (Vite) dashboard with a custom design system for dataset management, model training/comparison, live prediction, and route lookup.
- **DevOps**: containerized all services with Docker and Docker Compose (backend, frontend/Nginx, PostgreSQL) and documented an AWS EC2 + S3 + GitHub Actions deployment path.

## Talking points for interviews

- **Why ROC-AUC over accuracy for accident prediction?** Accident events are rare (class imbalance) — accuracy can look deceptively high on a model that predicts "no accident" every time. ROC-AUC measures ranking quality across all thresholds regardless of class balance.
- **Why LSTM/GRU and not a simple ARIMA model?** Traffic has multiple interacting seasonal patterns (hour-of-day, day-of-week) plus nonlinear dependencies on weather/road conditions; recurrent networks can learn these jointly from raw sequences without manual seasonal decomposition, and this project's architecture also generalizes to multivariate inputs.
- **Why IQR capping instead of dropping outliers?** Traffic outliers (e.g., accident-triggered congestion spikes) are often signal, not noise — dropping rows would discard exactly the events the accident model needs to learn from. Capping bounds their influence without deleting them.
- **Why Dijkstra/A\* rather than a pretrained routing service?** Demonstrates the underlying graph algorithm and shows how predicted congestion (a "soft" cost) integrates with a classic shortest-path algorithm as an edge-weight function — a pattern that generalizes to any traffic-aware routing problem.

## Future enhancements

- Real-time data ingestion (streaming traffic sensor feeds via Kafka/Kinesis) instead of batch CSV upload
- Multivariate DL models (weather + road-type + historical volume jointly, not just a single time series)
- Move training to an async job queue (Celery/Redis) with progress polling in the UI
- Graph neural networks (GNN) for network-wide congestion propagation, rather than per-edge forecasting
- Model versioning/rollback and A/B comparison in the dashboard
- Mobile-responsive route-finder with live map rendering (Mapbox/Leaflet) instead of the demo node graph
- Alerting (email/SMS) when predicted accident risk crosses a threshold on a monitored road segment
