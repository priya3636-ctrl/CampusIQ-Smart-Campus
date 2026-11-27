# CampusIQ – Smart Campus Management System

An AI-powered platform for smarter campus operations.

## Live Demo
https://campus-iq-smart-campus.vercel.app

## GitHub Repository
https://github.com/priya3636-ctrl/CampusIQ-Smart-Campus

## About
CampusIQ helps educational institutions manage maintenance requests, analyze campus resources, understand student feedback, and support administrative decisions using AI.

## Features

- Overview Dashboard – Campus statistics and summaries.
- AI Assistant – Campus question answering using RAG.
- Maintenance Management – Submit, prioritize, and track complaints.
- AI Agent Center – Six specialized campus analysis agents.
- Reports & Insights – View campus analysis and recommendations.

## AI Agents

1. Student Feedback Agent
2. Resource Management Agent
3. Energy Analysis Agent
4. Scheduling Agent
5. Administration Agent
6. Maintenance Agent

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: PostgreSQL, Neon
- AI Integration: Groq API
- Deployment: Vercel
- Version Control: Git and GitHub

## Local Setup

Clone the repository:

    git clone https://github.com/priya3636-ctrl/CampusIQ-Smart-Campus.git

Install backend dependencies:

    cd CampusIQ-Smart-Campus
    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Configure your required environment variables, including DATABASE_URL and API credentials, in a local .env file.

Start the backend:

    python -m uvicorn app.main:app --reload

API documentation: http://127.0.0.1:8000/docs

## Future Enhancements

- Role-based access control.
- More advanced campus analytics.
- Expanded AI-powered recommendations.

---
CampusIQ – Making Campus Management Smarter with AI.
