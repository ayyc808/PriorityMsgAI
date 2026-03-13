# ============================================================
# routes/classify.py — API Endpoint Definitions
# Defines the /classify endpoint that the React frontend calls.
# Receives a message, runs it through the classifier, returns result.
# ============================================================

from fastapi import APIRouter
from pydantic import BaseModel
from classifier import classify_message
from utils.preprocess import clean_text
import uuid
from datetime import datetime

router = APIRouter()

# Defines the shape of the incoming request from the frontend
class MessageRequest(BaseModel):
    text: str
    source: str  # "SMS", "Social Media", "Email", "Voice"

# Defines the shape of the response sent back to the frontend
class MessageResponse(BaseModel):
    id: str
    text: str
    source: str
    urgency_level: str
    emergency_type: str
    urgency_score: float
    timestamp: str

@router.post("/classify", response_model=MessageResponse)
def classify(request: MessageRequest):
    """
    Receives a message from the frontend.
    Cleans it, classifies it, and returns the prioritized result.
    """

    # Step 1: Clean the incoming text
    cleaned = clean_text(request.text)

    # Step 2: Run through the AI classifier
    result = classify_message(cleaned)

    # Step 3: Return the full response
    return MessageResponse(
        id=str(uuid.uuid4()),
        text=request.text,
        source=request.source,
        urgency_level=result["urgency_level"],
        emergency_type=result["emergency_type"],
        urgency_score=result["urgency_score"],
        timestamp=datetime.now().isoformat()
    )
