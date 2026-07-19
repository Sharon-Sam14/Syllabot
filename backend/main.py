from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.api.v1 import auth, syllabi, plans, progress
from backend.ai import router as ai_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Adaptive study planner API engine - Google Maps for your syllabus",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS configuration (essential for frontend-backend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)
app.include_router(
    syllabi.router,
    prefix=f"{settings.API_V1_STR}/syllabi",
    tags=["Syllabi Ingestion"]
)
app.include_router(
    plans.router,
    prefix=f"{settings.API_V1_STR}/plans",
    tags=["Study Plans"]
)
app.include_router(
    progress.router,
    prefix=f"{settings.API_V1_STR}/progress",
    tags=["Daily Progress & Tracking"]
)
app.include_router(
    ai_router.router,
    prefix=f"{settings.API_V1_STR}/ai",
    tags=["AI Study Assistant"]
)


@app.get("/", tags=["Health Check"])
def root():
    """
    Root endpoint serving basic health-check information.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }
