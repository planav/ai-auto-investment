"""
Email service — sends OTP emails via SMTP.
Falls back to dev-mode (OTP returned in API response) when SMTP is not configured.
"""

import asyncio
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from app.core.config import get_settings

settings = get_settings()


def _otp_html(otp: str, full_name: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #0A0A0F; color: #E5E7EB; margin: 0; padding: 0; }}
    .container {{ max-width: 480px; margin: 40px auto; background: #111827; border-radius: 16px; overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #00D4AA, #7B61FF); padding: 32px; text-align: center; }}
    .header h1 {{ margin: 0; color: #fff; font-size: 28px; letter-spacing: -0.5px; }}
    .body {{ padding: 32px; }}
    .otp-box {{ background: #0A0A0F; border: 2px solid #00D4AA; border-radius: 12px;
                text-align: center; padding: 24px; margin: 24px 0; }}
    .otp {{ font-size: 42px; font-weight: 700; letter-spacing: 8px; color: #00D4AA; font-family: monospace; }}
    .expires {{ color: #9CA3AF; font-size: 13px; margin-top: 8px; }}
    .footer {{ color: #6B7280; font-size: 12px; text-align: center; padding: 16px 32px 24px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header"><h1>AutoInvest</h1></div>
    <div class="body">
      <p>Hi <strong>{full_name}</strong>,</p>
      <p>Use the verification code below to complete your registration:</p>
      <div class="otp-box">
        <div class="otp">{otp}</div>
        <div class="expires">Expires in 10 minutes</div>
      </div>
      <p>If you did not create an AutoInvest account, please ignore this email.</p>
    </div>
    <div class="footer">© 2026 AutoInvest · This is an automated message, do not reply.</div>
  </div>
</body>
</html>
"""


def _send_smtp_sync(to_email: str, full_name: str, otp: str) -> None:
    """Blocking SMTP send — run in executor."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{otp} is your AutoInvest verification code"
    msg["From"] = f"{settings.from_name} <{settings.from_email or settings.smtp_user}>"
    msg["To"] = to_email

    msg.attach(MIMEText(_otp_html(otp, full_name), "html"))

    # Strip spaces — Gmail App Passwords are displayed with spaces but must be sent without
    smtp_password = (settings.smtp_password or "").replace(" ", "")
    smtp_user     = (settings.smtp_user or "").strip()

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())


async def send_otp_email(to_email: str, full_name: str, otp: str) -> bool:
    """
    Send OTP email asynchronously.
    Returns True if sent successfully, False on error.
    In dev mode (no SMTP configured), logs the OTP and returns False
    to signal the caller to include OTP in the API response.
    """
    if not settings.email_configured:
        logger.info("Dev mode — OTP for {} is: {}", to_email, otp)
        return False   # Caller will include OTP in response

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _send_smtp_sync, to_email, full_name, otp)
        logger.info("OTP email sent to {}", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP email to {}: {}", to_email, exc)
        return False
