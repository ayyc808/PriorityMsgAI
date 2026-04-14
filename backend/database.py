# Database models and configuration (The SQLAlchemy models + setup)

"""
PriorityMsgAI — database.py
SQLAlchemy ORM models + SQLite engine setup.
 
Place this file at: backend/database.py
Then import from other backend files like:
    from database import Base, engine, SessionLocal, User, Message, SavedFeed, Notification
"""
 
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
 
# ---------------------------------------------------------------------------
# Engine + session
# ---------------------------------------------------------------------------
 
DATABASE_URL = "sqlite:///./prioritymsgai.db"
 
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)
 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
Base = declarative_base()
 
 
# ---------------------------------------------------------------------------
# Dependency — use in FastAPI route handlers
# ---------------------------------------------------------------------------
 
def get_db():
    """Yield a database session and close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
 
class User(Base):
    """Registered user account."""
    __tablename__ = "users"
 
    id                  = Column(Integer, primary_key=True, index=True)
    first_name          = Column(String(50),  nullable=False)
    middle_name         = Column(String(50),  nullable=True)
    last_name           = Column(String(50),  nullable=False)
    email               = Column(String(120), unique=True, nullable=False, index=True)
    password_hash       = Column(String(255), nullable=False)   # bcrypt hash
    organization        = Column(String(100), nullable=True)    # Police / Fire / EMS / Analyst …
    role                = Column(String(80),  nullable=True)    # Dispatcher / Analyst …
 
    # Settings / preferences
    model_preference    = Column(String(20),  nullable=False, default="roberta")  # 'roberta' | 'all'
    theme               = Column(String(10),  nullable=False, default="light")    # 'light' | 'dark'
    notif_urgency_alerts = Column(Boolean,    nullable=False, default=True)
    notif_sound         = Column(Boolean,     nullable=False, default=True)
 
    created_at          = Column(DateTime, default=lambda: datetime.now(timezone.utc))
 
    # Relationships
    messages            = relationship("Message",      back_populates="user", cascade="all, delete-orphan")
    saved_feeds         = relationship("SavedFeed",    back_populates="user", cascade="all, delete-orphan")
    notifications       = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"
 
 
class Message(Base):
    """
    A single message submitted via '+ Add Message'.
    Stores both the raw input and every model's classification output.
    """
    __tablename__ = "messages"
 
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
 
    # Text
    raw_text        = Column(Text, nullable=False)   # original user input, unmodified
    cleaned_text    = Column(Text, nullable=True)    # output of preprocess.py
 
    # Primary classification result (from RoBERTa)
    urgency_label   = Column(String(10),  nullable=True)   # critical | high | medium | low
    urgency_score   = Column(Float,       nullable=True)   # 0.0 – 1.0
    category        = Column(String(60),  nullable=True)   # Fire | Flood | Medical | Collapse, etc
 
    # Per-model breakdown
    roberta_label   = Column(String(10),  nullable=True)
    roberta_score   = Column(Float,       nullable=True)
    lr_label        = Column(String(10),  nullable=True)
    lr_score        = Column(Float,       nullable=True)
    rf_label        = Column(String(10),  nullable=True)
    rf_score        = Column(Float,       nullable=True)
 
    # Optional location (extracted from text or user-entered)
    location        = Column(String(200), nullable=True)
 
    # Lifecycle state
    status          = Column(String(20),  nullable=False, default="active")
    # 'active'   → visible on dashboard feed
    # 'saved'    → pinned / saved by user (also appears in saved_feeds)
    # 'archived' → hidden from feed, not deleted
 
    analyzed_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
 
    # Relationships
    user            = relationship("User",         back_populates="messages")
    saved_by        = relationship("SavedFeed",    back_populates="message", cascade="all, delete-orphan")
    notifications   = relationship("Notification", back_populates="message", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Message id={self.id} urgency={self.urgency_label!r} score={self.urgency_score}>"
 
 
class SavedFeed(Base):
    """
    Join table: a user saves a message to their Saved Feed.
    A message can be saved by the same user once (unique constraint).
    """
    __tablename__ = "saved_feeds"
 
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)
    message_id  = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    saved_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    note        = Column(Text, nullable=True)   # optional dispatcher annotation
 
    # Relationships
    user        = relationship("User",    back_populates="saved_feeds")
    message     = relationship("Message", back_populates="saved_by")
 
    def __repr__(self):
        return f"<SavedFeed user={self.user_id} message={self.message_id}>"
 
 
class Notification(Base):
    """
    Bell-icon alerts.
    Auto-created when a message scores 'critical' or 'high'.
    """
    __tablename__ = "notifications"
 
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)
    message_id  = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    type        = Column(String(20), nullable=False)   # 'pulse' | 'critical_alert'
    is_read     = Column(Boolean,    nullable=False, default=False)
    created_at  = Column(DateTime,   default=lambda: datetime.now(timezone.utc))
 
    # Relationships
    user        = relationship("User",    back_populates="notifications")
    message     = relationship("Message", back_populates="notifications")
 
    def __repr__(self):
        return f"<Notification id={self.id} type={self.type!r} read={self.is_read}>"
 
 
# ---------------------------------------------------------------------------
# Create all tables (to call once on app startup)
# ---------------------------------------------------------------------------
 
def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)
 
 
if __name__ == "__main__":
    init_db()
    print("Database initialized — prioritymsgai.db created.")
 


