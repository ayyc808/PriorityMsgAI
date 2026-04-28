# ============================================================
# routes/classify.py — API Endpoint Definitions to classify emergency messasges
# Defines the /classify endpoint that the React frontend calls.
# Receives a message, runs it through the classifier, returns result.
# ============================================================

"""
This will handle:
POST /classify: classify a message and save to database
GET  /messages: get message feed with optional urgency filter
POST /messages/{id}/save: saves a message to saved feeds
POST /messages/{id}/archive: archive a message from feed
GET  /messages/saved: get user's saved messages
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os
from database import get_db, Message, SavedFeed, Notification, User
from classifier import classify_message

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")

router = APIRouter()
security = HTTPBearer()

# Auth helper functions
# Gets and validates the JWT token from request header
# Returns the user_id from the token payload

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    """
    Validate JWT token and return current user's ID.
    Called as a dependency on protected routes.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

#Pydantic Schema

class ClassifyRequest(BaseModel):
    """Request body for POST /classify"""
    text: str


class ClassifyResponse(BaseModel):
    """Response body for POST /classify"""
    message_id:       int
    raw_text:         str
    cleaned_text:     str
    urgency_label:    str
    urgency_score:    float
    category:         str
    roberta_label:    str
    roberta_score:    float
    lr_label:         str
    lr_score:         float
    rf_label:         str
    rf_score:         float
    priority_score:   float
    analyzed_at:      str
    override_applied: bool   # True if Critical override was triggered

# Routes

@router.post("/classify", response_model=ClassifyResponse)
def classify(
    request: ClassifyRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Classify an emergency message using all three models.

    Steps:
    1. Validate input is not empty
    2. Run through classifier.py (preprocess + all 3 models)
    3. Save result to messages table
    4. Auto-create notification if urgency is Critical or High
    5. Return full classification result
    """

    # Validate input
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text cannot be empty"
        )

    # Run classification
    result = classify_message(request.text)

    # Check for classification error
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # Save message to database
    new_message = Message(
        user_id=user_id,
        raw_text=result["raw_text"],
        cleaned_text=result["cleaned_text"],
        urgency_label=result["urgency_label"],
        urgency_score=result["urgency_score"],
        category=result["category"],
        roberta_label=result["roberta_label"],
        roberta_score=result["roberta_score"],
        lr_label=result["lr_label"],
        lr_score=result["lr_score"],
        rf_label=result["rf_label"],
        rf_score=result["rf_score"],
        status="active",
        analyzed_at=datetime.now(timezone.utc),
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Auto-create notification for Critical or High urgency
    # These trigger the bell icon and pulse alerts on the dashboard
    if result["urgency_label"] in ["Critical", "High"]:
        notification_type = (
            "critical_alert" if result["urgency_label"] == "Critical"
            else "pulse"
        )
        notification = Notification(
            user_id=user_id,
            message_id=new_message.id,
            type=notification_type,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notification)
        db.commit()

    return ClassifyResponse(
        message_id=new_message.id,
        raw_text=new_message.raw_text,
        cleaned_text=new_message.cleaned_text,
        urgency_label=new_message.urgency_label,
        urgency_score=new_message.urgency_score,
        category=new_message.category,
        roberta_label=new_message.roberta_label,
        roberta_score=new_message.roberta_score,
        lr_label=new_message.lr_label,
        lr_score=new_message.lr_score,
        rf_label=new_message.rf_label,
        rf_score=new_message.rf_score,
        priority_score=new_message.urgency_score,
        analyzed_at=new_message.analyzed_at.isoformat(),
        override_applied=result.get("override_applied", False),
    )


@router.get("/messages")
def get_messages(
    urgency: str = None,
    status: str = "active",
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get message feed for the current user.
    Optional filter by urgency level (Critical/High/Medium/Low)
    and status (active/saved/archived)
    Messages are sorted by priority score (highest first)
    """

    query = db.query(Message).filter(Message.user_id == user_id)

    # Filter by status
    if status:
        query = query.filter(Message.status == status)

    # Filter by urgency level
    if urgency and urgency in ["Critical", "High", "Medium", "Low"]:
        query = query.filter(Message.urgency_label == urgency)

    # Sort by urgency score descending (Critical first)
    messages = query.order_by(Message.urgency_score.desc()).all()

    return {
        "messages": [
            {
                "id":            m.id,
                "raw_text":      m.raw_text,
                "urgency_label": m.urgency_label,
                "urgency_score": m.urgency_score,
                "category":      m.category,
                "roberta_label": m.roberta_label,
                "roberta_score": m.roberta_score,
                "lr_label":      m.lr_label,
                "lr_score":      m.lr_score,
                "rf_label":      m.rf_label,
                "rf_score":      m.rf_score,
                "status":        m.status,
                "analyzed_at":   m.analyzed_at.isoformat(),
            }
            for m in messages
        ],
        "total": len(messages),
    }


@router.post("/messages/{message_id}/save")
def save_message(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Save a message to the user's saved feed.
    Updates message status to 'saved' and creates a SavedFeed record.
    """

    # Find message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == user_id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check not already saved
    existing = db.query(SavedFeed).filter(
        SavedFeed.user_id == user_id,
        SavedFeed.message_id == message_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message already saved"
        )

    # Update message status
    message.status = "saved"

    # Create saved feed record
    saved = SavedFeed(
        user_id=user_id,
        message_id=message_id,
    )

    db.add(saved)
    db.commit()

    return {"message": "Message saved successfully", "message_id": message_id}


@router.post("/messages/{message_id}/archive")
def archive_message(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Archive a message — hides it from the active feed
    but keeps it in the database for analytics.
    """

    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == user_id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    message.status = "archived"
    db.commit()

    return {"message": "Message archived", "message_id": message_id}


@router.get("/messages/saved")
def get_saved_messages(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all saved messages for the current user.
    Used by the Saved Feeds tab on the dashboard.
    """

    saved_feeds = db.query(SavedFeed).filter(
        SavedFeed.user_id == user_id
    ).all()

    messages = []
    for sf in saved_feeds:
        m = sf.message
        messages.append({
            "id":            m.id,
            "raw_text":      m.raw_text,
            "urgency_label": m.urgency_label,
            "urgency_score": m.urgency_score,
            "category":      m.category,
            "roberta_label": m.roberta_label,
            "roberta_score": m.roberta_score,
            "status":        m.status,
            "saved_at":      sf.saved_at.isoformat(),
            "analyzed_at":   m.analyzed_at.isoformat(),
        })

    return {"saved_messages": messages, "total": len(messages)}