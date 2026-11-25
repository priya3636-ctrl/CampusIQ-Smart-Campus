
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routes import maintenance, campus_insights, chat, documents

# DATABASE INITIALIZATION
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

@app.get("/")
def home():
    return {
        "project": "CampusIQ",
        "message": "Smart Campus Management Backend",
        "status": "Running successfully"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "initialized",
        "project": "CampusIQ"
    }
