"""
OTP service — generates, stores, and verifies 6-digit one-time passwords.
Uses the app cache (Redis when available, in-memory NoopCache as fallback).
"""

import secrets
from loguru import logger

from app.core.cache import cache

_OTP_TTL = 600        # 10 minutes
_MAX_ATTEMPTS = 5     # max wrong guesses before the OTP is invalidated
_RESEND_COOLDOWN = 60  # seconds between resend requests


def _otp_key(email: str) -> str:
    return f"otp:{email.lower()}"

def _attempts_key(email: str) -> str:
    return f"otp_attempts:{email.lower()}"

def _resend_key(email: str) -> str:
    return f"otp_resend:{email.lower()}"


def generate_and_store_otp(email: str) -> str:
    """Generate a 6-digit OTP, store it in cache, return it."""
    otp = str(secrets.randbelow(1_000_000)).zfill(6)
    cache.set(_otp_key(email), otp, ex=_OTP_TTL)
    # Reset attempt counter
    cache.set(_attempts_key(email), "0", ex=_OTP_TTL + 60)
    logger.debug("OTP generated for {}", email)
    return otp


def verify_otp(email: str, otp: str) -> tuple[bool, str]:
    """
    Verify the OTP for an email address.

    Returns (success: bool, message: str).
    On success the OTP is deleted so it can't be reused.
    """
    stored = cache.get(_otp_key(email))
    if stored is None:
        return False, "OTP has expired. Please request a new one."

    # Track failed attempts
    raw_attempts = cache.get(_attempts_key(email)) or "0"
    attempts = int(raw_attempts)

    if attempts >= _MAX_ATTEMPTS:
        cache.delete(_otp_key(email))
        cache.delete(_attempts_key(email))
        return False, "Too many incorrect attempts. Please request a new OTP."

    if otp.strip() != stored.strip():
        cache.set(_attempts_key(email), str(attempts + 1), ex=_OTP_TTL + 60)
        remaining = _MAX_ATTEMPTS - attempts - 1
        return False, f"Incorrect OTP. {remaining} attempt(s) remaining."

    # Correct — delete OTP so it's single-use
    cache.delete(_otp_key(email))
    cache.delete(_attempts_key(email))
    return True, "OTP verified successfully."


def can_resend(email: str) -> tuple[bool, int]:
    """
    Check if a resend is allowed (cooldown).
    Returns (allowed: bool, seconds_to_wait: int).
    """
    val = cache.get(_resend_key(email))
    if val is None:
        return True, 0
    # NoopCache doesn't track TTL so we can't compute wait time precisely
    return False, _RESEND_COOLDOWN


def mark_resend(email: str) -> None:
    cache.set(_resend_key(email), "1", ex=_RESEND_COOLDOWN)
