# System Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        UI["React Dashboard\n(Vite, Recharts)"]
    end

    subgraph Edge["Edge / Serving"]
        NGINX["Nginx\n(static files + /api reverse proxy)"]
    end

    subgraph API["Application Layer — FastAPI"]
        AUTH["Auth\n(JWT, bcrypt)"]
        DATASET_EP["Dataset endpoints"]
        ML_EP["ML endpoints\n(train / predict)"]
        DL_EP["DL endpoints\n(train / predict)"]
        ROUTE_EP["Route recommendation"]
        DASH_EP["Dashboard stats"]
    end

    subgraph Core["ML/DL Core"]
        PREP["Preprocessing pipeline\n(clean, engineer, encode, split)"]
        MLTRAIN["ML training\nXGBoost / RF / LightGBM / DT"]
        DLTRAIN["DL training\nLSTM / GRU"]
        ROUTING["Dijkstra / A*\nroad network graph"]
    end

    subgraph Storage["Storage"]
        PG[("PostgreSQL\nusers, datasets,\nmodel results, predictions, logs")]
        FILES[("File storage\nraw CSVs, saved model artifacts")]
    end

    UI -->|HTTPS| NGINX --> API
    AUTH --> PG
    DATASET_EP --> FILES
    DATASET_EP --> PG
    ML_EP --> PREP --> MLTRAIN --> FILES
    ML_EP --> PG
    DL_EP --> PREP
    DL_EP --> DLTRAIN --> FILES
    DL_EP --> PG
    ROUTE_EP --> ROUTING
    DASH_EP --> PG
```

**Notes**
- All ML/DL training runs synchronously inside the FastAPI request in this reference build; for real datasets, move `MLTRAIN`/`DLTRAIN` calls to a background task queue (Celery + Redis, or FastAPI `BackgroundTasks` at minimum) so uploads/training don't block the event loop.
- `FILES` currently means local disk (`backend/data`, `backend/saved_models`), mounted as Docker volumes. Swap for S3 in production (Module 11 of the original spec) by changing `RAW_DATA_DIR`/`MODEL_DIR` handling to an S3-backed storage class.
