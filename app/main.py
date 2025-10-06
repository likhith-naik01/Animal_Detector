from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import analysis, projects, batch, species, realtime

app = FastAPI(title="TrailGuard AI", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(batch.router, prefix="/api")
app.include_router(species.router, prefix="/api")
app.include_router(realtime.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and load models on startup"""
    from app.db.session import create_tables
    from app.pipeline.image_processor import image_processor_singleton
    
    create_tables()
    print("Database tables created/verified")
    
    # Load YOLO model at startup
    image_processor_singleton()
    print("Animal detection model loaded and ready")