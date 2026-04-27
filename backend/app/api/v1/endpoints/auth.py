"""Auth endpoints — register with email OTP verification, login, token refresh."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.email_service import send_otp_email
from app.core.otp_service import (
    can_resend,
    generate_and_store_otp,
    mark_resend,
    verify_otp,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    OTPVerifyRequest,
    RegisterResponse,
    ResendOTPRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter()
settings = get_settings()
security = HTTPBearer()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new account.

    - Validates email format and password strength (8+ chars, 1 uppercase, 1 special char)
    - Creates an unverified user record
    - Generates a 6-digit OTP (valid 10 min) and emails it
    - In dev mode (no SMTP configured): OTP is returned in `dev_otp` field
    """
    # Duplicate check
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Create user — NOT verified yet
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        risk_tolerance=user_in.risk_tolerance,
        investment_horizon=user_in.investment_horizon,
        initial_investment=user_in.initial_investment,
        monthly_contribution=user_in.monthly_contribution,
        preferred_assets=user_in.preferred_assets,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate OTP
    otp = generate_and_store_otp(user_in.email)
    mark_resend(user_in.email)  # start cooldown
    email_sent = await send_otp_email(user_in.email, user_in.full_name, otp)

    dev_otp = None if email_sent else otp   # expose only in dev mode

    return RegisterResponse(
        message=(
            f"Verification code sent to {user_in.email}. Please check your inbox."
            if email_sent
            else "Account created. Enter the OTP shown below to verify your email."
        ),
        email=user_in.email,
        dev_otp=dev_otp,
    )


# ---------------------------------------------------------------------------
# Verify OTP
# ---------------------------------------------------------------------------

@router.post("/verify-otp", response_model=Token)
async def verify_email_otp(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Verify the 6-digit OTP and activate the account.
    Returns JWT access + refresh tokens on success (user is auto-logged in).
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified. Please log in.",
        )

    ok, msg = verify_otp(str(body.email), body.otp)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    # Mark user as verified
    user.is_verified = True
    await db.commit()

    # Auto-login — return tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Resend OTP
# ---------------------------------------------------------------------------

@router.post("/resend-otp", response_model=RegisterResponse)
async def resend_otp(
    body: ResendOTPRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Resend a fresh OTP to the registered email (60-second cooldown between requests).
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified.",
        )

    allowed, wait = can_resend(str(body.email))
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {wait} seconds before requesting a new OTP.",
        )

    otp = generate_and_store_otp(str(body.email))
    mark_resend(str(body.email))
    email_sent = await send_otp_email(str(body.email), user.full_name, otp)

    return RegisterResponse(
        message=(
            f"New OTP sent to {body.email}."
            if email_sent
            else "New OTP generated. Enter the code shown below."
        ),
        email=str(body.email),
        dev_otp=None if email_sent else otp,
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Authenticate user. Requires email to be OTP-verified first."""
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please complete OTP verification first.",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Token refresh & me
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPBearer = Depends(security),
) -> Any:
    """Refresh access token using a valid refresh token."""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh = create_refresh_token(data={"sub": str(user_id)})

    return {"access_token": access_token, "refresh_token": new_refresh, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get currently authenticated user."""
    return current_user
