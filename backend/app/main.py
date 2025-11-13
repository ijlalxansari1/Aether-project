"""
AETHER Insight Platform - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.routers import ingestion, data_processing, eda, ml_pipeline, fairness, dashboard, auth, ethical, story, report, faq as faq_router
from app.database import engine, Base

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AETHER Insight Platform",
    description="Unified analytics, ML, and ethical AI platform",
    version="1.0.0"
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Data Ingestion"])
app.include_router(data_processing.router, prefix="/api/data-processing", tags=["Data Processing"])
app.include_router(eda.router, prefix="/api/eda", tags=["EDA"])
app.include_router(ml_pipeline.router, prefix="/api/ml", tags=["ML Pipeline"])
app.include_router(fairness.router, prefix="/api/fairness", tags=["Fairness & Explainability"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(ethical.router, prefix="/api/ethics", tags=["Ethical Analysis"])
app.include_router(story.router, prefix="/api/story", tags=["Story Mode"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])
app.include_router(faq_router.router, prefix="/api/info", tags=["FAQ & Glossary"])


@app.get("/")
async def root():
    return {
        "message": "AETHER Insight Platform API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "aether-insight-platform"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

    if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Railway injects PORT automatically
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)


