from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.auth import get_password_hash, verify_password, create_access_token
from database.connection import get_db
from database.models import User


def _hash_password(password: str) -> str:
    return get_password_hash(password)


def _verify_password(plain_password: str, stored_password: str) -> bool:
    return verify_password(plain_password, stored_password)


def _create_access_token(data: dict) -> str:
    return create_access_token(data)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return the first user matching an email address."""
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Return the first user matching a UUID identifier."""
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, username: str, email: str, password: str) -> User:
    """Create a new user after validating uniqueness and storing the password."""
    normalized_email = email.lower().strip()
    existing_user = get_user_by_email(db, normalized_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with that email already exists.",
        )

    stored_password = _hash_password(password)
    user = User(username=username.strip(), email=normalized_email, password=stored_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify email and password credentials."""
    user = get_user_by_email(db, email)
    if not user or not _verify_password(password, user.password):
        return None
    return user


def create_access_token_for_user(user: User) -> str:
    """Create a JWT token for an authenticated user."""
    return _create_access_token({"sub": user.id, "email": user.email})


def update_user(db: Session, user: User, email: str | None = None, password: str | None = None) -> User:
    """Update the user's email and/or password."""
    if email is not None:
        normalized_email = email.lower().strip()
        if normalized_email != user.email:
            existing_user = get_user_by_email(db, normalized_email)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with that email already exists.",
                )
            user.email = normalized_email

    if password is not None:
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long.",
            )
        user.password = _hash_password(password)

    db.commit()
    db.refresh(user)
    return user


def reset_password_for_email(db: Session, email: str, new_password: str) -> User:
    """Reset password for a user by email."""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for that email.",
        )
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long.",
        )

    user.password = _hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
