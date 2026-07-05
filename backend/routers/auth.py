import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.connection import get_db
from database.auth import decode_access_token
from services.auth_service import (
    authenticate_user,
    create_access_token_for_user,
    get_user_by_id,
    register_user,
    reset_password_for_email,
    update_user,
)

logger = logging.getLogger("uvicorn.error")
from models.auth_schemas import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate, ForgotPasswordRequest

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserResponse:
    """Decode a token and return the current authenticated user."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return UserResponse.from_orm(user)


@router.post("/register", response_model=dict)
async def register_endpoint(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return a success message."""
    try:
        if not user_create.username.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required.")

        if len(user_create.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long.",
            )

        register_user(db, user_create.username, user_create.email, user_create.password)
        return {"message": "Registration successful. You may now log in."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Register endpoint failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register due to server error.",
        )


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate an existing user and return a JWT token."""
    try:
        user = authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token_for_user(user)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.from_orm(user),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Login endpoint failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to login due to server error.",
        )


@router.post("/forgot-password", response_model=dict)
async def forgot_password_endpoint(
    forgot_request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset a user's password when they forget it."""
    reset_password_for_email(db, forgot_request.email, forgot_request.new_password)
    return {"message": "Password reset successful. You may now log in with your new password."}


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """Return current authenticated user data."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me_endpoint(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile email and password."""
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    updated_user = update_user(db, user, email=user_update.email, password=user_update.password)
    return UserResponse.from_orm(updated_user)


@router.post("/logout", response_model=dict)
async def logout_endpoint() -> dict:
    """Logout is handled client side by deleting the JWT token."""
    return {"message": "Logout successful. Remove token from client storage."}
