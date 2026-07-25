"""
Application entry point. Run with:
    uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import auth, datasets, ml, dl, routing, dashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creates tables if they don't exist yet. For real migrations, use Alembic instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="ML/DL powered traffic congestion & accident-risk prediction system with route recommendation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(ml.router)
app.include_router(dl.router)
app.include_router(routing.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.error(f"Unhandled error on {request.url}: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
