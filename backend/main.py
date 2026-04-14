"""
The brain/core of the app
Handles/initializes/builds FastAPI, CORS, and connects to database on startup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="RapidRelief API",
    description="AI-powered emergency message triage system",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS middleware
# Allows the React frontend (localhost:5173 is Vite's default port)
# to make requests to this backend without being blocked by the browser.
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # fallback if using CRA
    ],
    allow_credentials=True,
    allow_methods=["*"],           # allow GET, POST, PATCH, DELETE etc.
    allow_headers=["*"],           # allow Authorization, Content-Type etc.
)

# ---------------------------------------------------------------------------
# Startup event
# Runs once when the server boots.
# Creates all database tables if they don't already exist.
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    print("Starting RapidRelief API...")
    init_db()
    print("Database ready.")


# ---------------------------------------------------------------------------
# Health check route
# Testing GET / and confirming server is alive.
# http://127.0.0.1:8000/ in browser/Postman.
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "app": "RapidRelief",
        "status": "online",
        "version": "1.0.0",
    }


# ---------------------------------------------------------------------------
# Future routers to be added here later
# ---------------------------------------------------------------------------