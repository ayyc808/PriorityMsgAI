# Authentication routes (login/register endpoints)

"""
RapidRelief — routes/auth.py
Authentication routes for user registration and login.
Handles:
    POST /auth/register  — create a new user account
    POST /auth/login     — login and receive a JWT token
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from pydantic import BaseModel, EmailStr, field_validator
from dotenv import load_dotenv
import bcrypt as bcrypt_lib  # using bcrypt directly (passlib incompatible with bcrypt 4.x)
import os
import re

from database import get_db, User

# ---------------------------------------------------------------------------
# Load environment variables from backend/.env
# ---------------------------------------------------------------------------

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# ---------------------------------------------------------------------------
# Router instance
# All routes in this file will be prefixed with /auth in main.py
# ---------------------------------------------------------------------------

router = APIRouter()

# ---------------------------------------------------------------------------
# Password hashing
# Using bcrypt directly since passlib is incompatible with bcrypt >= 4.0
# Passwords are encoded to bytes before hashing — bcrypt requires bytes not strings
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt. Returns a string for DB storage."""
    password_bytes = password.encode("utf-8")       # bcrypt requires bytes
    salt = bcrypt_lib.gensalt()                      # auto-generates a random salt
    hashed = bcrypt_lib.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")                    # store as string in DB


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt_lib.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )


# ---------------------------------------------------------------------------
# JWT token creation
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token containing the given data payload.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Pydantic schemas
# These define and validate the shape of request bodies.
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Expected request body for POST /auth/register"""
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str
    organization: str | None = None
    role: str | None = None
    access_code: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def names_must_be_letters_only(cls, v):
        """Reject names containing numbers or special characters."""
        if not re.match(r"^[A-Za-z\s\-']+$", v):
            raise ValueError("Name must contain letters only")
        if len(v) > 50:
            raise ValueError("Name must be 50 characters or less")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v):
        """Enforce minimum password security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("access_code")
    @classmethod
    def access_code_not_supported(cls, v):
        """
        Access code feature is not yet implemented.
        If any code is entered, return an error.
        """
        if v and v.strip():
            raise ValueError("Access codes are not supported yet. Leave this field empty.")
        return v


class LoginRequest(BaseModel):
    """Expected request body for POST /auth/login"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response body returned after successful login."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    first_name: str
    last_name: str
    organization: str | None
    role: str | None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Validates:
    - Passwords match
    - Email is not already in use
    - Name fields contain only letters
    - Password meets security requirements
    - Access code is empty (not yet supported)
    """

    # Check passwords match
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Check for duplicate email (case-insensitive)
    existing_user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Create new user record
    new_user = User(
        first_name=request.first_name,
        middle_name=request.middle_name,
        last_name=request.last_name,
        email=request.email.lower(),        # always store email lowercase
        password_hash=hash_password(request.password),
        organization=request.organization,
        role=request.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Account created successfully. Please log in.",
        "user_id": new_user.id,
    }


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    Returns a JWT token on success.
    Frontend stores this token and sends it with every
    subsequent request in the Authorization header.
    """

    # Look up user by email
    user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    # If user not found or password wrong, return the same vague error message
    # Never reveal which one failed — security best practice
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create JWT token with user id as the subject
    token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role=user.role,
    )