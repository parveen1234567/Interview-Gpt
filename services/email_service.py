import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlsplit
from urllib.parse import urlencode

from dotenv import load_dotenv


load_dotenv()


def send_password_reset_email(recipient, raw_token, next_path="/dashboard"):
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", username or "")
    base_url = os.getenv("APP_BASE_URL", "")

    parsed_base_url = urlsplit(base_url)
    local_http_hosts = {"localhost", "127.0.0.1", "::1"}
    if (
        not username
        or not password
        or not sender
        or parsed_base_url.scheme not in {"http", "https"}
        or not parsed_base_url.netloc
        or (
            parsed_base_url.scheme != "https"
            and parsed_base_url.hostname not in local_http_hosts
        )
    ):
        raise RuntimeError(
            "Password reset email is not configured. Set SMTP_USERNAME, "
            "SMTP_PASSWORD, SMTP_FROM, and APP_BASE_URL."
        )

    reset_url = (
        base_url.rstrip("/")
        + "/reset-password?"
        + urlencode({"token": raw_token, "next": next_path})
    )
    message = EmailMessage()
    message["Subject"] = "Reset your Interview GPT password"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "We received a request to reset your password.\n\n"
        f"Use this link within 30 minutes:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)
