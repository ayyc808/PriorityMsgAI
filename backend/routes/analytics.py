"""
RapidRelief — routes/analytics.py
This provides the analytics data for the frontend Analytics page UI.

All endpoints require JWT authentication.
Data is derived from the messages table in the database.

Handles:
    1. GET /analytics/overview:  summary stats (total, by urgency, by category)
    2. GET /analytics/urgency-distribution: urgency breakdown for circle/bar chart (visually, how many crit vs low alerts day to day)
    3. GET /analytics/message-trends: message volume over time for line chart (can we derive or see patterns overtime)
    4. GET /analytics/model-performance: accuracy comparison across all three models (RoBERTa vs LR vs RF to draw conclusions)
    5. GET /analytics/confidence-distribution: confidence score histogram on predictions (are they high or uncertain?)
    6. GET /analytics/category-breakdown: emergency type breakdown and which emergencies dominate  (Fire? Medical?)
    7. GET /analytics/recent-activity: last 10 messages for activity feed and the data coming in for situations of what needs immediate attention
    
    Later, may add GET /analytics/false-positive-rate for how often critical msg are flagged and downgraded by human review
    Later may add GET /analyticss/peak-hours for what times of day have the highest alert volume
    LAter may add GET /analytics/model-disagreement for the messages where all 3 models conflict/disagree the most
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from database import get_db, Message
from routes.classify import get_current_user_id

router = APIRouter()

# ---------------------------------------------------------------------------
# 7 Routes for now for analytics page
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1.
@router.get("/analytics/overview")
def get_overview(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    High level summary stats for the analytics dashboard.
    Returns total messages, breakdown by urgency and category.
    """

    # Get all messages for this user
    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).all()

    total = len(messages)

    if total == 0:
        return {
            "total_messages": 0,
            "urgency_counts": {},
            "category_counts": {},
            "avg_confidence": 0,
        }

    # Count by urgency level
    urgency_counts = defaultdict(int)
    for m in messages:
        urgency_counts[m.urgency_label] += 1

    # Count by category
    category_counts = defaultdict(int)
    for m in messages:
        category_counts[m.category] += 1

    # Average RoBERTa confidence score
    avg_confidence = sum(m.urgency_score for m in messages) / total

    return {
        "total_messages":  total,
        "urgency_counts":  dict(urgency_counts),
        "category_counts": dict(category_counts),
        "avg_confidence":  round(avg_confidence, 4),
    }

# ---------------------------------------------------------------------------
#2.
@router.get("/analytics/urgency-distribution")
def get_urgency_distribution(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Urgency level distribution for donut/bar chart.
    Returns counts and percentages for each urgency level.
    """

    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).all()

    total = len(messages)

    if total == 0:
        return {"distribution": [], "total": 0}

    # Count each urgency level
    counts = defaultdict(int)
    for m in messages:
        counts[m.urgency_label] += 1

    # Build distribution with percentages and colors
    urgency_colors = {
        "Critical": "#E24B4A",
        "High":     "#EF9F27",
        "Medium":   "#c9b800",
        "Low":      "#639922",
    }

    distribution = []
    for level in ["Critical", "High", "Medium", "Low"]:
        count = counts.get(level, 0)
        distribution.append({
            "urgency_label": level,
            "count":         count,
            "percentage":    round(count / total * 100, 1),
            "color":         urgency_colors.get(level, "#888"),
        })

    return {"distribution": distribution, "total": total}

# ---------------------------------------------------------------------------
# 3. 
@router.get("/analytics/message-trends")
def get_message_trends(
    days: int = 7,              # default last 7 days
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Message volume over time for line chart.
    Returns daily counts for the last N days.
    days parameter controls the time window (default 7, max 30)
    """

    # Cap at 30 days to prevent excessive data
    days = min(days, 30)

    # Calculate start date
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Get messages within the time window
    messages = db.query(Message).filter(
        Message.user_id == user_id,
        Message.analyzed_at >= start_date
    ).all()

    # Group by date
    daily_counts = defaultdict(lambda: defaultdict(int))
    for m in messages:
        date_str = m.analyzed_at.strftime("%Y-%m-%d")
        daily_counts[date_str]["total"] += 1
        daily_counts[date_str][m.urgency_label] += 1

    # Build ordered list for all days in range
    trends = []
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days-1-i))
        date_str = date.strftime("%Y-%m-%d")
        day_data = daily_counts.get(date_str, {})
        trends.append({
            "date":     date_str,
            "total":    day_data.get("total", 0),
            "critical": day_data.get("Critical", 0),
            "high":     day_data.get("High", 0),
            "medium":   day_data.get("Medium", 0),
            "low":      day_data.get("Low", 0),
        })

    return {"trends": trends, "days": days}

# ---------------------------------------------------------------------------
# 4. 
@router.get("/analytics/model-performance")
def get_model_performance(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Model agreement and confidence comparison.
    Shows how often each model agrees with RoBERTa
    and average confidence scores per model.
    Used for the model performance bar chart.
    """

    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).all()

    total = len(messages)

    if total == 0:
        return {"model_performance": [], "total": 0}

    # Count agreements with RoBERTa (primary model)
    lr_agrees  = sum(1 for m in messages if m.lr_label == m.roberta_label)
    rf_agrees  = sum(1 for m in messages if m.rf_label == m.roberta_label)

    # Average confidence scores per model
    avg_roberta = sum(m.roberta_score for m in messages) / total
    avg_lr      = sum(m.lr_score for m in messages) / total
    avg_rf      = sum(m.rf_score for m in messages) / total

    return {
        "model_performance": [
            {
                "model":             "RoBERTa",
                "avg_confidence":    round(avg_roberta, 4),
                "agreement_rate":    1.0,        # baseline — compares against itself
                "color":             "#E24B4A",
            },
            {
                "model":             "Logistic Regression",
                "avg_confidence":    round(avg_lr, 4),
                "agreement_rate":    round(lr_agrees / total, 4),
                "color":             "#378ADD",
            },
            {
                "model":             "Random Forest",
                "avg_confidence":    round(avg_rf, 4),
                "agreement_rate":    round(rf_agrees / total, 4),
                "color":             "#1D9E75",
            },
        ],
        "total": total,
    }

# ---------------------------------------------------------------------------
# 5. 
@router.get("/analytics/confidence-distribution")
def get_confidence_distribution(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    RoBERTa confidence score distribution for histogram.
    Buckets scores into ranges (0-0.1, 0.1-0.2, etc.)
    """

    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).all()

    if not messages:
        return {"buckets": [], "total": 0}

    # Create 10 buckets from 0.0 to 1.0
    buckets = defaultdict(int)
    for m in messages:
        # Round down to nearest 0.1
        bucket = round(int(m.urgency_score * 10) / 10, 1)
        bucket = min(bucket, 0.9)   # cap at 0.9 (last bucket is 0.9-1.0)
        buckets[bucket] += 1

    # Build ordered list
    distribution = []
    for i in range(10):
        lower = round(i * 0.1, 1)
        upper = round((i + 1) * 0.1, 1)
        distribution.append({
            "range":  f"{lower}-{upper}",
            "lower":  lower,
            "upper":  upper,
            "count":  buckets.get(lower, 0),
        })

    return {
        "buckets": distribution,
        "total":   len(messages),
        "avg":     round(sum(m.urgency_score for m in messages) / len(messages), 4),
    }

# ---------------------------------------------------------------------------
# 6. 
@router.get("/analytics/category-breakdown")
def get_category_breakdown(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Emergency category breakdown.
    Shows distribution of Fire, Flood, Medical, Collapse etc.
    """

    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).all()

    total = len(messages)

    if total == 0:
        return {"categories": [], "total": 0}

    counts = defaultdict(int)
    for m in messages:
        counts[m.category] += 1

    categories = [
        {
            "category":   cat,
            "count":      count,
            "percentage": round(count / total * 100, 1),
        }
        for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {"categories": categories, "total": total}

# ---------------------------------------------------------------------------
# 7. 
@router.get("/analytics/recent-activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Most recent messages for the activity feed.
    Returns last N messages sorted by analyzed_at descending.
    """

    # Cap limit at 50
    limit = min(limit, 50)

    messages = db.query(Message).filter(
        Message.user_id == user_id
    ).order_by(
        Message.analyzed_at.desc()
    ).limit(limit).all()

    return {
        "recent": [
            {
                "id":            m.id,
                "raw_text":      m.raw_text[:100],  # truncate for display
                "urgency_label": m.urgency_label,
                "urgency_score": m.urgency_score,
                "category":      m.category,
                "status":        m.status,
                "analyzed_at":   m.analyzed_at.isoformat(),
            }
            for m in messages
        ],
        "total": len(messages),
    }