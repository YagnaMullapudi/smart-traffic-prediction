# Smart Traffic Prediction System

A full-stack Machine Learning + Deep Learning platform that predicts traffic congestion and accident risk, and recommends congestion-aware routes. Built as a portfolio-grade, production-shaped project: FastAPI + PostgreSQL backend, React dashboard, Docker/AWS deployment.

## What it does

| Capability | How |
|---|---|
| **Accident risk prediction** | Random Forest, XGBoost, LightGBM, Decision Tree — trained, compared on Accuracy/Precision/Recall/F1/ROC-AUC, best model auto-selected |
| **Congestion forecasting** | LSTM & GRU (TensorFlow/Keras) on sliding-window traffic sequences — compared on RMSE/MAE/MAPE |
| **Route recommendation** | Dijkstra & A* over a congestion-weighted road-network graph (NetworkX) |
| **Dashboard** | React (Vite) app: dataset upload, model training/comparison, live prediction, route finder |
| **API** | FastAPI, JWT auth, REST endpoints for every capability above |
| **Data layer** | PostgreSQL (users, datasets, model results, predictions, logs) |

## Project structure

```
smart-traffic-prediction/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/                # config, security (JWT/bcrypt)
│   │   ├── db/                  # SQLAlchemy engine/session
│   │   ├── models/               # ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── ml/
│   │   │   ├── preprocessing.py         # Phase 2: cleaning, feature engineering
│   │   │   ├── train_ml.py              # Phase 4: accident-risk ML models
│   │   │   ├── train_dl.py              # Phase 5: LSTM/GRU congestion forecasting
│   │   │   └── route_recommendation.py  # Phase 6: Dijkstra/A*
│   │   └── api/routes/            # auth, datasets, ml, dl, routing, dashboard
│   ├── tests/                     # pytest unit tests
│   ├── data/                      # raw/processed datasets (gitignored, .gitkeep present)
│   ├── saved_models/               # trained model artifacts (gitignored, .gitkeep present)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Login, Dashboard, Datasets, TrainModels, Predict, RouteFinder
│   │   ├── components/            # Sidebar, SignalStrip
│   │   ├── services/api.js        # Axios client + JWT interceptor
│   │   └── index.css              # design system (tokens, layout, components)
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
│   ├── architecture.md            # system architecture diagram
│   ├── er-diagram.md              # database ER diagram
│   ├── data-flow-diagram.md       # end-to-end data flow diagram
│   ├── sequence-diagrams.md       # auth + train/predict sequence diagrams
│   ├── deployment-guide.md        # local, Docker Compose, AWS EC2/S3/GitHub Actions
│   └── resume-and-future-enhancements.md
├── docker-compose.yml
├── .env.example
└── .gitignore
```

All diagrams are Mermaid — they render natively in GitHub's file viewer, no extra tooling needed.

## Quick start

**Full stack, one command (recommended):**
```bash
cp .env.example .env   # then edit SECRET_KEY
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend API docs (Swagger): http://localhost:8000/docs

**Manual local dev:** see `docs/deployment-guide.md` §1.

## Suggested datasets (Module 1: Data Collection)

The pipeline expects a CSV with, at minimum, a `timestamp` column and whatever numeric target you're training against (`accident` for the ML task, `traffic_volume` or similar for the DL task). Good public sources to start from:

- [Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) (UCI) — hourly traffic volume + weather, ideal for the DL congestion task
- [US Accidents (2016–2023)](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents) (Kaggle) — large accident dataset with road/weather features, ideal for the ML accident-risk task
- [Road Traffic Severity Classification](https://www.kaggle.com/datasets/saurabhshahane/road-traffic-accidents) (Kaggle) — smaller accident dataset, good for quick iteration

Upload any of these (trimmed/sampled if large) via the Datasets page, then point the ML/DL training forms at the relevant target column.

## How each module maps to the original spec

This build follows the 13-module spec from the original CARE prompt:

1. **Data Collection** → `/api/datasets/upload`, stores file + row/column metadata
2. **Data Preprocessing** → `app/ml/preprocessing.py`
3. **EDA** → not yet built as an endpoint; the cleaned DataFrame from preprocessing is ready to feed a notebook or a future `/api/eda` endpoint (see Future Enhancements)
4. **ML module** → `app/ml/train_ml.py` + `/api/ml/*`
5. **DL module** → `app/ml/train_dl.py` + `/api/dl/*`
6. **Route recommendation** → `app/ml/route_recommendation.py` + `/api/routes/recommend`
7. **Dashboard** → `frontend/src/pages/*`
8. **Backend API** → `app/api/routes/*`
9. **Database** → `app/models/models.py`, PostgreSQL via Docker Compose
10. **Auth** → `app/api/routes/auth.py`, JWT + bcrypt
11. **Deployment** → `docker-compose.yml`, `docs/deployment-guide.md`
12. **Monitoring** → basic logging + global exception handler in `app/main.py`; see Future Enhancements for production-grade monitoring
13. **Testing** → `backend/tests/`

See `docs/resume-and-future-enhancements.md` for what's intentionally left as a next step (EDA endpoint, async training queue, real-time ingestion, etc.) — a good source of "what would you do next" interview answers.

## License

MIT — use freely for your portfolio, resume projects, or as a learning reference.
