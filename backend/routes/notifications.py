"""
RapidRelief — routes/notifications.py
Handles notification retrieval and marking as read.

Notifications get auto-created in routes/classify.py when
a message is classified as Critical or High urgency.

Handles:
GET   /notifications: get all notifications for current user
PATCH /notifications/{id}/read: mark a notification as read
PATCH /notifications/read-all: mark all notifications as read
GET   /notifications/unread-count: get count of unread notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os
from database import get_db, Notification, Message
from routes.classify import get_current_user_id         # reuseing auth helper from classify.py

load_dotenv()

router   = APIRouter()
security = HTTPBearer()     # expecitng the "Authorization: Bearer <token>" header


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)     # validates JWT and gets user id
):
    """
    Get all notifications for the current user.
    Returns most recent first.
    Includes the associated message details for display.
    """

    # Query all notifications for this user starting with newest first
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()

    return {
        "notifications": [
            {
                "id":            n.id,
                "type":          n.type,        # crit alert or pulse alert
                "is_read":       n.is_read,     # False = unread and shows the badge on a bell icon
                "created_at":    n.created_at.isoformat(),
                # Includes associated message details so frontend can display what triggered the notification
                "message": {
                    "id":            n.message.id,
                    "raw_text":      n.message.raw_text,
                    "urgency_label": n.message.urgency_label,
                    "urgency_score": n.message.urgency_score,
                    "category":      n.message.category,
                    "analyzed_at":   n.message.analyzed_at.isoformat(),
                }
            }
            for n in notifications
        ],
        "total":  len(notifications),
        # unread count drives the red badge # on the bell icon
        "unread": sum(1 for n in notifications if not n.is_read),
    }


@router.get("/notifications/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get count of unread notifications.
    Used by the bell icon badge on the dashboard.
    """

    # Count only unread notifications for this user
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False       # only counts the unread ones
    ).count()

    return {"unread_count": count}


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,                   # the notification ID from the URL path
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark a single notification as read.
    Called when user clicks on a notification.
    """

    # Find notification — must belong to current user
    # Prevents users from marking other users' notifications as read
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id         # security check for own notif only
    ).first()

    # Returns 404 if not found or does not belong to uer
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # MArk as read and save to db
    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read", "id": notification_id}


@router.patch("/notifications/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark all notifications as read.
    Called when user clicks 'Mark all as read' on the dashboard.
    """

    # get all unread notif for this user
    updated = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False           # only targets unread ones
    ).all()

    # Marks each one as read
    for notification in updated:
        notification.is_read = True

    # single commit for all updates (more efficient than commiting one by one)
    db.commit()

    return {
        "message": f"Marked {len(updated)} notifications as read",
        "count": len(updated)           # tells the frontend how many were updated
    }