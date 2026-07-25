# Deployment Guide

## 1. Local development (fastest path)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env   # edit DATABASE_URL to point at a local Postgres, or use docker for just the db
uvicorn app.main:app --reload
```
API docs available at `http://localhost:8000/docs` (FastAPI auto-generates Swagger UI).

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000`. The Vite dev server proxies `/api/*` to `http://localhost:8000` (see `vite.config.js`).

**Database only, via Docker**
```bash
docker run -d --name traffic-db -p 5432:5432 \
  -e POSTGRES_USER=traffic_user -e POSTGRES_PASSWORD=traffic_pass -e POSTGRES_DB=traffic_db \
  postgres:16-alpine
```

## 2. Full stack via Docker Compose

```bash
cp .env.example .env   # set a real SECRET_KEY
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Postgres: `localhost:5432`

Model artifacts persist in `backend/saved_models/` and raw datasets in `backend/data/` via bind mounts, so retraining survives container restarts.

## 3. AWS deployment (EC2 + S3 + Nginx)

This mirrors what a small production deployment looks like without going all-in on Kubernetes/ECS.

1. **Provision an EC2 instance** (Ubuntu 22.04, t3.medium or larger — DL training is CPU/RAM hungry). Open inbound ports 80/443 (and 22 for SSH) in the security group.
2. **Install Docker + Docker Compose** on the instance:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   sudo apt install -y docker-compose-plugin
   ```
3. **Clone the repo** onto the instance and set `.env` with production secrets (a real `SECRET_KEY`, and a strong Postgres password reflected in both `docker-compose.yml` and `DATABASE_URL`).
4. **Point saved models / datasets at S3** instead of local disk for durability across instance replacement:
   - Create an S3 bucket (`smart-traffic-artifacts`).
   - Give the EC2 instance an IAM role with `s3:GetObject`/`s3:PutObject` on that bucket.
   - Swap the local file writes in `app/ml/train_ml.py` / `train_dl.py` for `boto3` S3 upload calls (the artifact-path fields in the DB already support arbitrary paths/URIs, so this is a localized change).
5. **Run it**: `docker compose up -d --build`.
6. **Put Nginx (or an ALB) in front for TLS**: either terminate TLS at an Application Load Balancer pointed at the EC2 instance, or run Certbot on the instance's Nginx container for free Let's Encrypt certificates.
7. **CI/CD with GitHub Actions**: on push to `main`, build and push Docker images to a registry (ECR or Docker Hub), then SSH into the EC2 instance and run `docker compose pull && docker compose up -d`. A minimal workflow:
   ```yaml
   name: deploy
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Deploy over SSH
           uses: appleboy/ssh-action@v1
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ubuntu
             key: ${{ secrets.EC2_SSH_KEY }}
             script: |
               cd smart-traffic-prediction
               git pull
               docker compose up -d --build
   ```

## 4. Production hardening checklist

- [ ] Real `SECRET_KEY`, rotated periodically, stored in a secrets manager rather than `.env` on disk
- [ ] Postgres backups (automated snapshots if using RDS instead of a container)
- [ ] Move ML/DL training off the request thread (Celery + Redis, or at minimum `BackgroundTasks` + polling endpoint)
- [ ] Rate limiting on `/api/ml/predict` and `/api/dl/predict`
- [ ] Structured logging shipped somewhere queryable (CloudWatch, ELK)
- [ ] HTTPS everywhere; restrict CORS `allow_origins` to your real frontend domain
- [ ] Alembic migrations instead of `Base.metadata.create_all()` for schema changes post-launch
