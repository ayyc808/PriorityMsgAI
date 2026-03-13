# ============================================================
# main.py — FastAPI App Entry Point
# This is where the backend server starts.
# All routes are registered here and the app is launched.
# Run with: uvicorn main:app --reload
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.classify import router as classify_router

app = FastAPI(
    title="PriorityMsgAI",
    description="AI-powered emergency message prioritization system",
    version="1.0.0"
)

# Allow React frontend (localhost:3000) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(classify_router)

@app.get("/")
def root():
    return {"message": "PriorityMsgAI backend is running"}
