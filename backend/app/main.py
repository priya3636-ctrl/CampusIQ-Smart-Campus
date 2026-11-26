
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env before importing application modules
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routes import maintenance, campus_insights, chat, documents

# DATABASE INITIALIZATION
with engine.begin() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

Base.metadata.create_all(bind=engine)

# FASTAPI APPLICATION
app = FastAPI(
    title="CampusIQ API",
    description="Smart Campus Management System",
    version="1.0.0"
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# REGISTER API ROUTES
app.include_router(maintenance.router)
app.include_router(campus_insights.router)
app.include_router(chat.router)
app.include_router(documents.router)

# HEALTH CHECK
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "initialized",
        "project": "CampusIQ"
    }

# SERVE FRONTEND
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"

app.mount(
    "/",
    StaticFiles(directory=str(frontend_dir), html=True),
    name="frontend"
)
